"""
validate_formulations.py
Validates Traditional and GPS against brute force / exhaustive enumeration.
"""

import numpy as np
import itertools
from formulations import build_traditional_qubo, build_gps_qubo, decode_gps_solution


def brute_force_tsp(dist_matrix):
    n = dist_matrix.shape[0]
    best_cost, best_tour = float("inf"), None
    for perm in itertools.permutations(range(n)):
        cost = sum(dist_matrix[perm[k], perm[(k + 1) % n]] for k in range(n))
        if cost < best_cost:
            best_cost, best_tour = cost, perm
    return best_tour, best_cost


def brute_force_qubo(Q):
    num_vars = Q.shape[0]
    best_energy, best_bits = float("inf"), None
    for bits in itertools.product([0, 1], repeat=num_vars):
        x = np.array(bits)
        energy = x @ Q @ x
        if energy < best_energy:
            best_energy, best_bits = energy, bits
    return best_bits, best_energy


def decode_traditional(bits, n):
    x = np.array(bits).reshape(n, n)
    tour = []
    for p in range(n):
        cities = np.where(x[:, p] == 1)[0]
        if len(cities) != 1:
            return None
        tour.append(int(cities[0]))
    return tour if len(set(tour)) == n else None


def random_instance(n, seed):
    rng = np.random.default_rng(seed)
    coords = rng.random((n, 2)) * 100
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = np.linalg.norm(coords[i] - coords[j])
    return dist


if __name__ == "__main__":
    print("--- Traditional (n=4, brute force) ---")
    dist = random_instance(4, seed=42)
    tour_real, cost_real = brute_force_tsp(dist)
    Q = build_traditional_qubo(dist)
    bits, energy = brute_force_qubo(Q)
    tour = decode_traditional(bits, 4)
    cost = sum(dist[tour[k], tour[(k + 1) % 4]] for k in range(4)) if tour else None
    print(f"real={cost_real:.4f} obtained={cost} match={np.isclose(cost, cost_real) if cost else False}")

    print("\n--- GPS n=2 (brute force) ---")
    dist2 = np.array([[0.0, 42.3], [42.3, 0.0]])
    Q2, vi2, N2 = build_gps_qubo(dist2)
    bits2, e2 = brute_force_qubo(Q2)
    tour2 = decode_gps_solution(bits2, vi2, N2)
    cost2 = sum(dist2[tour2[k], tour2[(k + 1) % 2]] for k in range(2)) if tour2 else None
    print(f"tour={tour2} cost={cost2} (real=84.6)")

    print("\n--- GPS n=3 (enumeration over r-assignments, 3^12) ---")
    dist3 = random_instance(3, seed=42)
    tour_real3, cost_real3 = brute_force_tsp(dist3)
    Q3, vi3, N3 = build_gps_qubo(dist3)
    num_aug = N3 + 2
    ordered_pairs = [(i, j) for i in range(num_aug) for j in range(num_aug)
                     if i != j and {i, j} != {0, N3 + 1}]
    best_energy, best_bits = float("inf"), None
    for r_choice in itertools.product(range(3), repeat=len(ordered_pairs)):
        bits = [0] * Q3.shape[0]
        for (i, j), r in zip(ordered_pairs, r_choice):
            bits[vi3[(i, j, r)]] = 1
        x = np.array(bits)
        e = x @ Q3 @ x
        if e < best_energy:
            best_energy, best_bits = e, bits
    tour3 = decode_gps_solution(best_bits, vi3, N3)
    cost3 = sum(dist3[tour3[k], tour3[(k + 1) % 3]] for k in range(3)) if tour3 else None
    print(f"real={cost_real3:.4f} obtained={cost3} match={np.isclose(cost3, cost_real3) if cost3 else False}")

    print("\n--- Anti-cycle constraint (eq. 13), N=3 ---")
    dist4 = random_instance(4, seed=5)
    Q4, vi4, N4 = build_gps_qubo(dist4)

    def energy_of(active):
        x = np.zeros(Q4.shape[0])
        for v in active:
            x[vi4[v]] = 1
        return x @ Q4 @ x

    edges_r1 = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (3, 4, 1)]
    order = [0, 1, 2, 3, 4]
    pos = {node: i for i, node in enumerate(order)}
    all_pairs = [(i, j) for i in range(5) for j in range(5) if i != j and {i, j} != {0, 4}]
    active_ok = list(edges_r1)
    for (i, j) in all_pairs:
        if (i, j, 1) in edges_r1:
            continue
        active_ok.append((i, j, 0) if pos[i] < pos[j] else (i, j, 2))
    e_ok = energy_of(active_ok)

    active_cyclic = [t for t in active_ok if t[:2] not in [(1, 3), (3, 1)]]
    active_cyclic.append((3, 1, 0))
    e_cyclic = energy_of(active_cyclic)
    print(f"consistent order={e_ok:.4f} cyclic order={e_cyclic:.4f} "
          f"penalizes_correctly={e_cyclic > e_ok}")