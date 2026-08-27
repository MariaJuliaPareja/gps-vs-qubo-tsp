"""
qaoa_experiment.py
Runs QAOA (Qiskit) on the Traditional and GPS formulations for the small
synthetic instances (n=3 to 6). Defaults to CPU -- see README for which
instance size requires a high-memory cloud machine (GPS n=3, ~1TB).

Requires: pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
(add qiskit-aer-gpu only when running with --device GPU)

Usage:
    python qaoa_experiment.py --instances synth03,synth04,synth05 --device CPU --replicas 5
"""

import argparse
import json
import os
import time
import csv
import numpy as np

from synthetic_instances import load_instance, SAMPLE
from formulations import build_traditional_qubo, build_gps_qubo

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results")


def run_qaoa_on_qubo(Q: np.ndarray, reps: int, device: str, maxiter: int = 50):
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer import AerSimulator
    from qiskit import transpile

    class TranspilingSampler(AerSampler):
        """QAOAAnsatz produces a non-basis 'QAOA' instruction that Aer's
        simulator cannot run directly; this transpiles each circuit to basis
        gates before simulation (see README, Qiskit 2.x compatibility note).
        Caches the transpiled circuit by identity, since COBYLA calls run()
        repeatedly on the same circuit structure with only parameters changing."""
        _cache = {}

        def run(self, pubs, *, shots=None):
            backend = AerSimulator(device=device)
            new_pubs = []
            for pub in pubs:
                if isinstance(pub, tuple):
                    circ, rest = pub[0], pub[1:]
                else:
                    circ, rest = pub, ()
                key = id(circ)
                if key not in self._cache:
                    self._cache[key] = transpile(circ, backend)
                tcirc = self._cache[key]
                new_pubs.append((tcirc,) + rest if rest else tcirc)
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
        raise RuntimeError(
            f"MinimumEigenOptimizer failed to interpret samples after 3 attempts "
            f"(known edge case at larger qubit counts): {last_error}"
        )
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
    parser.add_argument("--instances", type=str, default=",".join(SAMPLE))
    parser.add_argument("--formulations", type=str, default="traditional,gps")
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--replicas", type=int, default=5)
    parser.add_argument("--maxiter", type=int, default=50)
    parser.add_argument("--device", type=str, default="CPU", choices=["GPU", "CPU"])
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    instances = args.instances.split(",")
    formulations_to_run = args.formulations.split(",")
    rows = []

    for instance_name in instances:
        dist_matrix, _ = load_instance(instance_name)
        n = dist_matrix.shape[0]
        available = {}
        if "traditional" in formulations_to_run:
            available["traditional"] = build_traditional_qubo(dist_matrix)
        if "gps" in formulations_to_run:
            available["gps"] = build_gps_qubo(dist_matrix)[0]

        for form_name, Q in available.items():
            print(f"{instance_name} | {form_name} | {Q.shape[0]} qubits")
            for rep in range(args.replicas):
                try:
                    metrics = run_qaoa_on_qubo(Q, reps=args.reps, device=args.device, maxiter=args.maxiter)
                except Exception as e:
                    print(f"  [ERROR replica {rep}] {e}")
                    continue
                metrics.update({"instance": instance_name, "n_cities": n,
                                 "formulation": form_name, "replica": rep})
                with open(os.path.join(RESULTS_DIR, f"{instance_name}_{form_name}_{rep}.json"), "w") as f:
                    json.dump(metrics, f, indent=2)
                rows.append(metrics)

    if rows:
        csv_path = os.path.join(RESULTS_DIR, "consolidated.csv")
        fields = ["instance", "n_cities", "formulation", "replica", "n_qubits",
                  "circuit_depth", "gate_count", "execution_time_sec", "objective_value"]
        with open(csv_path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"\nConsolidated: {csv_path}")


if __name__ == "__main__":
    main()