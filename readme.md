# Efficiency of the Positional Matrix Formulation Versus Unconstrained Quadratic Binary Optimization in Hybrid Quantum Computing

*[Versión en español](README.es.md)*

Undergraduate thesis — Systems Engineering, UCSM. Compares two QUBO
formulations for the TSP (GPS/Positional Matrix vs. Traditional QUBO) via
QAOA on quantum simulation.

## Structure

```
formulations.py            # Construction of both QUBO matrices
synthetic_instances.py      # Instance generator (n=3 to 6, fixed seed)
validate_formulations.py    # Validation against brute force
qaoa_experiment.py           # QAOA execution (CPU by default)
statistical_analysis.py      # Shapiro-Wilk, Wilcoxon, correlation, LOWESS
```

## Installation

```bash
pip install numpy pandas scipy statsmodels matplotlib
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

Add `qiskit-aer-gpu` only if running with `--device GPU` (requires CUDA).

## Usage

```bash
# 1. Validate the formulations (no Qiskit dependency, runs on any machine)
python validate_formulations.py

# 2. Run the experiment (small instances, regular CPU)
python qaoa_experiment.py --instances synth03,synth04,synth05 --device CPU --replicas 5

# 3. Analyze results
python statistical_analysis.py --input results/consolidated.csv
```

## Methodological Findings (read before interpreting results)

### 1. GPS uses ~3× more qubits than Traditional QUBO, not fewer

The GPS formulation (González-Bermejo et al., 2022, eqs. 8-13), implemented
literally, requires 3·(N+2)·(N+1) ≈ 3N² variables. Traditional QUBO (Lucas,
2014, one-hot) requires N². GPS loses by a constant factor of ~3 against the
plain one-hot — its real advantage in the original paper is against the
native formulation (N³) and MTZ (N²log₂N), never against one-hot. This
directly affects the expected direction of the thesis hypothesis.

### 2. "Traditional QUBO" is not literal DFJ

The thesis cites Montañez-Barrera et al. (2024) as the reference for
"Traditional QUBO," who use the DFJ (Dantzig-Fulkerson-Johnson)
formulation. DFJ requires subtour elimination with an exponential number of
constraints — the authors themselves only tested TSP up to 7 cities (42
qubits) for this exact reason. The N² one-hot (Lucas, 2014) is adopted
instead as a computationally viable baseline, documented as a scope
decision.

### 3. Why TSPLIB is not used

Exact (statevector) simulation of a quantum circuit requires memory =
2^(number of qubits). Even TSPLIB's smallest instance (burma14, 14 nodes)
requires 196 qubits under Traditional QUBO — far beyond the practical limit
of classical simulation (~50 qubits, even with supercomputers; see Boixo et
al. 2018, Doi & Horii 2020). TSPLIB is replaced with small synthetic
instances (n=3 to 6), generated with a fixed seed for reproducibility.

### 4. Paired comparison (GPS vs. Traditional) is only possible at n=3

| n | Traditional qubits | GPS qubits | GPS memory (statevector) |
|---|---|---|---|
| 3 | 9 | 36 | ~1 TB |
| 4 | 16 | 60 | ~17 billion GB (infeasible) |
| 5 | 25 | 90 | infeasible |
| 6 | 36 | 126 | infeasible |

GPS is only simulable at n=3 (with high-memory infrastructure). For n=4-6,
only Traditional is simulable. As a result:

- The Wilcoxon test (paired comparison) uses **replicas of the n=3
  instance** as the pairing unit, not different instance sizes.
- The scalability analysis (LOWESS regression) only applies to the
  Traditional formulation (n=3 to 5); it is not possible to contrast GPS's
  scalability trend against Traditional at sizes larger than n=3 with the
  available simulation resources.

### 5. Mixed infrastructure

- **Local CPU / institutional server**: QUBO construction, Traditional at
  n=3-5, and all statistical analysis.
- **High-memory cloud instance** (~1-2 TB RAM, e.g. AWS `x2idn.32xlarge`):
  only for GPS at n=3. No GPU required — the bottleneck is system memory,
  not compute.

## Verification Status

- `formulations.py`: both formulations validated against brute force /
  exhaustive enumeration (`validate_formulations.py`), match the real
  optimum exactly.
- `statistical_analysis.py`: tested end-to-end with simulated data.
- `qaoa_experiment.py`: built but not tested in this environment (requires
  Qiskit). Running first with `--instances synth03 --replicas 1` before the
  full experiment is recommended, due to possible API changes across
  `qiskit_algorithms` versions.

## Key References

- González-Bermejo, S., Alonso-Linaje, G., & Atchade-Adelomou, P. (2022). GPS: A new TSP formulation. arXiv:2110.12158
- Lucas, A. (2014). Ising formulations of many NP problems. *Frontiers in Physics*.
- Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization. *Quantum Science and Technology*, 9(2), 025022.
- Boixo, S. et al. (2018). Characterizing quantum supremacy in near-term devices. *Nature Physics*.