# Paquete de datos — tesis GPS vs QUBO tradicional (TSP con QAOA)

Comparación de dos formulaciones QUBO del TSP, GPS y QUBO tradicional (one-hot), resueltas con QAOA en Qiskit sobre instancias sintéticas.

Este paquete incluye solo las corridas de producción de synth03. Los resultados que había de synth04 y synth05 no forman parte de este paquete.

## Carpetas

- `instancias/`: coordenadas y matrices de distancia de synth03, synth04, synth05 y synth06. En el repositorio no había archivos de instancias guardados; estos CSV se obtuvieron ejecutando `generador/synthetic_instances.py` con la semilla definida ahí.
- `generador/`: script que genera las instancias y la semilla.
- `resultados/gps/`: corridas de producción de GPS en synth03.
- `resultados/qubo_tradicional/`: corridas de producción de QUBO tradicional en synth03.
- `scripts/`: scripts de experimento y `formulations.py`, que esos scripts importan para construir las matrices QUBO.

## Cómo regenerar las instancias

La semilla está en `generador/synthetic_instances.py`: `BASE_SEED = 42`.

Las instancias definidas son synth03 (3 ciudades), synth04 (4), synth05 (5) y synth06 (6). `load_instance` llama a `generate_instance(n)` con `BASE_SEED` para todas. Las coordenadas salen de `numpy.random.default_rng(42)` en el cuadrado `[0, 100)` y la distancia es la euclidiana.

Desde la carpeta `generador/`:

```bash
python synthetic_instances.py
```

Eso imprime el nombre, el número de ciudades y la suma de la matriz de distancias. Para volver a escribir los CSV de `instancias/` hay que llamar a `generate_instance(n, seed=42)` para cada tamaño.

## Formato de los resultados

Cada JSON es una réplica. Campos:

| Campo | Significado |
|---|---|
| `instance` | Nombre de la instancia (`synth03`) |
| `n_cities` | Número de ciudades |
| `formulation` | `gps` o `traditional` |
| `replica` | Índice de la réplica, desde 0 |
| `n_qubits` | Variables del QUBO |
| `circuit_depth` | Profundidad del ansatz tras `decompose()` |
| `gate_count` | Número de compuertas tras `decompose()` |
| `execution_time_sec` | Segundos de la corrida |
| `objective_value` | Valor de la función objetivo devuelto por QAOA |
| `optimal_bitstring` | Cadena de bits de la solución. Puede faltar si la réplica solo quedó en el CSV |

`resultados/gps/aws_consolidated.csv` tiene las columnas:

`instance`, `n_cities`, `formulation`, `replica`, `n_qubits`, `circuit_depth`, `gate_count`, `execution_time_sec`, `objective_value`

Ese CSV no incluye el bitstring. Cubre las réplicas GPS 0 a 18. No hay un CSV equivalente para QUBO tradicional en esta corrida: esas 20 réplicas están solo en JSON.

### Qué es cada archivo GPS

- `synth03_gps_0.json` y `synth03_gps_3.json` … `synth03_gps_18.json`: 17 réplicas del lote de 19 (`gps_batch_v2.log`). En el log, `eval N/~30`.
- Las réplicas 1 y 2 de ese lote no tienen JSON. Sus tiempo y objetivo están en las filas `replica` 1 y 2 de `aws_consolidated.csv`. No hay bitstring de esas dos.
- `backup_rep1/synth03_gps_0.json`: réplica 1/20 del lote `gps_batch_final.log` (también `eval N/~30`). El campo `replica` dentro del JSON vale 0. En el análisis se usó como réplica 19, porque el índice 0 ya lo ocupaba el otro lote. El log de ese lote de 20 se interrumpe en la réplica 2; de él solo entra esta réplica.

## Parámetros de las corridas

Los JSON no guardan el optimizador, `maxiter` ni el número de capas (`--reps`). La línea de comando no quedó en los logs.

Lo que sí consta:

- QUBO tradicional, synth03: 20 réplicas, índices 0–19, en `resultados/qubo_tradicional/`. El log `results_aws_final/run_completo.log` encabeza el lote como 20 réplicas y los tiempos coinciden en orden con estos JSON. Ese log no imprime `maxiter`.
- GPS, lote de 19: `maxiter` 30, visible como `eval N/~30` en `gps_batch_v2.log`.
- GPS, réplica guardada en `backup_rep1/`: `maxiter` 30, visible como `eval N/~30` en `gps_batch_final.log`. El lote se lanzó con 20 réplicas y solo terminó la primera.
- En todos los JSON de este paquete, `circuit_depth` es 6. GPS tiene `n_qubits` 30 y `gate_count` 65. QUBO tradicional tiene `n_qubits` 9 y `gate_count` 23.
- Los scripts declaran el optimizador COBYLA. Los defaults escritos en `run_aws_full.py` y `run_gps_n3_cloud.py` son `--reps 2` y `--maxiter 30`. `qaoa_experiment.py` declara por defecto `--reps 2`, `--replicas 5`, `--maxiter 50` y `--device CPU`. Esos defaults no sustituyen al valor usado cuando el log no lo imprime.

## Infraestructura

AWS EC2 t2.2xlarge, solo CPU.

`run_aws_full.py` no tiene opción de GPU. El tipo de instancia no está escrito en los JSON ni en los logs.

## Exclusiones

- synth04: MOTIVO: [completar]
- synth05: MOTIVO: [completar]
- synth06: MOTIVO: [completar]
