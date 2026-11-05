# 4.1.5 Etapa 5: Consolidación y control de calidad

## (A) Texto del apartado

La quinta etapa reúne las réplicas que entran al análisis y deriva, para cada una, la energía, la factibilidad y las dos brechas. La fuente es `results_aws_final/`. El directorio `results_aws/` corresponde a una ejecución preliminar y los programas de análisis no lo abren. La carga recorre todos los JSON de la carpeta, incluidas las subcarpetas (Código 6). Si la ruta contiene la palabra backup, la fila queda marcada como respaldo. El archivo `backup_rep1/synth03_gps_0.json` trae el índice 0, que ya ocupa un JSON principal, y el procedimiento le asigna el índice siguiente al máximo de esa formulación: queda como réplica 19. Después se lee el CSV consolidado. Una terna (instancia, formulación, réplica) que ya está en un JSON no se duplica. Las réplicas GPS 1 y 2 de synth03 no tienen JSON y entran desde el CSV, con origen `csv_sin_bitstring` y sin cadena de bits. El conjunto queda en 56 filas: 20 de GPS y 20 de la formulación tradicional en synth03, y 8 tradicionales en synth04 y en synth05 (Tabla X).

Con cadena de bits, la energía de trabajo es \(x^{\mathsf T}Qx\), recalculada con la misma \(Q\) de la formulación. En la tradicional, el vector se reordena como matriz de ciudad por posición, en el orden \(i\cdot n+p\), y la solución es factible cuando cada fila y cada columna suman uno. El recorrido es la ciudad activa de cada posición. En GPS, la decodificación sigue los arcos de estado \(r=1\) desde el depósito de salida hasta el de llegada y exige visitar cada nodo intermedio una vez. La factibilidad exige, además, que no haya violaciones de estado único, salida, entrada, orden ni transitividad. El análisis lee la lista ya guardada en el JSON y no invierte los bits. La convención de que el bit 0 está a la derecha se aplicó solo al construir esa lista, en el remuestreo de la etapa anterior. El costo decodificado es la longitud del ciclo sobre la matriz de distancias.

\(E_{\mathrm{opt}}\) es la menor energía entre las codificaciones factibles de esa \(Q\). En la formulación tradicional se enumeran las permutaciones de las ciudades. En GPS se enumeran las asignaciones de un estado por par, y se conservan las que decodifican y no violan restricciones; el cálculo se hace cuando el número de pares no pasa de 12, condición que cumple synth03. La brecha energética del archivo de análisis es \((\textit{objective\_value}-E_{\mathrm{opt}})/A\). Las figuras usan otra energía: \(x^{\mathsf T}Qx\) cuando el bitstring existe, y el objetivo archivado cuando no existe. Su brecha es \((E-E_{\mathrm{opt}})/A\). La brecha de ruta es otra magnitud. Compara el costo del ciclo decodificado con el costo óptimo del vendedor viajero, en porcentaje, y solo entra una fila factible que tenga ese costo. El óptimo de ruta fija la ciudad 0 y permuta las restantes.

El control de calidad deja cuatro decisiones explícitas sobre filas, sin retirarlas del archivo consolidado. En synth05 tradicional, réplica 4, \(x^{\mathsf T}Qx\) y `objective_value` difieren en 91,196. El objetivo guarda la menor energía vista durante la optimización, y la energía recalculada es la del bitstring. El programa avisa cuando esa diferencia supera una tolerancia relativa de \(10^{-6}\). Las figuras, al tener bitstring, usan la energía recalculada. [DECISIÓN DE LA AUTORA: no descartar la réplica 4; usar \(x^{\mathsf T}Qx\) como energía de la brecha cuando el bitstring existe.] Las réplicas GPS 1 y 2 de synth03 no tienen bitstring. Con tres ciudades y matriz simétrica hay un solo costo de recorrido, así que toda codificación factible tiene la misma energía, igual a \(E_{\mathrm{opt}}\). El código marca factible la fila sin bitstring cuando el objetivo archivado coincide con ese óptimo dentro de la misma tolerancia, y deja el costo de ruta vacío. [DECISIÓN DE LA AUTORA: aceptar ese criterio solo en \(n=3\).] La réplica GPS 1 de synth03 tiene un objetivo igual al \(E_{\mathrm{opt}}\) de la formulación tradicional, \(-4\,488{,}727\). Las figuras la retiran de la brecha energética y la mantienen en el diagrama de tiempo de synth03. La tabla agrupada que calcula a la vez brecha y tiempo mediano también la omite. El análisis estadístico no usa esa bandera. [DECISIÓN DE LA AUTORA: tratar esa fila como contaminada para la energía y conservarla para el tiempo.]

La higiene separa los ensayos del conjunto analizado. Dos registros, `gps_test_fix.log` y `gps_test_fix2.log`, muestran lotes de una y de cinco réplicas con el aviso `eval N/~5`, y COBYLA eleva el máximo de evaluaciones a 6. El script de corrida escribe siempre el nombre de producción `synth03_gps_{réplica}.json`, de modo que esos ensayos habrían ocupado archivos de ese nombre. Los JSON que carga el análisis corresponden a lotes cuyo aviso es `eval N/~30`. [VERIFICAR: el README y los commits no dicen que esas réplicas se hayan relanzado en limpio; se infiere porque el conjunto usado es el de los lotes con tope 30.]

## (B) Tabla

**Tabla X**

*Composición del conjunto de datos analizado*

| Instancia | Formulación | Réplicas | Origen | Observaciones |
| --- | --- | ---: | --- | --- |
| synth03 | GPS | 20 | 17 JSON, 2 CSV, 1 respaldo | Las réplicas 1 y 2 no tienen bitstring. El respaldo se reindexa como réplica 19. La réplica 1 se aparta de la brecha energética en las figuras. |
| synth03 | Tradicional | 20 | 20 JSON | |
| synth04 | Tradicional | 8 | 8 JSON | |
| synth05 | Tradicional | 8 | 8 JSON | En la réplica 4, `objective_value` y \(x^{\mathsf T}Qx\) difieren en 91,196. |

*Nota.* Total: 56 filas. La fuente es `results_aws_final/`. `results_aws/` no entra en esta carga.

## (C) Código

**Código 6.** Carga y consolidación: `statistical_analysis_v2.py`, líneas 63–100 (`load_results`). La decodificación y la factibilidad están en las líneas 107–135 de ese archivo y en `decode_gps_solution` (`formulations.py`, líneas 119–146). \(E_{\mathrm{opt}}\) y la brecha del archivo de análisis están en las líneas 142–169 y 191–192. La brecha de las figuras y la exclusión de la réplica GPS 1 están en `figuras_tesis.py`, líneas 109–111. La brecha de ruta está en las líneas 320–335.

## (D) Evidencia

**Origen y consolidación**

- Entrada por defecto del análisis: `results_aws_final` y `results_aws_final/aws_consolidated.csv` (`statistical_analysis_v2.py:306-307`). Las figuras usan las mismas rutas (`figuras_tesis.py:21-22`). Ninguno de los dos abre `results_aws/`.
- JSON recursivos, marca `backup` si la ruta contiene esa palabra, y reindexación si el índice ya existe: `statistical_analysis_v2.py:65-81`. El índice nuevo es el máximo de la formulación más uno.
- Filas solo en el CSV, con `source = csv_sin_bitstring` y `optimal_bitstring = None`: `statistical_analysis_v2.py:83-98`. Si el JSON ya existe y los tiempos difieren en más de un segundo, imprime un aviso y se queda con el JSON (`statistical_analysis_v2.py:89-93`).
- Conteo ya verificado del archivo `analisis_v2/datos_consolidados.csv`: synth03 GPS, 17 `json`, 2 `csv_sin_bitstring` y 1 `backup`; synth03 tradicional, 20 `json`; synth04 tradicional, 8 `json`; synth05 tradicional, 8 `json`.

**Decodificación, factibilidad y orden de bits**

- Energía \(x^{\mathsf T}Qx\): `statistical_analysis_v2.py:103-105`.
- Tradicional: `reshape(n, n)` con el comentario de que \(X[i,p]\) es la ciudad \(i\) en la posición \(p\); factible si las sumas de filas y de columnas valen uno; el recorrido es el argmax de cada columna (`statistical_analysis_v2.py:107-112`). En `evaluate_quality`, factible es que esa función no devuelva `None`, y el costo solo se calcula en ese caso (`statistical_analysis_v2.py:195-201`).
- GPS: violaciones de estado único, salida, entrada, orden y transitividad (`statistical_analysis_v2.py:115-135`). El recorrido exige \(N+1\) arcos de estado 1, un camino simple de 0 a \(N+1\) y los intermedios \(\{1,\ldots,N\}\) (`formulations.py:119-146`). Factible si el recorrido existe y la lista de violaciones está vacía (`statistical_analysis_v2.py:202-210`).
- El análisis no invierte el vector. La inversión del bit 0, el carácter de la derecha, está en el remuestreo de la corrida (`run_aws_full.py:105`), antes de guardar la lista.

**Réplicas sin bitstring en \(n=3\)**

- Si no hay lista y \(n=3\) y la matriz es simétrica, factible cuando \(|\textit{objective\_value}-E_{\mathrm{opt}}|\le 10^{-6}\,|E_{\mathrm{opt}}|\). El comentario dice que, con tres ciudades y distancias simétricas, todas las rutas cuestan lo mismo, y por eso factible equivale a energía igual al óptimo (`statistical_analysis_v2.py:211-214`). La tolerancia es `TOL = 1e-6` (`statistical_analysis_v2.py:23`).
- Si falta el bitstring y \(n\) no es 3, el criterio queda en `indeterminado (sin bitstring)` y la factibilidad no se asigna (`statistical_analysis_v2.py:215-216`).
- Esas filas no reciben `tour_cost`. La brecha de ruta descarta los costos nulos (`figuras_tesis.py:329`).

**Óptimos y brechas**

- \(E_{\mathrm{opt}}\) tradicional: mínimo de \(x^{\mathsf T}Qx\) sobre las permutaciones, con un bit por ciudad y posición (`statistical_analysis_v2.py:142-153`).
- \(E_{\mathrm{opt}}\) GPS: enumeración de los estados por par, solo si hay a lo sumo 12 pares; se exige decodificación y cero violaciones (`statistical_analysis_v2.py:154-169`). synth03 tiene 10 pares.
- `gap_A = (objective_value - E_opt) / A` y `gap_rel = (objective_value - E_opt) / |E_opt|` (`statistical_analysis_v2.py:191-192`). Esta brecha no sustituye el objetivo por \(x^{\mathsf T}Qx\).
- Aviso si, habiendo bitstring, \(x^{\mathsf T}Qx\) y `objective_value` difieren más que la tolerancia relativa (`statistical_analysis_v2.py:221-229`). El caso ya medido es synth05 tradicional, réplica 4, con diferencia 91,196. `objective_value` es `best_seen`, la menor energía vista en la optimización (`run_aws_full.py:73-75` y `:133`).
- Figuras: `E_usada` es \(x^{\mathsf T}Qx\) si existe y, si no, el objetivo; `brecha = (E_usada - E_opt) / A` (`figuras_tesis.py:109-110`). El comentario de las líneas 4–5 enuncia esa regla.
- Brecha de ruta: \((\textit{tour\_cost}-\textit{costo óptimo})/\textit{costo óptimo}\times 100\), media y máximo, solo en filas con `feasible_f == 1` y costo no nulo (`figuras_tesis.py:320-335`). El costo óptimo fija la ciudad 0 y permuta el resto (`figuras_tesis.py:321-324`).

**Réplica GPS 1 y archivos escritos**

- Comentario: se excluye de energía y brecha porque `objective_value` es idéntico al \(E_{\mathrm{opt}}\) tradicional, y se conserva para el tiempo (`figuras_tesis.py:2-3`). La bandera es synth03, GPS y réplica 1 (`figuras_tesis.py:111`). El valor \(-4\,488{,}727\) es el \(E_{\mathrm{opt}}\) tradicional de synth03 ya calculado en la Etapa 2.
- La brecha de las figuras de synth03 usa la negación de esa bandera (`figuras_tesis.py:208-209`). El diagrama de tiempo de synth03 toma la serie completa (`figuras_tesis.py:194`). La tabla agrupada filtra la bandera antes de calcular brecha y tiempo mediano (`figuras_tesis.py:312-316`). `statistical_analysis_v2.py` no crea ni lee `excluir_energia`; su comparación de tiempo usa todas las filas de synth03 (`statistical_analysis_v2.py:322` y `:240-244`).
- `analisis_v2/datos_consolidados.csv` se escribe sin la columna `optimal_bitstring` (`statistical_analysis_v2.py:316`). Columnas: `n_qubits`, `circuit_depth`, `gate_count`, `execution_time_sec`, `objective_value`, `instance`, `n_cities`, `formulation`, `replica`, `source`, `path`, `A`, `E_opt`, `gap_A`, `gap_rel`, `E_recalc`, `feasible`, `optimal`, `tour_cost`, `criterio`, `violaciones`.
- `figuras/datos_consolidados_corregidos.csv` guarda el marco completo (`figuras_tesis.py:113`). Añade `optimal_bitstring`, `feasible_f`, `E_usada`, `brecha` y `excluir_energia`.

**Higiene de los ensayos con tope 5**

- `results_aws_final/gps_test_fix.log` anuncia 1 réplica e imprime `eval 1/~5`. `results_aws_final/gps_test_fix2.log` anuncia 5 réplicas e imprime `eval N/~5`, y llega a `eval 6/~5`. Ambos muestran el aviso de COBYLA de que MAXFUN se eleva a 6.
- El nombre de archivo de una réplica exitosa es `{instancia}_{formulación}_{rep}.json` (`run_aws_full.py:153`). Un ensayo con ese script escribe el mismo nombre que la producción.
- `readme.md:273` y `datos_tesis/README.md:60-68` documentan los lotes con `eval N/~30` y dicen que la línea de comando no quedó en los logs. No dicen que los ensayos con tope 5 se hayan relanzado. Los mensajes de commit tampoco lo dicen.

## Pendientes

**[VERIFICAR]**

- Relanzamiento en limpio de las réplicas que los ensayos con máximo 5 habrían escrito con nombre de producción. Los logs `gps_test_fix.log` y `gps_test_fix2.log` prueban que esos ensayos existieron. El README y los commits no registran el reemplazo. El conjunto analizado es el de los lotes con `eval N/~30`.

**[CITA]**

- No hace falta una referencia nueva para este apartado. Las brechas y la decodificación se definen en el código del estudio.

**[DECISIÓN DE LA AUTORA]**

- Usar `results_aws_final/` como única fuente del análisis y dejar `results_aws/` fuera (`statistical_analysis_v2.py:306-307`, `figuras_tesis.py:21-22`).
- Reindexar el JSON de respaldo cuando su índice choca con otro, en lugar de descartarlo (`statistical_analysis_v2.py:74-81`).
- Incorporar las réplicas GPS 1 y 2 desde el CSV aunque no tengan bitstring, y juzgar su factibilidad por la energía solo porque \(n=3\) y la matriz es simétrica (`statistical_analysis_v2.py:83-98` y `:211-214`).
- No descartar synth05 tradicional, réplica 4. En las figuras, la brecha usa \(x^{\mathsf T}Qx\) cuando hay bitstring (`figuras_tesis.py:109-110`). El archivo del análisis conserva la brecha calculada con `objective_value` (`statistical_analysis_v2.py:191`).
- Excluir synth03 GPS, réplica 1, de la brecha energética de las figuras y mantenerla en el diagrama de tiempo (`figuras_tesis.py:2-3`, `:111`, `:194`, `:208-209`).
