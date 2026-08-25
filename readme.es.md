# Eficiencia de la formulación matricial posicional frente a la optimización binaria cuadrática sin restricciones en computación cuántica híbrida

*[English version](README.en.md)*

Tesis de pregrado — Ingeniería de Sistemas, UCSM. Compara dos formulaciones QUBO
para el TSP (GPS/Matricial Posicional vs. QUBO Tradicional) mediante QAOA
sobre simulación cuántica.

## Estructura

```
formulations.py            # Construcción de ambas matrices QUBO
synthetic_instances.py      # Generador de instancias (n=3 a 6, semilla fija)
validate_formulations.py    # Validación contra fuerza bruta
qaoa_experiment.py           # Ejecución de QAOA (CPU por defecto)
statistical_analysis.py      # Shapiro-Wilk, Wilcoxon, correlación, LOWESS
```

## Instalación

```bash
pip install numpy pandas scipy statsmodels matplotlib
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

Agregar `qiskit-aer-gpu` solo si se corre con `--device GPU` (requiere CUDA).

## Uso

```bash
# 1. Validar las formulaciones (sin dependencias de Qiskit, corre en cualquier máquina)
python validate_formulations.py

# 2. Ejecutar el experimento (instancias pequeñas, CPU normal)
python qaoa_experiment.py --instances synth03,synth04,synth05 --device CPU --replicas 5

# 3. Analizar resultados
python statistical_analysis.py --input results/consolidated.csv
```

## Hallazgos metodológicos (léase antes de interpretar resultados)

### 1. GPS usa ~3× más qubits que QUBO Tradicional, no menos

La formulación GPS (González-Bermejo et al., 2022, ecs. 8-13), implementada
literal, requiere 3·(N+2)·(N+1) ≈ 3N² variables. QUBO Tradicional (Lucas,
2014, one-hot) requiere N². GPS pierde por un factor constante de ~3 frente
al one-hot simple — su ventaja real en el paper original es frente a la
formulación nativa (N³) y MTZ (N²log₂N), nunca frente al one-hot. Esto afecta
directamente la dirección esperada de la hipótesis de la tesis.

### 2. "QUBO Tradicional" no es DFJ literal

La tesis cita a Montañez-Barrera et al. (2024) como referencia de "QUBO
Tradicional", quienes usan la formulación DFJ (Dantzig-Fulkerson-Johnson).
DFJ requiere eliminación de subtours con un número exponencial de
restricciones — los propios autores solo probaron TSP hasta 7 ciudades (42
qubits) por esta razón. Se adopta en su lugar el one-hot N² (Lucas, 2014)
como línea base computacionalmente viable, documentado como decisión de
alcance.

### 3. Por qué no se usa TSPLIB

La simulación exacta (statevector) de un circuito cuántico requiere memoria
= 2^(número de qubits). Incluso la instancia más pequeña de TSPLIB (burma14,
14 nodos) requiere 196 qubits bajo QUBO Tradicional — muy por encima del
límite práctico de simulación clásica (~50 qubits, incluso con
supercomputadoras; ver Boixo et al. 2018, Doi & Horii 2020). Se reemplaza
TSPLIB por instancias sintéticas pequeñas (n=3 a 6), generadas con semilla
fija para reproducibilidad.

### 4. La comparación pareada (GPS vs. Tradicional) solo es posible en n=3

| n | Qubits Tradicional | Qubits GPS | Memoria GPS (statevector) |
|---|---|---|---|
| 3 | 9 | 36 | ~1 TB |
| 4 | 16 | 60 | ~17 mil millones de GB (inviable) |
| 5 | 25 | 90 | inviable |
| 6 | 36 | 126 | inviable |

GPS solo es simulable en n=3 (con infraestructura de alta memoria). Para
n=4-6, únicamente Tradicional es simulable. En consecuencia:

- La prueba de Wilcoxon (comparación pareada) usa **réplicas de la instancia
  n=3** como unidad de pareo, no distintos tamaños de instancia.
- El análisis de escalabilidad (regresión LOWESS) solo se aplica a la
  formulación Tradicional (n=3 a 5); no es posible contrastar la tendencia de
  escalabilidad de GPS frente a Tradicional a tamaños mayores a n=3 con los
  recursos de simulación disponibles.

### 5. Infraestructura mixta

- **CPU local / servidor institucional**: construcción de QUBO, Tradicional
  en n=3-5, y todo el análisis estadístico.
- **Instancia de alta memoria en la nube** (~1-2 TB RAM, ej. AWS
  `x2idn.32xlarge`): únicamente para GPS en n=3. No requiere GPU — el cuello
  de botella es memoria de sistema, no cómputo.

## Estado de verificación

- `formulations.py`: ambas formulaciones validadas contra fuerza bruta /
  enumeración exhaustiva (`validate_formulations.py`), coinciden exactas con
  el óptimo real.
- `statistical_analysis.py`: probado end-to-end con datos simulados.
- `qaoa_experiment.py`: construido pero no probado en este entorno (requiere
  Qiskit). Se recomienda correr primero con `--instances synth03 --replicas 1`
  antes del experimento completo, por posibles cambios de API entre
  versiones de `qiskit_algorithms`.

## Referencias clave

- González-Bermejo, S., Alonso-Linaje, G., & Atchade-Adelomou, P. (2022). GPS: A new TSP formulation. arXiv:2110.12158
- Lucas, A. (2014). Ising formulations of many NP problems. *Frontiers in Physics*.
- Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization. *Quantum Science and Technology*, 9(2), 025022.
- Boixo, S. et al. (2018). Characterizing quantum supremacy in near-term devices. *Nature Physics*.