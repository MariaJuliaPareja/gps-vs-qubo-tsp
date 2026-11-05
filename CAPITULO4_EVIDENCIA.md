# Capítulo IV — Evidencia extraída del código

Documento de hechos. Cada afirmación cita el archivo y la línea. Lo que no aparece en el código queda como NO ENCONTRADO EN EL CÓDIGO. No se usó `datos_tesis/scripts/` (copia excluida por la consigna). No existe `requirements.txt`, `pyproject.toml` ni otro archivo de dependencias con versiones fijadas.

## 4.1 Desarrollo por etapas de la metodología

### 4.1.1 Etapa 1 — Generación de instancias

Hay dos archivos con el mismo nombre. El que entra en la corrida es el de la raíz del repositorio, `synthetic_instances.py`. `run_aws_full.py` y `run_gps_n3_cloud.py` insertan el directorio del propio script al inicio de `sys.path` y luego importan `load_instance` (`run_aws_full.py:12-14`, `run_gps_n3_cloud.py:12-14`). Esos scripts están en la raíz, así que el módulo resuelto es `synthetic_instances.py` de la raíz. `qaoa_experiment.py:10` importa el mismo nombre sin alterar `sys.path`. `statistical_analysis_v2.py:28` importa `synthetic_instances` y llama a `load_instance` si existe (`statistical_analysis_v2.py:29-36`). `recursos_circuito.py:9` obtiene la matriz por `get_dist_matrix`, que a su vez importa ese módulo (`recursos_circuito.py:16-20`, `statistical_analysis_v2.py:26-28`). Ningún `.py` fuera de `datos_tesis/scripts/` importa `datos_tesis.generador` ni lee los CSV de `datos_tesis/instancias/`. La matriz que usan QAOA y el análisis se calcula en memoria.

`SAMPLE` define synth03→3, synth04→4, synth05→5 y también synth06→6 (`synthetic_instances.py:5-10`). `BASE_SEED = 42` (`synthetic_instances.py:12`). `load_instance(name)` comprueba el nombre y llama a `generate_instance(SAMPLE[name])` sin pasar semilla, así que rige el valor por defecto 42 (`synthetic_instances.py:26-29`, `synthetic_instances.py:15`).

`generate_instance` abre `np.random.default_rng(seed)` y toma `rng.random((n, 2)) * 100` (`synthetic_instances.py:16-17`). `numpy` Generator.random es uniforme en [0, 1), de modo que las coordenadas quedan en [0, 100). La matriz nace en ceros (`synthetic_instances.py:18`). Para i ≠ j se escribe `np.linalg.norm(coords[i] - coords[j])` (`synthetic_instances.py:19-22`). `norm` sin `ord` es la norma euclidiana. La diagonal no se rellena y permanece 0. La norma es simétrica, así que D también. Cada llamada crea un generador nuevo con la misma semilla y consume los primeros 2n uniformes: las ciudades de n son el prefijo de las de n+1. Eso se sigue del código; el README lo afirma en prosa (`readme.md:265`).

Si el archivo de la raíz se ejecuta como script, escribe en el directorio de trabajo `{nombre}_dist.csv` (matriz, `%.6f`, sin encabezado de índices) y `{nombre}_coords.csv` (encabezado `x,y`, sin columna de ciudad) (`synthetic_instances.py:32-37`). Los scripts de QAOA no invocan ese bloque: llaman a `load_instance`.

`datos_tesis/generador/synthetic_instances.py` repite `SAMPLE`, `BASE_SEED`, `generate_instance` y `load_instance` con el mismo cuerpo (`datos_tesis/generador/synthetic_instances.py:5-29`). La única diferencia está en `__main__`: imprime nombre, n y `dist.sum()`, y no escribe CSV (`datos_tesis/generador/synthetic_instances.py:32-34`).

`validate_formulations.py` no usa `synthetic_instances`. Su `random_instance` repite el mismo algoritmo (semilla explícita, uniforme en [0, 100), euclidiana, diagonal nula) (`validate_formulations.py:40-48`) y se llama con (n=4, semilla 42), (n=3, semilla 42) y (n=4, semilla 5) (`validate_formulations.py:53`, `validate_formulations.py:70`, `validate_formulations.py:90`).

⚠️ INCONSISTENCIA. `datos_tesis/README.md:9` dice que los CSV de `instancias/` se obtuvieron ejecutando `generador/synthetic_instances.py`. El `__main__` de ese archivo no escribe CSV (`datos_tesis/generador/synthetic_instances.py:32-34`). `datos_tesis/instancias/README.md:37` dice lo mismo y deja el paso de exportación como `[COMPLETAR]`. El formato que ese README describe (`ciudad,x,y` y matriz de distancias con índices de fila y columna, `datos_tesis/instancias/README.md:23-25`) no es el que escribe la raíz (`x,y` y matriz pelada, `synthetic_instances.py:35-37`). `readme.md:312` separa ambos formatos. El código de corrida no lee esos CSV.

⚠️ INCONSISTENCIA. El comentario de `dist_for` pone synth06 como ejemplo de instancia ausente (`recursos_circuito.py:17-18`). `SAMPLE` incluye synth06 (`synthetic_instances.py:9`) y `get_dist_matrix("synth06", 6)` llega a `load_instance`. El respaldo, si la importación fallara, usa semilla 42 en el cuadrado [0, 1) sin multiplicar por 100 (`recursos_circuito.py:22-24`).

### 4.1.2 Etapa 2 — Formulación QUBO tradicional

`build_traditional_qubo` toma la matriz n×n y devuelve Q de forma (n², n²) (`formulations.py:10-14`). La variable es x_{i,p}, ciudad i en la posición p, con índice `i * n + p` (`formulations.py:11`, `formulations.py:16-17`).

El peso de penalización es el argumento `penalty` si no es `None`; si no, `_default_penalty` (`formulations.py:13`). No hay otro peso. No existe un símbolo B en `formulations.py`.

Término de costo, tal como está escrito. Para todo i ≠ j y todo p en 0…n−1:

`Q[idx(i, p), idx(j, (p + 1) % n)] += dist_matrix[i, j]` (`formulations.py:19-24`).

Usa `(p + 1) % n`. El coeficiente es la distancia, sumada una sola vez en esa entrada de Q. No se simetriza esa entrada en esta función y no se multiplica por una constante distinta de 1.

Primera penalización (cada ciudad una vez). Para cada ciudad i y cada posición p: la diagonal de (i, p) suma −A, y para cada p2 ≠ p la entrada `Q[(i,p), (i,p2)]` suma A (`formulations.py:26-31`). El bucle recorre los pares ordenados, así que (p, p2) y (p2, p) reciben cada uno +A.

Segunda penalización (cada posición una vez). Para cada posición p y cada ciudad i: la misma diagonal suma otro −A, y para cada j ≠ i la entrada `Q[(i,p), (j,p)]` suma A (`formulations.py:33-38`). Tampoco aquí se escribe la constante +A de (Σx − 1)². En Q solo quedan el término lineal sobre la diagonal y los productos.

`_default_penalty` es `float(np.sum(dist_matrix)) * 2.0` (`formulations.py:6-7`). La suma recorre las n² entradas, diagonal incluida (ceros).

Todas las llamadas de corrida, validación, análisis y figuras usan `build_traditional_qubo(dist)` sin `penalty`: `qaoa_experiment.py:119`, `run_aws_full.py:200`, `run_aws_full.py:215`, `run_gps_n3_cloud.py:101`, `validate_formulations.py:55`, `statistical_analysis_v2.py:146`, `statistical_analysis_v2.py:196`, `figuras_tesis.py:123`, `recursos_circuito.py:57`.

### 4.1.3 Etapa 3 — Formulación GPS

`build_gps_qubo(dist, penalty=None, lam=None)` exige n ≥ 2 (`formulations.py:43-48`). Fija `N = n - 1` y `num_aug = N + 2` (`formulations.py:50-51`). Los índices aumentados son 0…N+1. `real_city` envía 0 y N+1 a la ciudad real 0, y deja igual el resto (`formulations.py:55-56`). La distancia entre aumentados es `dist_matrix[real_city(i), real_city(j)]` (`formulations.py:58-59`).

Pares. Se listan (i, j) con i ≠ j cuyo conjunto no sea {0, N+1} (`formulations.py:61-62`). El par depósito–depósito, en los dos sentidos, queda fuera. El comentario dice que ese par tiene costo cero y que las restricciones del artículo no lo prohíben (`formulations.py:45`).

`var_index` asigna un entero consecutivo a cada (i, j, r) con r = 0, 1, 2, en el orden de `pairs` y, dentro de cada par, r creciente (`formulations.py:63-64`). Q es cuadrada de lado `len(var_index)` (`formulations.py:65`). La función devuelve `(Q, var_index, N)` (`formulations.py:116`).

El conteo que sale de esa construcción es 3 × ((n+1)·n − 2) = 3(n−1)(n+2): hay (n+1)n pares ordenados con i ≠ j y se restan los dos del par excluido. La misma expresión cerrada está en `extras_tesis.py:27`, `pipeline_figura.py:246` y el texto del README (`readme.md:250`). `qubo_variable_count` no usa esa cuenta; ver el punto 8.

Auxiliares. `lin(v, c)` suma c a la diagonal (`formulations.py:67-68`). `quad(v1, v2, c)` reparte c/2 en cada fuera de diagonal, o suma c a la diagonal si v1 = v2 (`formulations.py:70-75`). `eq_one(terms, w)` suma −w a cada diagonal y, para cada par no ordenado, llama `quad(..., 2*w)` (`formulations.py:77-82`). Con x binaria, xᵀQx de ese bloque es w(Σx − 1)² sin la constante +w.

A es `penalty` o `_default_penalty` (`formulations.py:52`). `lam_val` es `lam` si no es `None`; si no, A (`formulations.py:53`).

Bloques, en el orden del código:

1. Costo. Para cada par, `lin(var_index[(i, j, 1)], d(i, j))` (`formulations.py:84-85`). Peso: la distancia, solo en la diagonal de la variable r = 1. No usa A ni λ.
2. Un estado por par. `eq_one` de las tres variables r = 0, 1, 2 de ese par, peso A (`formulations.py:87-88`).
3. Salida. Para cada i en 0…N (incluye el depósito de salida y excluye N+1), `eq_one` de las x_{i,j,1} con j válido, peso A (`formulations.py:90-93`).
4. Entrada. Para cada j en 1…N+1 (excluye el depósito de salida e incluye el de llegada), `eq_one` de las x_{i,j,1} con i válido, peso A (`formulations.py:95-98`).
5. Orden. Para i < j, salvo el par {0, N+1}, `eq_one` de (x_{i,j,2}, x_{j,i,2}), peso A (`formulations.py:100-103`). No interviene r = 0 en este bloque.
6. Transitividad. Para i, j, k distintos en 1…N (nodos intermedios; los depósitos no entran), con v_ji = (j, i, 2), v_kj = (k, j, 2), v_ki = (k, i, 2): `quad(v_ji, v_kj, λ)`, `quad(v_ji, v_ki, −λ)`, `quad(v_kj, v_ki, −λ)` y `lin(v_ki, λ)` (`formulations.py:105-114`). El peso es `lam_val`.

El número de ejecuciones del bucle de transitividad es (n−1)(n−2)(n−3). Para n = 3 el producto es 0 y el cuerpo no corre. `figuras_tesis.py:299-307` escribe en la tabla de recursos la fórmula de igualdades (3n² + 7n − 6)/2, la de transitividad (n−1)(n−2)(n−3) y, para el tradicional, 2n. Comprueba que en GPS con n = 3 la igualdad vale 21 (`figuras_tesis.py:309`). Esa fórmula no se calcula dentro de `build_gps_qubo`; el comentario de la figura desglosa one-hot por par (n²+n−2) + salida (n) + entrada (n) + orden (n(n+1)/2 − 1) (`figuras_tesis.py:299-301`). Esos cuatro sumandos coinciden con el número de llamadas a `eq_one` de los bloques 2 a 5.

El comentario de `extras_tesis.py:3-5` asigna r = 1 al arco directo i→j, r = 0 a «i antes que j y no adyacente» y r = 2 a «i después de j», y dice λ = A. El código no documenta r = 0 y r = 2 más que por los bloques que los usan: el costo y los grados usan r = 1, el orden y la transitividad usan r = 2, y r = 0 solo entra en el one-hot de tres estados.

### 4.1.4 Etapa 4 — Construcción y ejecución de QAOA

Hay tres ejecutores. Los tres arman un `QuadraticProgram` con una binaria `x{i}` por fila de Q, ponen en el lineal la diagonal Q[i, i] y en el cuadrático, para i < j, el coeficiente Q[i, j] + Q[j, i] si esa suma no es 0, y minimizan (`qaoa_experiment.py:54-62`, `run_aws_full.py:53-61`, `run_gps_n3_cloud.py:48-56`).

El ansatz no se construye en estos scripts. Se instancia `qiskit_algorithms.QAOA(sampler=..., optimizer=COBYLA(maxiter=maxiter), reps=reps)` (`qaoa_experiment.py:65`, `run_aws_full.py:78-79`, `run_gps_n3_cloud.py:59`). `run_aws_full.py` añade `callback=progress_callback` (`run_aws_full.py:78-79`). No se pasa mezclador, estado inicial, `initial_point` ni `shots` al constructor de `QAOA`. Esas opciones son NO ENCONTRADO EN EL CÓDIGO. Después de resolver se lee `qaoa.ansatz` (`qaoa_experiment.py:85`, `run_aws_full.py:124`, `run_gps_n3_cloud.py:76`). El comentario de `qaoa_experiment.py:26-28` y el de `run_aws_full.py:29-30` dicen que `QAOAAnsatz` emite una instrucción `QAOA` que Aer no ejecuta como compuerta de base. El único sitio que llama a `QAOAAnsatz` por nombre es `recursos_circuito.py:66` (etapa 7). `pipeline_figura.py:20-21` y `pipeline_figura.py:289` dibujan p = 2 y maxiter = 30; no ejecutan QAOA.

Optimizador. En los tres archivos es `COBYLA(maxiter=maxiter)` y ningún otro argumento (`qaoa_experiment.py:65`, `run_aws_full.py:78`, `run_gps_n3_cloud.py:59`). `rhobeg`, `tol`, `disp` u `options` son NO ENCONTRADO EN EL CÓDIGO. El resultado pasa por `MinimumEigenOptimizer(qaoa)` y `meo.solve(qp)` (`qaoa_experiment.py:66-73`, `run_aws_full.py:80-85`, `run_gps_n3_cloud.py:60-67`).

Valores por defecto de la línea de comandos. `run_aws_full.py`: `--reps` 2, `--maxiter` 30, `--replicas_paired` 20, `--replicas_scale` 8 (`run_aws_full.py:176-188`). `run_gps_n3_cloud.py`: `--replicas` 20, `--reps` 2, `--maxiter` 30 (`run_gps_n3_cloud.py:92-94`). `qaoa_experiment.py`: `--reps` 2, `--replicas` 5, `--maxiter` 50, `--device` CPU (`qaoa_experiment.py:103-106`); la firma `run_qaoa_on_qubo(..., maxiter: int = 50)` repite el 50 (`qaoa_experiment.py:16`). Los tres leen el valor desde argparse, así que la corrida puede cambiarlos. La línea de comando efectivamente usada en los lotes no está en el código. El README lo dice (`readme.md:273`).

Sampler y transpilación.

`qaoa_experiment.py` define `TranspilingSampler(AerSampler)`. En cada pub hace `SamplerPub.coerce(pub)`, cachea por `id(coerced.circuit)` y guarda `transpile(coerced.circuit, backend)` con `backend = AerSimulator(device=device)` (`qaoa_experiment.py:25-52`). No pasa `basis_gates`, `optimization_level`, `seed_transpiler` ni `coupling_map`. Reconstruye el pub con el circuito transpilado, `parameter_values` y `shots=coerced.shots`, y llama a `super().run(new_pubs, shots=shots)` (`qaoa_experiment.py:47-52`). `device` llega de `--device` (CPU o GPU).

`run_gps_n3_cloud.py` hace lo mismo con `AerSimulator(device="CPU")` fijo (`run_gps_n3_cloud.py:29-46`). Tampoco pasa `coupling_map` ni semilla de transpilador.

`run_aws_full.py` no importa `transpile` ni `AerSimulator`. `DecomposingSampler` hace `coerced.circuit.decompose(reps=5)`, cachea por identidad del circuito y rearma el pub con `SamplerPub` (`run_aws_full.py:28-51`). No hay `coupling_map` en esa llamada. El comentario (`run_aws_full.py:29-35`) dice que transpiló contra un `AerSimulator` imponía un `coupling_map` por defecto y un tope de unos 27–28 qubits, y que `decompose` evita ese camino. Eso está en el comentario; el código de este archivo no asigna `coupling_map`.

`shots` del bucle de optimización: el parámetro de `run` llega con valor por defecto `None` y se reenvía. El entero de shots de la optimización es NO ENCONTRADO EN EL CÓDIGO. El único entero escrito es 4096, y solo en el remuestreo manual de `run_aws_full.py:98-100`.

`best_seen` existe solo en `run_aws_full.py`. Un diccionario `{"value": None, "params": None}` se actualiza en el callback de COBYLA cuando la energía es menor (`run_aws_full.py:63-75`). El comentario dice que el callback se llama en cada evaluación y que `eval_count` puede pasar de `maxiter` (`run_aws_full.py:63-64`). Si `meo.solve` devuelve y `result.fval` es menor que `best_seen["value"]`, se reemplaza el valor (`run_aws_full.py:84-88`). Si `solve` lanza cualquier excepción, se intenta remuestrear `qaoa.ansatz.measure_all(inplace=False)` en `best_seen["params"]` con 4096 shots, se leen las cuentas de `pub_result.data.meas`, se invierte el bitstring (`bitstr[::-1]`, comentario: el bit 0 es el de la derecha) y se queda el x de menor `x @ Q @ x` (`run_aws_full.py:89-116`). `objective_value` guardado es `float(best_seen["value"])`, no `result.fval` directamente (`run_aws_full.py:133`). En `qaoa_experiment.py` y `run_gps_n3_cloud.py` no hay callback ni `best_seen`: el objetivo es `float(result.fval)` y el bitstring es `result.x` (`qaoa_experiment.py:94-95`, `run_gps_n3_cloud.py:85-86`). Esos dos, si `solve` lanza `IndexError`, reintentan hasta 3 veces; si los tres fallan, lanzan `RuntimeError` (`qaoa_experiment.py:71-82`, `run_gps_n3_cloud.py:65-73`). Otro tipo de excepción no entra en ese reintento.

Semillas de la corrida QAOA. `COBYLA` no recibe semilla. `QAOA` no recibe semilla. `AerSimulator` solo recibe `device`. `transpile` de los dos samplers que transpilán no recibe `seed_transpiler`. El bucle de réplicas es `for rep in range(...)` y no cambia ninguna semilla entre réplicas (`qaoa_experiment.py:125`, `run_aws_full.py:141`, `run_gps_n3_cloud.py:108`). Una semilla de optimizador, de muestreo o de transpilación de la corrida es NO ENCONTRADO EN EL CÓDIGO. La semilla 42 de instancias y la de `recursos_circuito.py` son otras etapas.

`execution_time_sec` es `time.perf_counter()` al salir menos el valor tomado justo antes de `meo.solve` (`qaoa_experiment.py:68-83`, `run_aws_full.py:82-122`, `run_gps_n3_cloud.py:62-74`). Queda dentro del intervalo: los intentos de `solve` (incluidos los `IndexError` reintentados en los dos primeros scripts) y, en `run_aws_full.py`, el remuestreo del `except` si lo hubo. También queda dentro la transpilación o el `decompose(reps=5)` que el sampler hace durante `solve`, porque ocurren dentro de `run`. Queda fuera: armar el `QuadraticProgram`, crear sampler, `QAOA` y `MinimumEigenOptimizer` (están antes de `t0`), y el `ansatz.decompose()` con el que se calculan `circuit_depth` y `gate_count` (está después de cerrar el cronómetro: `qaoa_experiment.py:85-87`, `run_aws_full.py:124-126`, `run_gps_n3_cloud.py:76-78`). La escritura del JSON y del CSV está en el llamador, después del `return`. El `elapsed` del callback usa `time.time()` desde antes de construir `QAOA` (`run_aws_full.py:65-72`) y solo se imprime; no es el campo guardado.

La profundidad y el número de compuertas del JSON salen de `ansatz.decompose()` sin argumento `reps`, sumando `count_ops()` (`qaoa_experiment.py:86-87`, `run_aws_full.py:125-126`). Ese circuito no es el que simula el sampler: en AWS el sampler usa `decompose(reps=5)` (`run_aws_full.py:44`); en los otros dos, `transpile(..., backend)`.

⚠️ INCONSISTENCIA. El comentario de `run_gps_n3_cloud.py:3` dice que GPS con n = 3 exige unos 1 TB de statevector. El mismo código construye GPS de synth03 (`run_gps_n3_cloud.py:102`) y el README asigna a ese caso 30 qubits y 16 GB, y el orden de 1 TB al tradicional de n = 6 con 36 qubits (`readme.md:269`). El encabezado de `run_aws_full.py:3` junta «GPS no es simulable para n>3» con el paréntesis «synth06, 36 qubits, ~1 TB». 36 qubits es el tradicional de n = 6 (`readme.md:257`); GPS de n = 4 está en 54 en esa misma tabla (`readme.md:255`).

### 4.1.5 Etapa 5 — Persistencia de resultados

Los tres ejecutores escriben el JSON al terminar cada réplica que no lanzó excepción, antes de la réplica siguiente.

Campos del JSON, en los tres: `n_qubits` (lado de Q), `circuit_depth`, `gate_count`, `execution_time_sec`, `objective_value`, `optimal_bitstring`, y luego `instance`, `n_cities`, `formulation`, `replica` (`qaoa_experiment.py:89-96` y `131-134`; `run_aws_full.py:128-135` y `151-154`; `run_gps_n3_cloud.py:80-87` y `118-121`). `json.dump(..., indent=2)`. El índice `replica` empieza en 0. No se guardan optimizador, `maxiter`, `reps`, shots, semilla ni dispositivo. En `run_aws_full.py` el bitstring puede quedar en `None` si también falla el remuestreo (`run_aws_full.py:111-121`); `json` lo escribe como null. En los otros dos, una réplica fallida no genera archivo (`continue` antes del `open`).

Nombre: `{instancia}_{formulacion}_{replica}.json`.

Carpetas y CSV:

- `qaoa_experiment.py` escribe en `results/` (`qaoa_experiment.py:13`, `133`). El CSV `results/consolidated.csv` se escribe una vez, al final, solo si hubo alguna réplica (`qaoa_experiment.py:137-145`).
- `run_aws_full.py` escribe en `results_aws/` (`run_aws_full.py:16`, `153`). El CSV `results_aws/aws_consolidated.csv` se reescribe después de cada réplica exitosa (`run_aws_full.py:156-160`) y otra vez al acabar `main` si `rows` no está vacío (`run_aws_full.py:218-219`).
- `run_gps_n3_cloud.py` escribe en `results_n3/` archivos `synth03_{formulacion}_{replica}.json` (`run_gps_n3_cloud.py:16`, `120`). El CSV `results_n3/n3_consolidated.csv` se escribe una vez al final (`run_gps_n3_cloud.py:124-131`).

Columnas del CSV, idénticas en los tres: `instance`, `n_cities`, `formulation`, `replica`, `n_qubits`, `circuit_depth`, `gate_count`, `execution_time_sec`, `objective_value` (`qaoa_experiment.py:139-140`, `run_aws_full.py:165-166`, `run_gps_n3_cloud.py:126-127`). `DictWriter(..., extrasaction="ignore")` deja fuera `optimal_bitstring`.

Qué corre cada `main`. `qaoa_experiment.py` recorre las instancias de `--instances` (por defecto todas las de `SAMPLE`, incluido synth06) y las formulaciones pedidas (`qaoa_experiment.py:114-121`). `run_gps_n3_cloud.py` solo synth03, tradicional y GPS (`run_gps_n3_cloud.py:98-103`). `run_aws_full.py` corre synth03 en las formulaciones de `--paired_formulations` (por defecto `traditional,gps`) y, solo con `--include_scale`, tradicional en `--scale_instances` (por defecto synth04, synth05, synth06) (`run_aws_full.py:197-216`).

⚠️ INCONSISTENCIA. Los ejecutores crean `results/`, `results_aws/` o `results_n3/`. El análisis y las figuras leen por defecto `results_aws_final/` y `results_aws_final/aws_consolidated.csv` (`statistical_analysis_v2.py:305-306`, `figuras_tesis.py:21-22`, `pipeline_figura.py:22-23`). No hay código que copie ni renombre una carpeta a la otra.

`statistical_analysis_v2.py` vuelve a escribir, en `--outdir` (por defecto `analisis_v2/`): `datos_consolidados.csv` sin la columna `optimal_bitstring` (`statistical_analysis_v2.py:315-316`) y `escalabilidad.csv` (`statistical_analysis_v2.py:340`). `figuras_tesis.py` escribe `figuras/datos_consolidados_corregidos.csv`, `figuras/tabla_recursos.csv`, `figuras/tabla_resultados.csv` y `figuras/tabla_brecha_ruta.csv` (`figuras_tesis.py:113`, `310`, `318`, `337`). `recursos_circuito.py` escribe `recursos_circuito.csv` en el directorio de trabajo (`recursos_circuito.py:90`).

### 4.1.6 Etapa 6 — Decodificación y validación

`traditional_tour(bits, n)` rehace la matriz n×n en orden de fila: `X[i, p]` es la ciudad i en la posición p, el mismo orden que `idx(i, p) = i*n+p` (`statistical_analysis_v2.py:107-109`, `formulations.py:16-17`). Exige que cada columna y cada fila sumen 1. Si no, devuelve `None`. Si sí, devuelve la ciudad `argmax` de cada columna (`statistical_analysis_v2.py:110-112`). No calcula el costo.

`decode_gps_solution` toma las aristas con r = 1 y bit 1 (`formulations.py:121`). Si no hay exactamente N+1 aristas, o el diccionario de sucesores no tiene N+1 claves, devuelve `None` (`formulations.py:122-126`). Recorre desde 0 siguiendo el sucesor, como máximo N+1 pasos; corta al llegar a N+1; devuelve `None` si falta sucesor, si repite un nodo o si el camino no termina en N+1 (`formulations.py:128-142`). Los intermedios deben ser exactamente el conjunto {1, …, N} y tener longitud N (`formulations.py:143-145`). Devuelve `[0] + intermedios`, sin el depósito de llegada N+1 (`formulations.py:146`). `tour_cost` cierra el ciclo con `(t + 1) % len(tour)` sobre la matriz real (`statistical_analysis_v2.py:138-139`).

`gps_violations` recorre las mismas familias que `build_gps_qubo` y devuelve una lista de textos (`statistical_analysis_v2.py:115-135`): one-hot de tres estados distinto de 1; salida de i = 0…N distinta de 1; entrada de j = 1…N+1 distinta de 1; para i < j, x_{ij,2} + x_{ji,2} distinto de 1; y, para cada permutación de tres intermedios, el patrón «x_{ji,2} y x_{kj,2} y no x_{ki,2}». No mira el costo.

`qubo_energy` es `float(x @ Q @ x)` (`statistical_analysis_v2.py:103-105`).

`evaluate_quality` recalcula Q con `build_traditional_qubo` o `build_gps_qubo` (sin `penalty` ni `lam`) y guarda `E_recalc` (`statistical_analysis_v2.py:195-208`). Factible, con bitstring: en tradicional, que `traditional_tour` no sea `None`; en GPS, que el tour decodificado exista y que `gps_violations` esté vacío (`statistical_analysis_v2.py:197-208`). Sin bitstring, solo si n = 3 y la matriz es simétrica: factible si `abs(fval - E_opt) <= TOL * abs(E_opt)` (`statistical_analysis_v2.py:211-214`). En otro caso el criterio queda en `"indeterminado (sin bitstring)"` y `feasible` sigue NaN (`statistical_analysis_v2.py:215-216`). Si es factible, `optimal` usa la misma comparación con `TOL` (`statistical_analysis_v2.py:217-218`).

`TOL = 1e-6` (`statistical_analysis_v2.py:23`). Es relativa: el umbral es `TOL` por el valor absoluto de la referencia (`E_opt` o `objective_value`).

Verificación xᵀQx frente a `objective_value`. Sobre las filas con `E_recalc` no nulo, si `abs(E_recalc - objective_value) > TOL * abs(objective_value)` imprime un aviso con el número de filas; si no, imprime que coinciden (`statistical_analysis_v2.py:222-229`). No corrige el valor. `gap_A` de este archivo usa `objective_value`, no `E_recalc`: `(fval - E_opt) / A`, con `A = _default_penalty(dist)` (`statistical_analysis_v2.py:181-192`). `gap_rel` divide por `abs(E_opt)` (`statistical_analysis_v2.py:193`).

`E_opt` es el mínimo de `qubo_energy` sobre soluciones factibles, no sobre todo el hipercubo (`statistical_analysis_v2.py:142-169`). Tradicional: todas las permutaciones, con el bit de la ciudad `c` en la posición `p` en el índice `c*n+p` (`statistical_analysis_v2.py:145-153`). GPS: si el número de pares (`len(var_index)//3`) es mayor que 12, avisa y devuelve NaN (`statistical_analysis_v2.py:155-158`). Si no, enumera una asignación de r por par, descarta las que `decode_gps_solution` o `gps_violations` rechazan, y toma la energía mínima (`statistical_analysis_v2.py:159-169`). Para n = 3 hay 10 pares (12 pares ordenados menos 2), así que 10 no supera 12 y sí se enumera. Para n = 4 hay 18 pares y devuelve NaN.

`validate_formulations.py` es un script aparte, solo bajo `__main__`. Compara el tradicional n = 4 (semilla 42) contra fuerza bruta del TSP y fuerza bruta de la QUBO (`validate_formulations.py:51-59`). GPS n = 2 usa una matriz fija [[0, 42.3], [42.3, 0]] (`validate_formulations.py:61-67`). GPS n = 3 enumera asignaciones de r (`validate_formulations.py:69-87`). Otro bloque con n = 4 y semilla 5 compara la energía de un orden coherente con la de un orden cíclico e imprime si la segunda es mayor (`validate_formulations.py:89-114`). No escribe archivos de resultados.

`figuras_tesis.py` define la brecha de otra forma: `E_usada` es `E_recalc` cuando existe y, si no, `objective_value`; `brecha = (E_usada - E_opt) / A` (`figuras_tesis.py:109-110`). Marca `excluir_energia` en synth03, GPS, réplica 1 (`figuras_tesis.py:111`). Esa fila sale de la brecha y de `tabla_resultados` (`figuras_tesis.py:208`, `figuras_tesis.py:312-317`). El comentario dice que se conserva para el tiempo (`figuras_tesis.py:2-4`); el boxplot de tiempo de n = 3 usa todas las filas de synth03 (`figuras_tesis.py:194`). La brecha de ruta, solo en factibles con `tour_cost`, es `(tour_cost - opt) / opt * 100`, con `opt` el mínimo por permutaciones que empiezan en 0 (`figuras_tesis.py:320-335`).

⚠️ INCONSISTENCIA. `readme.md:283-287` dice que, con bitstring, la energía de la brecha es E_recalc y que la réplica synth03/gps/1 queda fuera de la energía y de la brecha. Eso está en `figuras_tesis.py:109-111`. `statistical_analysis_v2.py` no excluye esa réplica y calcula `gap_A` con `objective_value` (`statistical_analysis_v2.py:187-192`).

⚠️ INCONSISTENCIA. El comentario de `validate_formulations.py:69` dice enumeración 3^12 para GPS n = 3. El bucle usa `ordered_pairs`, que ya quitó {0, N+1} (`validate_formulations.py:74-77`), es decir 10 pares y 3^10.

### 4.1.7 Etapa 7 — Conteo de recursos sin simulación

`recursos_circuito.py` no llama a `Sampler`, `QAOA` ni `MinimumEigenOptimizer`. Para n = 3, 4, 5 y 6 y para las dos formulaciones (`recursos_circuito.py:55-57`) construye Q, la simetriza con `(Q+Q.T)/2` y se queda con las filas cuyo suma absoluta supera 1e-12 (`recursos_circuito.py:59-61`). Esas son las variables activas. El subbloque es `Qr`.

`qubo_to_ising` vuelve a simetrizar, y para x = (1−z)/2 escribe el campo y los acoplos, sin el término constante (`recursos_circuito.py:33-51`). Con tolerancia 1e-12: h_i = −0.5·Q[i,i] − 0.5·(suma de la fila i − Q[i,i]); J_ij = 0.5·Q[i,j] para i < j. La etiqueta de Pauli pone Z en la posición `n-1-i` (el índice 0 queda a la derecha). Devuelve `SparsePauliOp.from_list`. El docstring menciona «(+ constante)» (`recursos_circuito.py:34`) y el operador no incluye esa identidad.

⚠️ INCONSISTENCIA. El docstring de `qubo_to_ising` anuncia la constante (`recursos_circuito.py:34`). El `return` solo lleva los términos h y J (`recursos_circuito.py:51`).

El ansatz de esta etapa sí es explícito: `QAOAAnsatz(H, reps=REPS)` con `REPS = 2`, seguido de `measure_all()` (`recursos_circuito.py:11`, `recursos_circuito.py:66-67`). No se pasa mezclador ni estado inicial. La transpilación es `transpile(ansatz, basis_gates=["rz", "sx", "x", "cx"], optimization_level=1, seed_transpiler=42)` (`recursos_circuito.py:12-13`, `recursos_circuito.py:68`). No hay backend ni `coupling_map`. `SEED = 42` (`recursos_circuito.py:13`).

Guarda, por fila: n, formulación, origen de la instancia, variables de Q, qubits activos, variables descartadas, términos lineales (diagonal no nula), términos cuadráticos (triángulo superior no nulo), profundidad del ansatz ya con `measure_all`, profundidad transpilada, compuertas totales excepto `measure` y `barrier`, número de `cx`, y memoria `(2 ** qubits_activos) * 16 / 1e9` (`recursos_circuito.py:71-85`). Escribe `recursos_circuito.csv` (`recursos_circuito.py:89-91`).

## 4.2 Estadística y pruebas

El README llama a `statistical_analysis_v2.py` el análisis usado en la tesis (`readme.md:235`). `statistical_analysis.py` es el plan anterior (`readme.md` lo lista aparte en el inventario inglés, línea 22, y el docstring del archivo dice Shapiro-Wilk, Wilcoxon, correlación y LOWESS, `statistical_analysis.py:1`). Las cifras de las figuras salen de `figuras_tesis.py`.

### 4.2.1 Estadística descriptiva

En `statistical_analysis_v2.py`, para synth03 y el tiempo: mediana GPS, mediana tradicional y cociente de esas medianas (`statistical_analysis_v2.py:240-244`). Si un grupo tiene al menos 3 réplicas, guarda el p de Shapiro-Wilk y no lo usa para elegir la prueba (`statistical_analysis_v2.py:245-247`). Para la factibilidad, con filas de `feasible` no nulo: el texto `k/n` y un intervalo que la clave llama `IC95`, obtenido con `stats.binomtest(k, n).proportion_ci(method="wilson")` (`statistical_analysis_v2.py:233-237`, `statistical_analysis_v2.py:260-265`). No se pasa `confidence_level`; el 95 % está en el nombre de la clave, no en un argumento. Recursos por formulación: mínimo y máximo de `n_qubits`, `circuit_depth` y `gate_count`, y el cociente de medianas GPS/tradicional (`statistical_analysis_v2.py:279-286`). Esos tres no entran a una prueba; el comentario dice que son constantes (`statistical_analysis_v2.py:4`). Calidad: `DataFrame.describe()` de `E_opt`, `gap_A` y `gap_rel` por formulación, que en pandas incluye cuenta, media, desviación, mínimo, cuartiles y máximo (`statistical_analysis_v2.py:333`). Escalabilidad, solo filas tradicionales: cuenta de réplicas, primer `n_qubits`, mediana del tiempo, media de factibilidad ignorando NaN, mediana de `gap_A` (`statistical_analysis_v2.py:289-295`).

`figuras_tesis.py` agrupa por n y formulación, después de quitar la réplica marcada, y resume cuenta de réplicas, suma de factibles, mediana, media y desviación de la brecha, y mediana del tiempo (`figuras_tesis.py:312-317`). Las barras de factibilidad de n = 3 usan otro Wilson, con z = 1.96 escrito en la fórmula (`figuras_tesis.py:88-95`, `figuras_tesis.py:178-185`). La brecha de ruta resume media y máximo del porcentaje, solo en factibles (`figuras_tesis.py:330-334`).

`statistical_analysis.py` resume, por formulación y para `execution_time_sec`, `circuit_depth`, `gate_count`, `n_qubits` y `objective_value`: media, desviación, mínimo, máximo y cuenta (`statistical_analysis.py:11-13`, `statistical_analysis.py:66-68`). No calcula mediana ni Wilson.

### 4.2.2 Estadística inferencial

`statistical_analysis_v2.py` define `ALPHA = 0.05` (`statistical_analysis_v2.py:22`) y no vuelve a leer esa constante. Las pruebas imprimen el p-valor y no lo comparan con 0.05 (`statistical_analysis_v2.py:328-335`).

Sin `--paired`, el tiempo usa Mann-Whitney U bilateral y la factibilidad usa Fisher exacto (`statistical_analysis_v2.py:253-256`, `statistical_analysis_v2.py:272-275`). Con `--paired`, el tiempo usa Wilcoxon sobre la intersección de los índices `replica` y la factibilidad usa McNemar exacto: `binomtest(b, b+c, 0.5)` con b = solo tradicional factible y c = solo GPS factible; si no hay discordantes, p = 1 (`statistical_analysis_v2.py:248-251`, `statistical_analysis_v2.py:266-271`). El help del flag dice que solo corresponde al caso en que ambas formulaciones compartieron semilla por réplica (`statistical_analysis_v2.py:309-310`). El código no lee ni comprueba ninguna semilla; el flag solo cambia la prueba. Wilcoxon se llama como `stats.wilcoxon(g[common], t[common])` sin `alternative` (`statistical_analysis_v2.py:250`). La alternativa de Wilcoxon es NO ENCONTRADO EN EL CÓDIGO. Fisher se llama `stats.fisher_exact(table)` sin `alternative` (`statistical_analysis_v2.py:274`). La alternativa de Fisher es NO ENCONTRADO EN EL CÓDIGO.

Shapiro-Wilk en este archivo es un diagnóstico del tiempo, con n ≥ 3 (`statistical_analysis_v2.py:245-247`). No condiciona Mann-Whitney ni Wilcoxon. No hay Shapiro sobre la factibilidad. El supuesto de normalidad no selecciona la prueba.

`statistical_analysis.py` sí usa `ALPHA = 0.05`: normal si p > 0.05 (`statistical_analysis.py:24`), Wilcoxon significativo si p < 0.05 (`statistical_analysis.py:35`), y Pearson si ambos Shapiro superan 0.05; si no, Spearman (`statistical_analysis.py:44-51`). El Wilcoxon de ese archivo es incondicional: no hay rama hacia una prueba t (`statistical_analysis.py:32`). Su entrada por defecto es `results/consolidated.csv` (`statistical_analysis.py:105`).

### 4.2.3 Test 1 — Fisher exacto (factibilidad)

Se aplica solo si no está `--paired`, sobre synth03, después de `dropna` en `feasible` (`statistical_analysis_v2.py:260-261`, `statistical_analysis_v2.py:322`, `statistical_analysis_v2.py:334`). `t` es la serie booleana tradicional y `g` la de GPS, indexadas por `replica`. La tabla que se pasa a `fisher_exact` es exactamente (`statistical_analysis_v2.py:273`):

```
[[ factibles_tradicional,  no_factibles_tradicional ],
 [ factibles_gps,          no_factibles_gps         ]]
```

con cada celda `int(suma)` o `int((~serie).sum())`. Las filas con `feasible` nulo no entran. El código no reordena columnas ni añade totales.

### 4.2.4 Test 2 — Mann-Whitney U (tiempo)

Sin `--paired`, `stats.mannwhitneyu(g, t, alternative="two-sided")` (`statistical_analysis_v2.py:253`). `g` son los `execution_time_sec` de GPS y `t` los de tradicional, en synth03 (`statistical_analysis_v2.py:241-242`, `statistical_analysis_v2.py:322`). La alternativa escrita es bilateral (`"two-sided"`).

`r` es el campo `r_rank_biserial` (`statistical_analysis_v2.py:256`):

`2 * u.statistic / (len(g) * len(t)) - 1`.

`u.statistic` es el estadístico que devuelve SciPy para ese orden de muestras (GPS primero). No hay otra corrección ni valor absoluto en el código.

### 4.2.5 LOWESS

En `statistical_analysis_v2.py` el suavizado existe solo si la formulación tradicional tiene al menos 3 valores distintos de `n_cities` (`statistical_analysis_v2.py:297`). La llamada es `sm.nonparametric.lowess(tr["execution_time_sec"], tr["n_cities"], frac=1.0, it=0)` (`statistical_analysis_v2.py:299`). Variable dependiente: tiempo de ejecución. Regresor: número de ciudades. Solo filas `formulation == "traditional"` de todo el dataframe cargado, no un subconjunto fijado a synth03–05 (`statistical_analysis_v2.py:290`). El título impreso dice «synth03-05» (`statistical_analysis_v2.py:337`); el filtro del código no recorta por nombre de instancia.

`figuras_tesis.py` hace dos LOWESS, ambos con `frac=1.0` e `it=0`. Uno sobre la brecha tradicional (ya sin la marca de exclusión, que no afecta al tradicional) contra `n_cities` (`figuras_tesis.py:215-216`). Otro sobre `execution_time_sec` tradicional contra `n_cities`, aquí sin quitar filas por energía (`figuras_tesis.py:257-258`).

`statistical_analysis.py` llama `lowess(sub[metric], sub["n_cities"], frac=frac)` con `frac=0.5` por defecto y sin argumento `it` (`statistical_analysis.py:55-63`). El `it` de esa llamada es NO ENCONTRADO EN EL CÓDIGO. Lo aplica, por formulación, a cada métrica del informe (`execution_time_sec`, `circuit_depth`, `gate_count`, `n_qubits`, `objective_value`) si hay al menos 3 puntos (`statistical_analysis.py:66-77`).

⚠️ INCONSISTENCIA. El LOWESS del análisis v2 y el de las figuras usan `frac=1.0` e `it=0` sobre tiempo (y, en las figuras, también sobre brecha). `statistical_analysis.py` usa `frac=0.5` y no fija `it`.

## Sección final

1. Versiones. No hay archivo de requisitos con pines. El README pide, sin versión, `numpy pandas scipy statsmodels matplotlib pillow` y `qiskit qiskit-aer qiskit-algorithms qiskit-optimization` (`readme.md:296-297`). `qiskit-aer-gpu` se menciona solo para `--device GPU` (`readme.md:300`). Los imports usan `qiskit`, `qiskit_aer`, `qiskit_algorithms` y `qiskit_optimization` (`qaoa_experiment.py:17-23`, `run_aws_full.py:21-26`, `recursos_circuito.py:4-6`) y no consultan la versión instalada. «Qiskit 2.x» aparece en un comentario (`qaoa_experiment.py:28`) y como texto de una celda de la tabla de requisitos (`extras_tesis.py:61`), no como restricción de instalación. Python 3.14.7 y NumPy 2.4.3 aparecen como el entorno en el que se contrastaron los CSV con el generador (`readme.md:316`, `datos_tesis/instancias/README.md:39`), no como requisito del código. Una versión exigida de qiskit, de qiskit-aer o de Python, fijada en requirements o en un import, es NO ENCONTRADO EN EL CÓDIGO.

2. `_default_penalty(dist_matrix)` devuelve `float(np.sum(dist_matrix)) * 2.0` (`formulations.py:6-7`).

3. Semillas. Instancias de producción: `BASE_SEED = 42` en cada `generate_instance` (`synthetic_instances.py:12-16`). La validación usa además la semilla 5 en un caso (`validate_formulations.py:90`). Transpilación de la corrida QAOA: NO ENCONTRADO EN EL CÓDIGO. Transpilación del conteo de recursos: `seed_transpiler=42` (`recursos_circuito.py:13`, `recursos_circuito.py:68`). Optimizador: `COBYLA(maxiter=maxiter)` sin semilla (`run_aws_full.py:78` y equivalentes). Muestreo: `AerSampler` / `AerSimulator` / `QAOA` sin semilla; el bucle de réplicas no fija una semilla por réplica (`run_aws_full.py:141`). El `default_rng(0)` de `figuras_tesis.py:133` solo desplaza puntos en las figuras.

4. Shots de la optimización: NO ENCONTRADO EN EL CÓDIGO. El constructor de `QAOA` no recibe `shots`, y el sampler reenvía `shots=None` más los shots que ya traiga el pub (`qaoa_experiment.py:37-52`, `run_aws_full.py:38-51`). El único literal es 4096, en el remuestreo de respaldo de `run_aws_full.py:98-100`.

5. El costo tradicional usa `(p + 1) % n` (`formulations.py:24`). No tiene un peso B. El coeficiente escrito es `dist_matrix[i, j]`, una vez, en `Q[idx(i, p), idx(j, (p + 1) % n)]` (`formulations.py:19-24`). A multiplica solo las dos penalizaciones (`formulations.py:26-38`).

6. Sí, en el sentido del valor por defecto. `lam_val = lam if lam is not None else A` (`formulations.py:53`). Todas las llamadas encontradas fuera de `datos_tesis/scripts/` son `build_gps_qubo(dist)` o `build_gps_qubo(dist)[0]`, sin `penalty` y sin `lam`: `qaoa_experiment.py:121`, `run_aws_full.py:203`, `run_gps_n3_cloud.py:102`, `validate_formulations.py:63`, `validate_formulations.py:72`, `validate_formulations.py:91`, `statistical_analysis_v2.py:154`, `statistical_analysis_v2.py:203`, `figuras_tesis.py:124`, `pipeline_figura.py:90`, y `recursos_circuito.py:57` vía `builder(dist)`. No hay ninguna llamada que pase un λ distinto de A.

7. `run_aws_full.py` y `run_gps_n3_cloud.py` tienen por defecto `--reps 2` y `--maxiter 30` (`run_aws_full.py:187-188`, `run_gps_n3_cloud.py:93-94`). Ninguno llama a QAOA con otro literal. Ambos aceptan otros valores por la línea de comandos, y esa línea no está en el repositorio (`readme.md:273`). `qaoa_experiment.py`, que el README separa de la corrida de EC2 (`readme.md:273`, `readme.md:314`), tiene por defecto `--maxiter 50` y `--reps 2` (`qaoa_experiment.py:103-105`). `decompose(reps=5)` en el sampler de AWS es la profundidad de `decompose`, no el `reps` de QAOA (`run_aws_full.py:44`). `recursos_circuito.py` fija `REPS = 2` y no usa `maxiter` (`recursos_circuito.py:11`).

8. `qubo_variable_count` solo se define y se imprime en el `__main__` de `formulations.py:149-159`. Ningún otro archivo fuera de `datos_tesis/scripts/` lo importa ni lo llama. La fórmula de ahí es `gps_vars = 3 * (N + 2) * (N + 1)` con `N = n - 1`, es decir 3n(n+1) (`formulations.py:150-151`). La construcción real excluye el par {0, N+1} antes de crear `var_index` (`formulations.py:61-64`), así que el lado de Q es 3((n+1)n − 2) = 3(n−1)(n+2). Para n = 3 la función imprime 36 y `len(var_index)` es 30.

9. Fragmentos candidatos para la lista de códigos. Como máximo cuatro.

- `formulations.py:10-40`. La QUBO tradicional completa: índice i·n+p, costo con `(p+1) % n` sin peso B, y las dos penalizaciones con A. Es el bloque que la sección 4.1.2 tiene que mostrar entero.
- `formulations.py:61-114`. Pares excluidos, `var_index`, `eq_one` y los seis bloques de GPS con peso A o λ. Es la formulación que la sección 4.1.3 describe.
- `run_aws_full.py:63-135`. Callback, `best_seen`, `COBYLA(maxiter)`, `reps`, el cronómetro de `execution_time_sec`, el remuestreo a 4096 shots con el bitstring invertido y el objetivo que realmente se guarda. Es el protocolo de la corrida de EC2.
- `statistical_analysis_v2.py:103-135` junto con `statistical_analysis_v2.py:240-276`. Energía xᵀQx, `traditional_tour`, `gps_violations`, Mann-Whitney bilateral, la fórmula de r y la tabla de Fisher. Son la validación y las dos pruebas del capítulo. Si la lista admite un solo rango contiguo por ítem, el cuarto puede quedarse en `statistical_analysis_v2.py:240-276` y dejar la decodificación para el primero de una versión recortada; el rango 103-135 no es contiguo con 240-276.
