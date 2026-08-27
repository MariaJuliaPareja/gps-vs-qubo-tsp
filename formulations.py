"""
formulations.py
Traditional QUBO (one-hot, Lucas 2014) and GPS (positional matrix,
Gonzalez-Bermejo et al. 2022, eqs. 8-13) for the TSP.
"""

import numpy as np


def _default_penalty(dist_matrix: np.ndarray) -> float:
    return float(np.sum(dist_matrix)) * 2.0


def build_traditional_qubo(dist_matrix: np.ndarray, penalty: float = None) -> np.ndarray:
    """Variables x_{i,p} = city i at position p. n^2 variables."""
    n = dist_matrix.shape[0]
    A = penalty if penalty is not None else _default_penalty(dist_matrix)
    Q = np.zeros((n * n, n * n))

    def idx(i, p):
        return i * n + p

    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            for p in range(n):
                Q[idx(i, p), idx(j, (p + 1) % n)] += dist_matrix[i, j]

    for i in range(n):
        for p in range(n):
            Q[idx(i, p), idx(i, p)] += -A
            for p2 in range(n):
                if p2 != p:
                    Q[idx(i, p), idx(i, p2)] += A

    for p in range(n):
        for i in range(n):
            Q[idx(i, p), idx(i, p)] += -A
            for j in range(n):
                if j != i:
                    Q[idx(i, p), idx(j, p)] += A

    return Q


def build_gps_qubo(dist_matrix: np.ndarray, penalty: float = None, lam: float = None):
    """
    Variables x_{i,j,r}, i,j in {0,...,N+1} (N = n-1), r in {0,1,2}.
    The pair (0, N+1) is excluded (depot-to-depot edge, zero cost, not
    forbidden by the paper's constraints -- see README, "Findings" section).
    Returns (Q, var_index, N).
    """
    n = dist_matrix.shape[0]
    if n < 2:
        raise ValueError("At least 2 cities are required.")

    N = n - 1
    num_aug = N + 2
    A = penalty if penalty is not None else _default_penalty(dist_matrix)
    lam_val = lam if lam is not None else A

    def real_city(aug_idx):
        return 0 if aug_idx in (0, N + 1) else aug_idx

    def d(i, j):
        return dist_matrix[real_city(i), real_city(j)]

    pairs = [(i, j) for i in range(num_aug) for j in range(num_aug)
             if i != j and {i, j} != {0, N + 1}]
    var_index = {(i, j, r): k for k, (i, j, r) in
                 enumerate((i, j, r) for (i, j) in pairs for r in range(3))}
    Q = np.zeros((len(var_index), len(var_index)))

    def lin(v, c):
        Q[v, v] += c

    def quad(v1, v2, c):
        if v1 == v2:
            Q[v1, v1] += c
        else:
            Q[v1, v2] += c / 2
            Q[v2, v1] += c / 2

    def eq_one(terms, w):
        for v in terms:
            Q[v, v] += -w
        for a in range(len(terms)):
            for b in range(a + 1, len(terms)):
                quad(terms[a], terms[b], 2 * w)

    for (i, j) in pairs:
        lin(var_index[(i, j, 1)], d(i, j))

    for (i, j) in pairs:
        eq_one([var_index[(i, j, r)] for r in range(3)], A)

    for i in range(0, N + 1):
        terms = [var_index[(i, j, 1)] for j in range(num_aug)
                 if j != i and {i, j} != {0, N + 1}]
        eq_one(terms, A)

    for j in range(1, N + 2):
        terms = [var_index[(i, j, 1)] for i in range(0, N + 1)
                 if i != j and {i, j} != {0, N + 1}]
        eq_one(terms, A)

    for i in range(num_aug):
        for j in range(num_aug):
            if i < j and {i, j} != {0, N + 1}:
                eq_one([var_index[(i, j, 2)], var_index[(j, i, 2)]], A)

    for i in range(1, N + 1):
        for j in range(1, N + 1):
            for k in range(1, N + 1):
                if i == j or j == k or i == k:
                    continue
                v_ji, v_kj, v_ki = var_index[(j, i, 2)], var_index[(k, j, 2)], var_index[(k, i, 2)]
                quad(v_ji, v_kj, lam_val)
                quad(v_ji, v_ki, -lam_val)
                quad(v_kj, v_ki, -lam_val)
                lin(v_ki, lam_val)

    return Q, var_index, N


def decode_gps_solution(bits, var_index: dict, N: int):
    """Decode a GPS bitstring into a real tour [0, ...]. None if infeasible."""
    edges = [(i, j) for (i, j, r), v in var_index.items() if r == 1 and bits[v] == 1]
    if len(edges) != N + 1:
        return None
    successor = dict(edges)
    if len(successor) != N + 1:
        return None

    path, visited, current = [0], {0}, 0
    for _ in range(N + 1):
        if current not in successor:
            return None
        nxt = successor[current]
        path.append(nxt)
        if nxt == N + 1:
            break
        if nxt in visited:
            return None
        visited.add(nxt)
        current = nxt

    if path[-1] != N + 1:
        return None
    intermediate = path[1:-1]
    if len(intermediate) != N or set(intermediate) != set(range(1, N + 1)):
        return None
    return [0] + intermediate


def qubo_variable_count(n: int) -> dict:
    N = n - 1
    gps_vars = 3 * (N + 2) * (N + 1)
    trad_vars = n * n
    return {"n": n, "traditional": trad_vars, "gps": gps_vars,
            "gps_size_factor": round(gps_vars / trad_vars, 2)}


if __name__ == "__main__":
    for n in [3, 4, 5, 6]:
        print(qubo_variable_count(n))