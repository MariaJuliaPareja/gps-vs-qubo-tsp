"""Recursos del circuito QAOA (n = 3..6) sin simular el statevector."""
import numpy as np
import pandas as pd
from qiskit import transpile
from qiskit.circuit.library import QAOAAnsatz
from qiskit.quantum_info import SparsePauliOp

from formulations import build_traditional_qubo, build_gps_qubo
from statistical_analysis_v2 import get_dist_matrix

REPS = 2
BASIS = ["rz", "sx", "x", "cx"]
SEED = 42


def dist_for(n):
    """Usa la instancia sintética real si existe; si no (p. ej. synth06),
    una matriz euclidiana aleatoria: la ESTRUCTURA de Q no depende de los valores."""
    try:
        return get_dist_matrix(f"synth0{n}", n), f"synth0{n}"
    except Exception:
        rng = np.random.default_rng(SEED)
        pts = rng.random((n, 2))
        d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=-1)
        return d, "aleatoria (solo estructura)"


def get_Q(builder, dist):
    res = builder(dist)
    return np.asarray(res[0] if isinstance(res, tuple) else res, dtype=float)


def qubo_to_ising(Q, tol=1e-12):
    """E(x) = x^T Q x con x = (1 - z)/2  ->  sum h_i Z_i + sum J_ij Z_i Z_j (+ constante)."""
    Q = (Q + Q.T) / 2
    n = Q.shape[0]
    terms = []
    for i in range(n):
        h = -0.5 * Q[i, i] - 0.5 * (Q[i].sum() - Q[i, i])
        if abs(h) > tol:
            label = ["I"] * n
            label[n - 1 - i] = "Z"
            terms.append(("".join(label), h))
    for i in range(n):
        for j in range(i + 1, n):
            if abs(Q[i, j]) > tol:
                label = ["I"] * n
                label[n - 1 - i] = "Z"
                label[n - 1 - j] = "Z"
                terms.append(("".join(label), 0.5 * Q[i, j]))
    return SparsePauliOp.from_list(terms)


rows = []
for n in range(3, 7):
    dist, origen = dist_for(n)
    for form, builder in [("traditional", build_traditional_qubo), ("gps", build_gps_qubo)]:
        Q = get_Q(builder, dist)
        Qs = (Q + Q.T) / 2
        activas = np.where(np.abs(Qs).sum(axis=1) > 1e-12)[0]
        Qr = Qs[np.ix_(activas, activas)]
        nnz_cuad = int(np.count_nonzero(np.triu(np.abs(Qr) > 1e-12, k=1)))
        nnz_lin = int(np.count_nonzero(np.abs(np.diag(Qr)) > 1e-12))  # x_i^2 = x_i

        H = qubo_to_ising(Qr)
        ansatz = QAOAAnsatz(H, reps=REPS)
        ansatz.measure_all()
        tc = transpile(ansatz, basis_gates=BASIS, optimization_level=1, seed_transpiler=SEED)
        ops = tc.count_ops()

        rows.append({
            "n": n,
            "formulacion": form,
            "origen_instancia": origen,
            "variables_Q": Q.shape[0],
            "qubits_activos": len(activas),
            "variables_descartadas": Q.shape[0] - len(activas),
            "terminos_lineales": nnz_lin,
            "terminos_cuadraticos": nnz_cuad,
            "profundidad_bloques": ansatz.depth(),
            "profundidad_transpilada": tc.depth(),
            "compuertas_total": sum(v for k, v in ops.items() if k not in ("measure", "barrier")),
            "cx": ops.get("cx", 0),
            "memoria_statevector_GB": (2 ** len(activas)) * 16 / 1e9,
        })
        print(f"n={n} {form:11s} vars={Q.shape[0]:4d} activas={len(activas):4d} "
              f"lin={nnz_lin:4d} cuad={nnz_cuad:6d} depth={tc.depth():6d} cx={ops.get('cx', 0):7d}")

df = pd.DataFrame(rows)
df.to_csv("recursos_circuito.csv", index=False)
print("\nGuardado: recursos_circuito.csv")
print(df.to_string(index=False))