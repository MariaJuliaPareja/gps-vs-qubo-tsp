"""Corrida QAOA en AWS: synth03 pareado (Tradicional y GPS) y escalabilidad Tradicional."""
# synth03: ambas formulaciones, mismo hardware (comparación pareada, Wilcoxon).
# synth04–06: solo Tradicional (LOWESS); GPS no es simulable para n>3 (synth06, 36 qubits, ~1 TB).

import argparse
import json
import os
import time
import csv
import sys

sys.path.insert(0, os.path.dirname(__file__))
from formulations import build_traditional_qubo, build_gps_qubo
from synthetic_instances import load_instance

RESULTS_DIR = os.path.join(os.path.dirname(__file__), "results_aws")


def run_qaoa(Q, reps, maxiter, label=""):
    import numpy as np
    from qiskit_optimization import QuadraticProgram
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
    from qiskit_algorithms import QAOA
    from qiskit_algorithms.optimizers import COBYLA
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit.primitives.containers import SamplerPub

    class DecomposingSampler(AerSampler):
        """QAOAAnsatz produces a non-basis 'QAOA' instruction that Aer's
        simulator cannot run directly. The original fix (transpile() against
        an AerSimulator backend) turned out to impose an artificial qubit cap
        (27-28 qubits) via the backend's default coupling_map -- a constraint
        meant for real hardware topology, irrelevant to a statevector
        simulator. Using circuit.decompose() directly avoids the backend/
        coupling_map path entirely and has no such limit."""
        _cache = {}

        def run(self, pubs, *, shots=None):
            new_pubs = []
            for pub in pubs:
                coerced = SamplerPub.coerce(pub)
                key = id(coerced.circuit)
                if key not in self._cache:
                    self._cache[key] = coerced.circuit.decompose(reps=5)
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

    # COBYLA calls the callback on every evaluation, so eval_count can exceed
    # maxiter. best_seen (minimum energy) is the value reported as the result.
    t_cb_start = time.time()
    best_seen = {"value": None, "params": None}

    def progress_callback(eval_count, params, value, meta):
        elapsed = time.time() - t_cb_start
        pct = min(100, round(100 * eval_count / max(maxiter, 1)))
        print(f"    [{label}] eval {eval_count}/~{maxiter} (~{pct}%) | "
              f"energy={value:.2f} | elapsed={elapsed:.1f}s", flush=True)
        if best_seen["value"] is None or value < best_seen["value"]:
            best_seen["value"] = value
            best_seen["params"] = params

    sampler = DecomposingSampler()
    qaoa = QAOA(sampler=sampler, optimizer=COBYLA(maxiter=maxiter), reps=reps,
                callback=progress_callback)
    meo = MinimumEigenOptimizer(qaoa)

    t0 = time.perf_counter()
    bitstring = None
    try:
        result = meo.solve(qp)
        bitstring = [int(b) for b in result.x]
        if result.fval < best_seen["value"]:
            best_seen["value"] = result.fval
    except Exception as e:
        print(f"    [{label}] note: final bitstring extraction failed "
              f"({type(e).__name__}) -- attempting manual resampling at "
              f"best known parameters instead.", flush=True)
        # MinimumEigenOptimizer's decode can fail; resample at best_seen["params"]
        # and keep the bitstring with the lowest x^T Q x.
        # The ansatz has no measurements until measure_all(), which creates
        # the classical register "meas" (pub_result.data.meas).
        try:
            shots = 4096
            measured_ansatz = qaoa.ansatz.measure_all(inplace=False)
            job = sampler.run([(measured_ansatz, best_seen["params"])], shots=shots)
            pub_result = job.result()[0]
            counts = pub_result.data.meas.get_counts()
            best_energy_x, best_bits = None, None
            for bitstr, _count in counts.items():
                x = np.array([int(b) for b in bitstr[::-1]])  # qiskit: bit 0 = rightmost
                if len(x) != n:
                    continue
                energy_x = float(x @ Q @ x)
                if best_energy_x is None or energy_x < best_energy_x:
                    best_energy_x, best_bits = energy_x, x
            if best_bits is not None:
                bitstring = [int(b) for b in best_bits]
                if best_energy_x < best_seen["value"]:
                    best_seen["value"] = best_energy_x
                print(f"    [{label}] recovered bitstring via manual "
                      f"resampling (energy={best_energy_x:.2f})", flush=True)
        except Exception as e2:
            print(f"    [{label}] manual resampling also failed "
                  f"({type(e2).__name__}: {e2}) -- proceeding without "
                  f"bitstring; objective_value/timing still valid.",
                  flush=True)
    exec_time = time.perf_counter() - t0

    ansatz = getattr(qaoa, "ansatz", None)
    circuit_depth = ansatz.decompose().depth() if ansatz is not None else None
    gate_count = sum(ansatz.decompose().count_ops().values()) if ansatz is not None else None

    return {
        "n_qubits": n,
        "circuit_depth": circuit_depth,
        "gate_count": gate_count,
        "execution_time_sec": exec_time,
        "objective_value": float(best_seen["value"]),
        "optimal_bitstring": bitstring,
    }


def run_batch(instance_name, n_cities, form_name, Q, replicas, reps, maxiter, rows):
    print(f"\n{'=' * 55}\n{instance_name} | {form_name} | {Q.shape[0]} qubits | "
          f"{replicas} replicas\n{'=' * 55}", flush=True)
    for rep in range(replicas):
        t_start = time.strftime("%H:%M:%S")
        print(f"[{t_start}] replica {rep + 1}/{replicas}...", flush=True, end=" ")
        try:
            metrics = run_qaoa(Q, reps=reps, maxiter=maxiter, label=f"{instance_name}/{form_name}/rep{rep+1}")
        except Exception as e:
            print(f"FAILED: {e}", flush=True)
            continue
        print(f"OK ({metrics['execution_time_sec']:.1f}s, fval={metrics['objective_value']:.2f})",
              flush=True)
        metrics.update({"instance": instance_name, "n_cities": n_cities,
                         "formulation": form_name, "replica": rep})
        with open(os.path.join(RESULTS_DIR, f"{instance_name}_{form_name}_{rep}.json"), "w") as f:
            json.dump(metrics, f, indent=2)
        rows.append(metrics)
        # Write the consolidated CSV after every successful replica, not just
        # at the end of the whole batch -- so a crash mid-batch (e.g. an
        # out-of-memory kill on a later replica) doesn't lose already-
        # completed replicas that were only sitting in memory.
        _write_csv(rows)


def _write_csv(rows):
    csv_path = os.path.join(RESULTS_DIR, "aws_consolidated.csv")
    fields = ["instance", "n_cities", "formulation", "replica", "n_qubits",
              "circuit_depth", "gate_count", "execution_time_sec", "objective_value"]
    with open(csv_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    return csv_path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicas_paired", type=int, default=20,
                         help="Replicas for synth03 (both formulations) -- the paired Wilcoxon comparison")
    parser.add_argument("--replicas_scale", type=int, default=8,
                         help="Replicas for synth04/05/06 (Traditional only) -- the LOWESS scalability trend")
    parser.add_argument("--include_scale", action="store_true",
                         help="Also run the scalability instances (Traditional only). Skip this flag "
                              "on small/low-memory instances -- synth06 (36 qubits, ~1TB) will fail or "
                              "crash the process if there isn't enough RAM.")
    parser.add_argument("--scale_instances", type=str, default="synth04,synth05,synth06",
                         help="Comma-separated list of instances to run with --include_scale. "
                              "Drop synth06 here if your instance doesn't have ~1TB RAM available.")
    parser.add_argument("--reps", type=int, default=2)
    parser.add_argument("--maxiter", type=int, default=30)
    parser.add_argument("--paired_formulations", type=str, default="traditional,gps",
                         help="Comma-separated: which formulations to run for synth03. "
                              "Use 'gps' alone to re-run only GPS after Traditional already succeeded.")
    args = parser.parse_args()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    rows = []

    dist3, _ = load_instance("synth03")
    formulations_to_run = args.paired_formulations.split(",")
    if "traditional" in formulations_to_run:
        run_batch("synth03", 3, "traditional", build_traditional_qubo(dist3),
                  args.replicas_paired, args.reps, args.maxiter, rows)
    if "gps" in formulations_to_run:
        run_batch("synth03", 3, "gps", build_gps_qubo(dist3)[0],
                  args.replicas_paired, args.reps, args.maxiter, rows)

    # Skipped unless --include_scale; synth06 needs ~1 TB for exact statevector.
    if args.include_scale:
        size_map = {"synth04": 4, "synth05": 5, "synth06": 6}
        for instance_name in args.scale_instances.split(","):
            n = size_map.get(instance_name)
            if n is None:
                print(f"  [skipping unknown instance: {instance_name}]")
                continue
            dist, _ = load_instance(instance_name)
            run_batch(instance_name, n, "traditional", build_traditional_qubo(dist),
                      args.replicas_scale, args.reps, args.maxiter, rows)

    if rows:
        csv_path = _write_csv(rows)
        print(f"\n{'=' * 55}\nConsolidated: {csv_path}\n{'=' * 55}")
        for instance_name in ["synth03", "synth04", "synth05", "synth06"]:
            for form_name in ["traditional", "gps"]:
                n_ok = sum(1 for r in rows if r["instance"] == instance_name and r["formulation"] == form_name)
                if n_ok > 0:
                    print(f"  {instance_name} | {form_name}: {n_ok} successful replicas")
    else:
        print("\nNo successful replicas.")


if __name__ == "__main__":
    main()