# 4.1.4 Etapa 4: Ejecución experimental

## (A) Texto del apartado

La cuarta etapa ejecuta QAOA sobre las combinaciones que la etapa anterior dejó dentro de la memoria. La máquina es una instancia EC2 t2.2xlarge de AWS, con 8 vCPU y 32 GiB (≈ 31 GB utilizables), usada solo como CPU. [VERIFICAR: los 8 vCPU, los 32 GiB y la denegación de la cuota de GPU no aparecen en el repositorio.] El script de esta etapa no tiene opción de GPU. Las sesiones largas se mantuvieron con tmux, de modo que una caída de la conexión no interrumpiera el bucle. [VERIFICAR: tmux consta como requisito del proyecto; no hay un registro de la sesión.] El entorno de esa máquina fue Qiskit 2.5.2, Qiskit Aer 0.17.2, qiskit-algorithms 0.4.0, qiskit-optimization 0.7.0, NumPy 2.5.3 y SciPy 1.18.1. [VERIFICAR: esas versiones no están fijadas en el repositorio.]

Cada matriz \(Q\) se traduce a un programa cuadrático: una variable binaria por columna, el término lineal en la diagonal y el término cuadrático \(Q_{ij}+Q_{ji}\) en cada par \(i<j\) distinto de cero. Ese programa se minimiza con `MinimumEigenOptimizer` [CITA: MinimumEigenOptimizer de Qiskit Optimization], cuyo eigensolver es QAOA [CITA: algoritmo QAOA] de \(p=2\) capas. El optimizador clásico es COBYLA [CITA: COBYLA] con un máximo de 30 evaluaciones. La llamada no entrega punto inicial ni semilla. Con el punto inicial omitido, qiskit-algorithms 0.4.0 sortea un punto dentro de los límites del ansatz, o en \([-2\pi,2\pi]\) si el ansatz no declara límites [CITA: punto inicial de QAOA en qiskit-algorithms 0.4.0]. El muestreador tampoco recibe semilla, así que usa un generador aleatorio. [DECISIÓN DE LA AUTORA: \(p=2\), máximo de 30 evaluaciones, y ninguna semilla ni punto inicial fijo, para que cada réplica sea una muestra independiente del algoritmo estocástico.]

El muestreador es `SamplerV2` de Qiskit Aer, envuelto para descomponer el circuito antes de simularlo. El script no fija el número de disparos de la optimización. En Aer 0.17.2, si `shots` llega vacío, `SamplerV2` usa `default_shots = 1024` [CITA: disparos por defecto de SamplerV2 en Qiskit Aer 0.17.2]. Tampoco fija el método del simulador ni un modelo de ruido: el backend se construye sin argumentos. La descomposición es `decompose(reps=5)` y no una transpilación contra un backend de Aer. Esa transpilación aplicaba el mapa de acoplamiento por defecto del backend y se detenía alrededor de 27–28 qubits, un tope de topología de hardware que no corresponde a esta simulación (Código 5).

Durante la optimización, un callback guarda en `best_seen` la menor energía vista y los parámetros que la produjeron. COBYLA puede evaluar la función más veces que el máximo declarado, y el valor que se archiva es esa energía mínima, no necesariamente la de la última evaluación. Si el optimizador devuelve un vector, ese vector es el bitstring guardado. Si la decodificación final falla, el script vuelve a muestrear el ansatz en los parámetros de `best_seen`, con 4096 disparos, y conserva la cadena cuya energía \(x^{\mathsf T}Qx\) es menor. En ese remuestreo el bit 0 es el carácter de la derecha, y la cadena se invierte antes de alinearla con las variables. El cronómetro es `perf_counter` alrededor de la resolución y, cuando ocurre, del remuestreo. Quedan fuera la construcción de \(Q\), la del programa cuadrático, el armado del ansatz y el conteo posterior de profundidad y compuertas.

Las réplicas salen de un bucle del mismo script. Cada una exitosa se escribe en su propio JSON y el CSV consolidado se reescribe en ese momento. Si la llamada entera falla, la réplica se omite y no se reintenta. Los valores por defecto son 20 réplicas para synth03, en tradicional y en GPS, y 8 para el escalamiento tradicional, con \(p=2\) y máximo de 30 evaluaciones (Tabla X). El escalamiento solo se lanza con una opción explícita; su lista por defecto incluye synth06, que la etapa anterior dejó fuera de la simulación. GPS no entra en ese escalamiento: para \(n\ge 4\) supera el corte de memoria. [DECISIÓN DE LA AUTORA: 8 réplicas en \(n=4\) y \(n=5\).] La línea de comando de cada lote no quedó en los registros. Los lotes que sí imprimieron el callback muestran `eval N/~30`, que es el máximo con el que se lanzaron. [VERIFICAR: la línea de comando exacta de cada lote.]

## (B) Tabla

**Tabla X**

*Protocolo de ejecución experimental*

| Instancia | \(n\) | Formulación | Qubits | Réplicas | Máximo de evaluaciones | \(p\) |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| synth03 | 3 | Tradicional | 9 | 20 | 30 | 2 |
| synth03 | 3 | GPS | 30 | 20 | 30 | 2 |
| synth04 | 4 | Tradicional | 16 | 8 | 30 | 2 |
| synth05 | 5 | Tradicional | 25 | 8 | 30 | 2 |

*Nota.* El total es 56 ejecuciones. GPS con cuatro o más ciudades no se ejecutó: queda fuera del corte \(q\le 30\) de la Etapa 3. synth06 figura en la lista por defecto del escalamiento y tampoco entra en este protocolo. Los 20 y los 8 son los valores por defecto del script; la línea de comando real no está archivada.

## (C) Código

**Código 5.** Callback, QAOA con COBYLA, cronómetro y remuestreo de respaldo: `run_aws_full.py`, líneas 63–122. El programa cuadrático que alimenta esa llamada está en las líneas 53–61. El bucle de réplicas, el nombre del JSON y el salto cuando una réplica falla están en las líneas 141–160.

## (D) Evidencia

**Programa cuadrático y optimizador**

- Variables binarias \(x_0,\ldots,x_{n-1}\), lineal igual a la diagonal y cuadrático \(Q_{ij}+Q_{ji}\) solo si esa suma no es cero: `run_aws_full.py:53-61`.
- `QAOA(..., optimizer=COBYLA(maxiter=maxiter), reps=reps, callback=progress_callback)` y `MinimumEigenOptimizer(qaoa)`: `run_aws_full.py:77-80`. No se pasa `initial_point`, `initial_state`, `mixer`, `aggregation`, `transpiler` ni semilla.
- El docstring de `QAOA.__init__` en qiskit-algorithms 0.4.0 dice que, si `initial_point` es `None`, se genera un punto aleatorio en los límites del ansatz, y que si el ansatz no declara límites se usa \([-2\pi, 2\pi]\). La clase hereda ese comportamiento de `SamplingVQE`.
- COBYLA se construye solo con `maxiter` (`run_aws_full.py:78`). El script no le pasa semilla.

**Muestreador, disparos y descomposición**

- `DecomposingSampler()` sin argumentos: `run_aws_full.py:77`. Hereda de `SamplerV2` de Aer (`run_aws_full.py:25`).
- En Qiskit Aer 0.17.2, `qiskit_aer/primitives/sampler_v2.py`, `SamplerV2.__init__` declara `default_shots: int = 1024` y `seed: int | None = None`. El texto del argumento `seed` dice que, si es `None`, se usa un generador aleatorio. `run` asigna `shots = self._default_shots` cuando `shots` es `None`. El backend es `AerSimulator(**backend_options)` y las opciones por defecto son diccionarios vacíos. Este script no pasa `method` ni un modelo de ruido.
- El `run` del envoltorio reenvía `shots` sin cambiarlo (`run_aws_full.py:38-51`). El único entero de disparos escrito en el script es 4096, y solo en el remuestreo (`run_aws_full.py:98-100`).
- `decompose(reps=5)` y el comentario del tope de 27–28 qubits: `run_aws_full.py:28-44`.

**best_seen, bitstring y cronómetro**

- El callback recibe evaluación, parámetros, energía y metadatos, e imprime `eval {eval_count}/~{maxiter}`. Guarda energía y parámetros cuando la energía es menor que la ya vista (`run_aws_full.py:63-75`). `time.time()` en ese callback solo alimenta el mensaje impreso.
- Si `meo.solve` devuelve, el bitstring es `result.x` (`run_aws_full.py:85-86`). Si `result.fval` es menor que `best_seen`, se actualiza la energía (`run_aws_full.py:87-88`). El valor archivado es `best_seen["value"]` (`run_aws_full.py:133`).
- El remuestreo está en el `except` de esa resolución (`run_aws_full.py:89-121`): 4096 disparos, medición añadida al ansatz, y se conserva la cadena de menor \(x^{\mathsf T}Qx\). La inversión está en la línea 105, con el comentario de que el bit 0 es el de la derecha. Si también falla el remuestreo, la réplica sigue sin bitstring y conserva tiempo y energía (`run_aws_full.py:117-121`).
- `t0 = time.perf_counter()` en la línea 82, antes del `try`. `exec_time = time.perf_counter() - t0` en la línea 122, después del `try`/`except` y antes de calcular profundidad y compuertas (líneas 124–126). El intervalo incluye `meo.solve` y el remuestreo cuando ese `except` se ejecuta. Excluye la construcción de \(Q\) en `main`, el programa cuadrático (líneas 53–61), la creación del muestreador y del ansatz (líneas 77–80), el conteo de profundidad y la escritura del JSON (líneas 153–160).

**Réplicas y argumentos**

- Bucle `for rep in range(replicas)`, nombre `{instancia}_{formulación}_{rep}.json`, directorio `results_aws`: `run_aws_full.py:16` y `:141-160`. Una excepción se imprime y la réplica se salta con `continue` (`run_aws_full.py:145-148`). No hay un segundo intento.
- Defectos: `--replicas_paired` 20, `--replicas_scale` 8, `--include_scale` desactivado, `--scale_instances` `synth04,synth05,synth06`, `--reps` 2, `--maxiter` 30, `--paired_formulations` `traditional,gps` (`run_aws_full.py:176-191`).
- Sin la opción de escalamiento, `main` solo llama a synth03 (`run_aws_full.py:197-204`). Con la opción, el escalamiento construye solo el QUBO tradicional (`run_aws_full.py:207-216`). GPS de \(n\ge 4\) no tiene llamada.
- El formato `eval N/~30` sale de la línea 71. Aparece en `run_completo.log` (tradicional de synth03, lote de 20), en `results_aws_final/gps_batch_v2.log` (GPS, lote de 19, con `eval 30/~30`), en `results_aws_final/gps_batch_final.log` (GPS, lote anunciado de 20) y en `escala.log` (tradicional de synth04 y de synth05, 8 réplicas, también `eval N/~30`). `escala.log` abre synth03 con 0 réplicas en las dos formulaciones y cierra con 8 réplicas exitosas de synth04 y 8 de synth05; no menciona synth06. Ningún log guarda la línea `python run_aws_full.py ...`.
- `datos_tesis/README.md:54-66` describe el armado de las 20 filas GPS: 17 JSON de un lote de 19, las réplicas 1 y 2 solo en el CSV, y el JSON de `backup_rep1` reasignado porque su índice choca con otro. `readme.md:273` y `readme.md:277` dicen lo mismo: la línea de comando no está en los logs, y donde el log imprime `eval N/~30` el tope de ese lote es 30.
- Qubits de la tabla: 9 y 30 para \(n=3\), 16 para \(n=4\) y 25 para \(n=5\), que son \(n^2\) y \(3(n-1)(n+2)\) ya contados en la Etapa 3.

**Infraestructura en el repositorio**

- `readme.md:275`: EC2 t2.2xlarge, solo CPU; el tipo de instancia no está en los JSON; `run_aws_full.py` no tiene opción de GPU.
- `readme.md:269`: 31 GB y el corte \(2^{q}\cdot 16\) bytes. No dice 8 vCPU ni 32 GiB.
- `extras_tesis.py:59` y `:63`: la hoja de requisitos nombra la EC2 t2.2xlarge (CPU) y una sesión tmux. No es un registro de la sesión ni de una cuota de GPU.
- `qaoa_experiment.py:106` admite `--device GPU`. Ese argumento no existe en `run_aws_full.py`. No hay en el repositorio un texto de la denegación de la cuota.

## Pendientes

**[VERIFICAR]**

- 8 vCPU y 32 GiB de la t2.2xlarge. El README registra el tipo de instancia y 31 GB (`readme.md:269`, `readme.md:275`), no esos dos datos.
- Denegación de la cuota de GPU. No hay constancia en el repositorio.
- Uso efectivo de tmux. Consta como requisito en `extras_tesis.py:63`, no en un registro de sesión.
- Versiones de la EC2 (Qiskit 2.5.2, Aer 0.17.2, qiskit-algorithms 0.4.0, qiskit-optimization 0.7.0, NumPy 2.5.3, SciPy 1.18.1). No hay un archivo de requisitos que las fije.
- Método efectivo de `AerSimulator()` sin argumentos en Aer 0.17.2. El código no pasa `method`. La clase, con opciones vacías, deja el método automático del simulador.
- Línea de comando exacta de cada lote. Los logs muestran el tamaño del lote y `eval N/~30`, y no el comando.

**[CITA]**

- Algoritmo QAOA, para la ficha bibliográfica del método.
- COBYLA, para el optimizador clásico.
- `MinimumEigenOptimizer` de Qiskit Optimization 0.7.0.
- Punto inicial aleatorio de QAOA en qiskit-algorithms 0.4.0, docstring de `QAOA.__init__`.
- Disparos por defecto de `SamplerV2` en Qiskit Aer 0.17.2: `default_shots = 1024` en `qiskit_aer/primitives/sampler_v2.py`.

**[DECISIÓN DE LA AUTORA]**

- \(p=2\) y máximo de 30 evaluaciones (`run_aws_full.py:187-188`).
- No fijar semilla ni punto inicial (`run_aws_full.py:77-79`), de modo que cada réplica sea una muestra independiente.
- Ocho réplicas en el escalamiento de \(n=4\) y \(n=5\) (`run_aws_full.py:178-179`).
- Resolver el circuito con `decompose(reps=5)` en lugar de transpilar contra el backend de Aer (`run_aws_full.py:28-44`).
- Archivar la menor energía vista por el callback y, si la decodificación falla, remuestrear 4096 veces (`run_aws_full.py:63-75` y `:98-114`).
