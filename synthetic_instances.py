"""
synthetic_instances.py
Small synthetic TSP instances (n=3 to 6), fixed seed. Replaces TSPLIB
(see README, "Why TSPLIB is not used").
"""

import numpy as np

SAMPLE = {
    "synth03": 3,
    "synth04": 4,
    "synth05": 5,
    "synth06": 6,
}

BASE_SEED = 42


def generate_instance(n: int, seed: int = BASE_SEED):
    rng = np.random.default_rng(seed)
    coords = rng.random((n, 2)) * 100
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = np.linalg.norm(coords[i] - coords[j])
    return dist, coords


def load_instance(name: str):
    if name not in SAMPLE:
        raise ValueError(f"Unknown instance: {name}. Available: {list(SAMPLE)}")
    return generate_instance(SAMPLE[name])


if __name__ == "__main__":
    for name, n in SAMPLE.items():
        dist, _ = generate_instance(n)
        print(f"{name}: n={n}, total distance={dist.sum():.2f}")