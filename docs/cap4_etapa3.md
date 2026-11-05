# 4.1.3 Etapa 3: Conteo de recursos del circuito

## (A) Texto del apartado

La tercera etapa registra el circuito QAOA sin simular el vector de estado. La profundidad, el número de compuertas y la memoria de ese vector quedan fijados por la matriz \(Q\), por el número de capas y por los parámetros del transpilador. El optimizador y los disparos no entran en el cálculo. La misma entrada produce, por tanto, el mismo conteo cada vez que se repite, y el registro alcanza también los casos cuyo vector de estado supera la memoria de la máquina. Esos casos permanecen en la descripción del circuito y salen de la simulación.

El conteo parte de la matriz \(Q\) de cada formulación y de cada instancia de tres a seis ciudades. Antes de armar el operador se retiran las filas nulas; en estos ocho circuitos no hubo ninguna, y el número de qubits coincide con el orden de \(Q\). Una función del propio script, distinta del conversor de la corrida, pasa del QUBO simetrizado al hamiltoniano de Ising: con \(x=(1-z)/2\), cada campo local no nulo da un término \(Z\) y cada acoplamiento no nulo da un término \(ZZ\). La constante aditiva de esa sustitución no se guarda, porque no modifica el circuito. El campo local mezcla la diagonal de \(Q\) con el resto de la fila, de modo que una diagonal nula puede seguir generando un \(Z\). Ocurre en GPS con cinco ciudades: la matriz tiene 72 diagonales no nulas y el Ising tiene 84 términos \(Z\), uno por qubit. En los otros siete circuitos ambas cuentas coinciden.

Con ese operador se construye el ansatz de \(p=2\), se miden todos los qubits y el circuito se transpila a la base \(\{rz, sx, x, cx\}\) (Código 4.4). La llamada usa nivel de optimización 1 y semilla 42, y no recibe ni backend ni mapa de acoplamiento. [DECISIÓN DE LA AUTORA: nivel de optimización 1, semilla del transpilador y medición de todos los qubits antes de medir la profundidad.] En Qiskit 2.6.1, la ausencia de mapa deja las compuertas de dos qubits definidas sobre cualquier par, y el pase de nivel 1 no inserta enrutamiento. [DECISIÓN DE LA AUTORA: no fijar `coupling_map`, para que el conteo recoja la formulación y no la topología de un equipo.] Un mapa de dispositivo añadiría intercambios. En la ruta de simulación, el comentario del script de corrida registra que un mapa por defecto del backend llegó a imponer un tope de 27–28 qubits.

El indicador 1.1 es el número de qubits lógicos de ese circuito. El 1.2 es la profundidad del circuito ya transpilado, con la capa de medición incluida. El 1.3 separa el total de compuertas, del que se excluyen `measure` y `barrier`, y el número de CNOT. En los ocho circuitos ese número cumple \(\mathrm{CNOT}=2\cdot p\cdot(\text{términos }ZZ)\), con \(p=2\): cada término \(ZZ\) aporta dos CNOT por capa, el diccionario de compuertas no contiene intercambios y el nivel 1 no altera el total. El 1.4 es la memoria del vector de estado, \(2^{q}\cdot 16\) bytes. La Tabla 4.6 usa esa memoria para decidir qué filas caben en la simulación. Las profundidades y los totales de compuertas, que comparan las formulaciones, quedan para el capítulo de resultados.

La profundidad y el total de compuertas archivados en los JSON de la corrida miden otro objeto. Salen de `ansatz.decompose()`, una sola descomposición del ansatz que construye el optimizador, y no de la transpilación a la base. La descomposición de cinco repeticiones que el muestreador aplica para poder ejecutar el circuito tampoco es la cifra que se guarda. En los consolidados de la corrida, synth03 tiene profundidad 6 en todos los registros, y el número de compuertas es \(2q+5\) (23 en la tradicional, de 9 qubits, y 65 en GPS, de 30). La misma profundidad 6 aparece en la tradicional de cuatro y de cinco ciudades. Esa columna no distingue el tamaño del hamiltoniano. La métrica de esta etapa es el circuito transpilado.

El criterio de memoria toma 32 GiB (≈ 31 GB utilizables) y admite el circuito cuando \(2^{q}\cdot 16\) bytes no superan 31 GB. El mayor entero \(q\) que lo cumple es 30, el mismo corte que calcula el generador de figuras. La Tabla 4.6 marca como simulables la formulación tradicional de tres, cuatro y cinco ciudades y GPS de tres ciudades. La tradicional de seis ciudades y GPS de cuatro, cinco y seis ciudades superan el límite: siguen en este conteo y quedan fuera del vector de estado de la etapa siguiente. El script de la corrida no evalúa esa desigualdad. Siempre puede lanzar synth03 en las dos formulaciones y, si se activa el escalamiento, la tradicional de cuatro, cinco y seis ciudades; el propio aviso del argumento indica que seis ciudades exigen alrededor de 1 TB. GPS por encima de tres ciudades no entra en esa lista. [VERIFICAR: si la línea de comando de la máquina activó el escalamiento y hasta qué instancia.]

## (B) Tabla 4.6

**Tabla 4.6**

*Memoria requerida y simulabilidad por formulación*

| \(n\) | Formulación | Qubits | Memoria \(2^{q}\cdot 16\) bytes | Simulable |
| ---: | --- | ---: | --- | --- |
| 3 | Tradicional | 9 | 8 KiB | Sí |
| 3 | GPS | 30 | 16 GiB | Sí |
| 4 | Tradicional | 16 | 1 MiB | Sí |
| 4 | GPS | 54 | 256 PiB | No |
| 5 | Tradicional | 25 | 512 MiB | Sí |
| 5 | GPS | 84 | 256 YiB | No |
| 6 | Tradicional | 36 | 1 TiB | No |
| 6 | GPS | 120 | \(2^{44}\) YiB | No |

*Nota.* Las unidades son binarias (1 KiB \(= 2^{10}\) bytes). El corte es \(2^{q}\cdot 16 \le 31\times 10^{9}\) bytes, esto es \(q\le 30\), sobre 32 GiB (≈ 31 GB utilizables). GPS con tres ciudades usa 16 GiB, equivalentes a 17,18 GB decimales, y queda dentro del corte. La tradicional con seis ciudades usa 1 TiB. \(2^{44}\) YiB \(= 17\,592\,186\,044\,416\) YiB. En los ocho circuitos el número de qubits es el orden de \(Q\): ninguna fila nula fue descartada.

## (C) Tabla de recursos para el Capítulo V y código

**PARA CAPÍTULO V.** Recursos del circuito QAOA transpilado (\(p=2\), base \(\{rz, sx, x, cx\}\), nivel de optimización 1, semilla 42, sin mapa de acoplamiento).

| \(n\) | Formulación | Qubits | Términos \(Z\) | Términos \(ZZ\) | Profundidad | Compuertas | CNOT | Razón de qubits | Razón de profundidad | Razón de compuertas | Razón de CNOT |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | Tradicional | 9 | 9 | 36 | 88 | 351 | 144 | — | — | — | — |
| 3 | GPS | 30 | 30 | 45 | 112 | 720 | 180 | 3,333 | 1,273 | 2,051 | 1,250 |
| 4 | Tradicional | 16 | 16 | 96 | 145 | 816 | 384 | — | — | — | — |
| 4 | GPS | 54 | 54 | 108 | 160 | 1458 | 432 | 3,375 | 1,103 | 1,787 | 1,125 |
| 5 | Tradicional | 25 | 25 | 200 | 214 | 1575 | 800 | — | — | — | — |
| 5 | GPS | 84 | 84 | 222 | 235 | 2592 | 888 | 3,360 | 1,098 | 1,646 | 1,110 |
| 6 | Tradicional | 36 | 36 | 360 | 295 | 2700 | 1440 | — | — | — | — |
| 6 | GPS | 120 | 120 | 405 | 331 | 4230 | 1620 | 3,333 | 1,122 | 1,567 | 1,125 |

*Nota.* Los términos \(Z\) y \(ZZ\) son los del hamiltoniano de Ising que entra al ansatz, no las diagonales de \(Q\). Esa distinción solo cambia GPS con cinco ciudades: `recursos_circuito.csv` anota 72 términos lineales, porque cuenta diagonales no nulas, y el Ising tiene 84 términos \(Z\). En el resto de las filas las dos cuentas coinciden, y los términos \(ZZ\) coinciden en las ocho con la columna `terminos_cuadraticos`. La profundidad incluye la medición final. El total de compuertas excluye `measure` y `barrier`. Cada razón es el valor GPS dividido por el tradicional del mismo \(n\), con tres decimales. \(\mathrm{CNOT}=4\cdot(\text{términos }ZZ)\) en las ocho filas.

**Código 4.4.** Construcción del ansatz y transpilación: `recursos_circuito.py`, líneas 65–68. Los argumentos de esa llamada están en las líneas 11–13 (`REPS = 2`, base `{rz, sx, x, cx}`, semilla 42). El paso a Ising que alimenta el ansatz es `qubo_to_ising`, líneas 33–51. El descarte de filas nulas es las líneas 59–63.

## (D) Evidencia

Recálculo con `.venv/bin/python` y Qiskit 2.6.1, sin escribir en el repositorio. El módulo `recursos_circuito.py` no se importó, porque al cargarse vuelve a guardar el CSV. Se repitieron sus funciones en memoria. Cada fila del CSV coincidió en qubits activos, términos cuadráticos, profundidad transpilada, compuertas, CNOT y memoria en GB decimales. La columna `terminos_lineales` también coincidió con el recuento de diagonales no nulas; el número de \(Z\) del Ising se calculó aparte.

**Parámetros de la transpilación**

- Base, semilla y capas: `recursos_circuito.py:11-13` (`REPS = 2`, `BASIS = ["rz", "sx", "x", "cx"]`, `SEED = 42`).
- Llamada: `transpile(ansatz, basis_gates=BASIS, optimization_level=1, seed_transpiler=SEED)` en `recursos_circuito.py:68`. No se pasan `backend`, `coupling_map` ni `target`.
- Qiskit 2.6.1, con `coupling_map is None` y `basis_gates` definido, construye el target añadiendo cada compuerta de la base sin restringir pares (`target.py:873-880` del paquete). `build_coupling_map` devuelve `None` cuando la compuerta de dos qubits es global (`target.py:610-613`). El pase de nivel 1 omite el diseño y el enrutamiento si el mapa es nulo (`preset_passmanagers/level1.py:65-73`).
- El CSV no tiene columna de versión de Qiskit. El recálculo con 2.6.1 reprodujo las celdas numéricas del archivo.
- `optimization_level` admite 0, 1, 2 y 3 en el transpilador. El script fija 1. No hay en el repositorio una justificación distinta de esa línea.

**Ising, qubits y la identidad de las CNOT**

- Simetrización y descarte de filas con suma absoluta \(\le 10^{-12}\): `recursos_circuito.py:59-63`. Descartes observados: 0 en los ocho circuitos. Qubits: 9, 30, 16, 54, 25, 84, 36, 120.
- \(h_i=-\tfrac12 Q_{ii}-\tfrac12\sum_{j\neq i}Q_{ij}\) y \(J_{ij}=\tfrac12 Q_{ij}\): `recursos_circuito.py:38-50`. El comentario de la línea 34 menciona la constante; el código no la agrega al operador.
- Términos \(Z\) / \(ZZ\) obtenidos del `SparsePauliOp`: tradicional 9/36, 16/96, 25/200, 36/360; GPS 30/45, 54/108, 84/222, 120/405. Campos locales con valor absoluto \(\le 10^{-12}\): cero en los ocho. En GPS con \(n=5\) hay 72 diagonales no nulas y 84 términos \(Z\).
- Ansatz: `QAOAAnsatz(H, reps=REPS)` y `measure_all()` en `recursos_circuito.py:66-67`. Antes de medir, el ansatz es una sola instrucción `QAOA` de profundidad 1; después, profundidad 2. Esa profundidad de bloques es la columna `profundidad_bloques` del CSV, igual a 2 en las ocho filas, y no es la métrica.
- Compuertas transpiladas de synth03 tradicional: `rz` 162, `cx` 144, `sx` 45, `measure` 9, `barrier` 1. El total del script suma todo menos `measure` y `barrier` (`recursos_circuito.py:82`): 351. La profundidad `tc.depth()` es 88 e incluye la medición.
- CNOT frente a \(2\cdot p\cdot(ZZ)\), con \(p=2\): 144, 180, 384, 432, 800, 888, 1440 y 1620. Igualdad exacta en los ocho. Ningún circuito transpilado contenía `swap`.

**Memoria y corte**

- Fórmula del script: \((2^{q})\cdot 16/10^{9}\), en GB decimales (`recursos_circuito.py:84`). Para 30 qubits el archivo da 17,179869184, que son \(2^{34}\) bytes \(= 16\) GiB.
- Corte del generador de figuras: `RAM_GB = 31` y \(q=\lfloor\log_2(31\cdot 10^{9}/16)\rfloor\) (`figuras_tesis.py:25` y `:126`). El recálculo dio \(q=30\). \(2^{30}\cdot 16=17\,179\,869\,184\le 31\times 10^{9}\). \(2^{31}\cdot 16=34\,359\,738\,368\), igual a 32 GiB y por encima de 31 GB.
- Simulables: tradicional \(n=3,4,5\) (8 KiB, 1 MiB, 512 MiB) y GPS \(n=3\) (16 GiB). Fuera: tradicional \(n=6\) (1 TiB) y GPS \(n=4,5,6\) (256 PiB, 256 YiB, \(2^{44}\) YiB).

**Qué lee el archivo de recursos**

- `figuras_tesis.py:23` carga `recursos_circuito.csv`. `figuras_tesis.py:115-117` deriva `densidad_Q` y `grado_medio` de `terminos_cuadraticos` y `qubits_activos`.
- `fig02_qubits_vs_n.png` usa `qubits_activos` (`figuras_tesis.py:154-155`). `fig03_profundidad_cnot.png` usa `profundidad_transpilada` y `cx` (`figuras_tesis.py:166-168`). `fig10_dispersion_Q.png` usa la densidad y el grado derivados (`figuras_tesis.py:267-268`).
- `tabla_recursos.csv` copia qubits, términos lineales y cuadráticos del CSV, densidad, grado, profundidad, compuertas, CNOT y memoria, y añade restricciones por fórmula (`figuras_tesis.py:293-310`). Esas figuras y esa tabla pertenecen al capítulo de resultados, no a esta etapa.

**Profundidad guardada en la corrida**

- Cálculo: `circuit_depth = ansatz.decompose().depth()` y `gate_count = sum(ansatz.decompose().count_ops().values())` en `run_aws_full.py:125-126`. El ansatz es el de `qiskit_algorithms.QAOA` (`run_aws_full.py:78-79`), no el circuito ya transpilado.
- El muestreador guarda `decompose(reps=5)` solo para ejecutar (`run_aws_full.py:44`). Esa expansión no se escribe en el JSON.
- `results_aws/aws_consolidated.csv`, synth03 tradicional, 20 filas: `n_qubits` 9, `circuit_depth` 6, `gate_count` 23. synth04 tradicional, 8 filas: 16, 6, 37. synth05 tradicional, 1 fila: 25, 6, 55. En los tres, \(2q+5\) da 23, 37 y 55.
- `results_aws_final/aws_consolidated.csv`, synth03 GPS, 19 filas: `n_qubits` 30, `circuit_depth` 6, `gate_count` 65, y \(2\cdot 30+5=65\). Ese archivo no trae filas tradicionales.
- El mismo `QAOAAnsatz` de la biblioteca de circuitos, descompuesto una vez en este entorno, da profundidad 5 y \(q+4\) compuertas (`h` y cuatro `PauliEvolution`). No reproduce el 6 ni el \(2q+5\) de los JSON. Esos números salen del ansatz del optimizador. `qiskit_algorithms` no está instalado en este entorno, así que esa descomposición no se volvió a ejecutar; se leyó de los CSV.
- `statistical_analysis_v2.py:4-6` trata qubits, profundidad y compuertas de la corrida como constantes descriptivas. `resources_table` (`statistical_analysis_v2.py:279-286`) agrega esas columnas del CSV de resultados, no las de `recursos_circuito.csv`.

**Origen de las instancias del conteo**

- `dist_for` llama a `get_dist_matrix("synth0{n}", n)` (`recursos_circuito.py:15-25`). El recálculo obtuvo synth03, synth04, synth05 y synth06, el mismo `origen_instancia` del CSV. No hizo falta la matriz aleatoria de respaldo.

## Pendientes

**[VERIFICAR]**

- Versión de Qiskit con la que se escribió `recursos_circuito.csv`. El archivo no la registra. El recálculo con Qiskit 2.6.1 reproduce sus celdas numéricas.
- Línea de comando de la máquina: si activó `--include_scale` y si la lista llegó a synth06. El script no aplica el corte de 31 GB; el aviso de `--include_scale` sitúa synth06 en torno a 1 TB (`run_aws_full.py:180-186`).
- Lista interna de compuertas de `ansatz.decompose()` en `qiskit_algorithms.QAOA`. Aquí no está instalado ese paquete. Los CSV fijan profundidad 6 y \(2q+5\) compuertas; el ansatz de `qiskit.circuit.library` no da esas cifras.

**[CITA]**

- Algoritmo QAOA, para la primera mención del ansatz en el capítulo si aún no tiene ficha. El código usa la clase `QAOAAnsatz` de Qiskit y no trae la referencia.

**[DECISIÓN DE LA AUTORA]**

- Nivel de optimización 1 y semilla de transpilación 42 (`recursos_circuito.py:13` y `:68`).
- No pasar `backend` ni `coupling_map`, de modo que el conteo no incorpore la topología de un dispositivo (`recursos_circuito.py:68`; el tope de 27–28 qubits de un mapa por defecto está comentado en `run_aws_full.py:31-35`).
- Medir todos los qubits antes de tomar la profundidad, e excluir `measure` y `barrier` del total de compuertas (`recursos_circuito.py:67` y `:82`).
- Contar los recursos sobre las variables de fila no nula, aunque en estas instancias el descarte sea cero (`recursos_circuito.py:59-63`).
