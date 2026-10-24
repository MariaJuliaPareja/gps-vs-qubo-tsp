"""QAOA de Tradicional y GPS sobre synth03 (n = 3) en la misma máquina."""
# Mismo hardware: execution_time_sec es comparable (Wilcoxon pareado).
# GPS en n = 3 requiere ~1 TB para la simulación statevector exacta.

import argparse
import json
import os
import time
import csv
import sys

sys.path.insert(0, os.path.dirname(__file__))
from formulations import build_traditional_qubo, build_gps_qubo
from synthetic_instances import load_instance

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_n3")


def run_qaoa(Q, reps, maxiter):
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer import AerSimulator
    from qiskit import transpile
    from qiskit.primitives.containers import SamplerPub

    class TranspilingSampler(AerSampler):
        _cache = {}

        def run(self, pubs, *, shots=None):
            backend = AerSimulator(device="CPU")
            new_pubs = []
            for pub in pubs:
                coerced = SamplerPub.coerce(pub)
                key = id(coerced.circuit)
                if key not in self._cache:
                    self._cache[key] = transpile(coerced.circuit, backend)
                tcirc = self._cache[key]
                new_pubs.append(SamplerPub(
                    circuit=tcirc,
                    parameter_values=coerced.parameter_values,
                    shots=coerced.shots,
                ))
            return super().run(new_pubs, shots=shots)

    n = Q.shape[0]
    qp = QuadraticProgram()
    for i in range(n):
        qp.binary_var(name=f"x{i}")

    linear = {f"x{i}": float(Q[i, i]) for i in range(n)}
    quadratic = {(f"x{i}", f"x{j}"): float(Q[i, j] + Q[j, i])
                 for i in range(n) for j in range(i + 1, n) if Q[i, j] + Q[j, i] != 0.0}
    qp.minimize(linear=linear, quadratic=quadratic)

    sampler = TranspilingSampler()
    qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=maxiter), reps=reps)
    meo = MinimumEigenOptimizer(qaoa)

    t0 = time.perf_counter()
    last_error = None
    result = None
    for attempt in range(3):
        try:
            result = meo.solve(qp)
            break
        except IndexError as e:
            last_error = e
            continue
    if result is None:
        raise RuntimeError(f"Failed after 3 attempts: {last_error}")
    exec_time = time.perf_counter() - t0

    ansatz = getattr(qaoa, "ansatz", None)
    circuit_depth = ansatz.decompose().depth() if ansatz is not None else None
    gate_count = sum(ansatz.decompose().count_ops().values()) if ansatz is not None else None

    return {
        "n_qubits": n,
        "circuit_depth": circuit_depth,
        "gate_count": gate_count,
        "execution_time_sec": exec_time,
        "objective_value": float(result.fval),
        "optimal_bitstring": [int(b) for b in result.x],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicas", type=int, default=20)
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--maxiter", type=int, default=30)
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    dist_matrix, _ = load_instance("synth03")

    formulations = {
        "traditional": build_traditional_qubo(dist_matrix),
        "gps": build_gps_qubo(dist_matrix)[0],
    }

    rows = []
    for form_name, Q in formulations.items():
        print(f"\n{'=' * 50}\n{form_name.upper()} -- {Q.shape[0]} qubits\n{'=' * 50}", flush=True)
        for rep in range(args.replicas):
            t_start = time.strftime("%H:%M:%S")
            print(f"[{t_start}] replica {rep + 1}/{args.replicas}...", flush=True, end=" ")
            try:
                metrics = run_qaoa(Q, reps=args.reps, maxiter=args.maxiter)
            except Exception as e:
                print(f"FAILED: {e}", flush=True)
                continue
            print(f"OK ({metrics['execution_time_sec']:.1f}s, fval={metrics['objective_value']:.2f})",
                  flush=True)
            metrics.update({"instance": "synth03", "n_cities": 3,
                             "formulation": form_name, "replica": rep})
            with open(os.path.join(RESULTS_DIR, f"synth03_{form_name}_{rep}.json"), "w") as f:
                json.dump(metrics, f, indent=2)
            rows.append(metrics)

    if rows:
        csv_path = os.path.join(RESULTS_DIR, "n3_consolidated.csv")
        fields = ["instance", "n_cities", "formulation", "replica", "n_qubits",
                  "circuit_depth", "gate_count", "execution_time_sec", "objective_value"]
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\nConsolidated: {csv_path}")
        for form_name in formulations:
            n_ok = sum(1 for r in rows if r["formulation"] == form_name)
            print(f"  {form_name}: {n_ok}/{args.replicas} successful replicas")
    else:
        print("\nNo successful replicas.")


if __name__ == "__main__":
    main()