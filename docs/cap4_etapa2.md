# 4.1.2 Etapa 2: Construcción y validación de las formulaciones

## (A) Texto del apartado

La segunda etapa codifica cada instancia como matriz QUBO en las dos formulaciones, con un mismo peso de penalización. En la formulación tradicional, de tipo one-hot ciudad por posición [CITA: formulación QUBO one-hot del vendedor viajero], la variable binaria \(x_{i,p}\) vale uno cuando la ciudad \(i\) ocupa la posición \(p\). Su índice en el vector de decisión es \(i\cdot n+p\), y la matriz \(Q\) tiene orden \(n^2\) (Código 4.2). El costo escribe la distancia \(d_{ij}\) en la entrada que acopla \(x_{i,p}\) con \(x_{j,(p+1)\bmod n}\), para cada par de ciudades distintas y cada posición. Cada ciudad y cada posición aportan una penalización \(A(\sum x-1)^2\); en la matriz se guarda el desarrollo de ese cuadrado y el sumando constante \(+A\) de cada restricción queda fuera de \(Q\). Esas restricciones son \(2n\).

En la formulación GPS se toma \(N=n-1\) y el grafo se amplía a los nodos \(0,\ldots,N+1\) (González-Bermejo et al., 2022; Código 4.3; Figura 4.2). El depósito se duplica: el nodo 0 es la salida, el nodo \(N+1\) es la llegada, y al leer la distancia ambos se identifican con la ciudad real 0. Hay una variable \(x_{ij}^{r}\) por cada par ordenado de nodos distintos y cada estado \(r\in\{0,1,2\}\). El par no ordenado \(\{0,N+1\}\) no se genera. [DECISIÓN DE LA AUTORA: excluir ese par; el comentario del código señala que su costo sería nulo y que las restricciones del artículo no lo prohíben.] Quedan fuera dos pares ordenados y seis variables. El orden de \(Q\) es \(3(n-1)(n+2)\): 30, 54, 84 y 120 variables para \(n=3,4,5,6\). La función `qubo_variable_count`, que cuenta \(3n(n+1)\), solo se imprime al ejecutar el módulo y no interviene en la construcción ni en el análisis.

El papel de cada \(r\) es el que le asignan los bloques del hamiltoniano. La variable \(x_{ij}^{1}\) recibe el costo en su coeficiente lineal y entra en la restricción de salida del nodo \(i\) y en la de entrada del nodo \(j\). La variable \(x_{ij}^{2}\) entra en la restricción de orden, que exige un único estado activo entre \(x_{ij}^{2}\) y \(x_{ji}^{2}\), y en los monomios de transitividad de los nodos intermedios. La variable \(x_{ij}^{0}\) solo entra en la restricción que elige un estado del conjunto \(\{0,1,2\}\) para ese par. La Figura 4.2 rotula además \(r=1\) como arco directo, \(r=0\) como precedencia no adyacente y \(r=2\) como el orden inverso. [VERIFICAR: si esos rótulos, y el conjunto de bloques, coinciden con las ecuaciones 8–13 de González-Bermejo et al. (2022).]

\(H_{\mathrm{GPS}}\) suma seis bloques (Código 4.3). El costo pesa \(x_{ij}^{1}\) con la distancia entre las ciudades reales de sus extremos. Los cuatro bloques de igualdad —un estado por par, salida, entrada y orden— pesan \(A\). La transitividad, escrita para cada terna de índices distintos en \(\{1,\ldots,N\}\), pesa \(\lambda\). En todas las llamadas del estudio el argumento \(\lambda\) se omite, y el código lo iguala a \(A\). [DECISIÓN DE LA AUTORA: fijar \(\lambda=A\).] El peso común es \(A=2\cdot\sum_{i\neq j}d_{ij}\): la diagonal de distancias es nula, y la penalización por defecto devuelve el doble de la suma de todas las entradas. Las dos formulaciones quedan así en la misma escala. La brecha que el análisis posterior divide por \(A\), \((E-E_{\mathrm{opt}})/A\), se expresa en unidades de ese peso. [DECISIÓN DE LA AUTORA: compartir \(A\) para que esa brecha sea comparable entre formulaciones.]

La Tabla 4.4 reúne variables y restricciones de \(n=3\) a \(n=6\). La formulación tradicional tiene \(n^2\) variables y \(2n\) igualdades. GPS tiene \(3(n-1)(n+2)\) variables, \((3n^2+7n-6)/2\) igualdades y \((n-1)(n-2)(n-3)\) polinomios de transitividad. Las tres expresiones coinciden, en esos cuatro tamaños, con los bucles que escriben \(Q\). La Tabla 4.5 describe la matriz simetrizada de synth03, synth04 y synth05. GPS usa más variables y, a la vez, una \(Q\) más dispersa: la densidad de elementos no nulos fuera de la diagonal es 10,34 %, 7,55 % y 6,37 %, frente a 100,00 %, 80,00 % y 66,67 % en la formulación tradicional. El grado medio del grafo de interacción es 3, 4 y 5,29 en GPS, y 8, 12 y 16 en la tradicional.

En synth05, doce variables de GPS tienen coeficiente lineal exactamente nulo. Son las \(x_{ij}^{2}\) con ambos índices en \(\{1,\ldots,N\}\) y \(N=4\). El bloque de un estado les resta \(A\), el de orden les resta otro \(A\), y cada una aparece como término lineal de la transitividad en \(N-2=2\) ternas, con aporte \(\lambda(N-2)\). Con \(\lambda=A\) los tres aportes suman cero. Esas variables conservan acoplamientos cuadráticos, de modo que su fila no queda vacía. En synth03 y synth04, donde \(N-2\) vale 0 y 1, el mismo coeficiente lineal es \(-2A\) y \(-A\), y ninguno se anula.

La codificación se contrastó con el óptimo del vendedor viajero en `validate_formulations.py`. La formulación tradicional se probó en cuatro ciudades con semilla 42, matriz idéntica a synth04: el mínimo de \(x^{\mathsf T}Qx\) sobre los \(2^{16}\) vectores binarios decodifica a un recorrido de costo 196,3285, igual al óptimo enumerado. GPS se probó en tres ciudades con la misma semilla, que es synth03: el bloque recorre las asignaciones de un estado por par. Hay diez pares ordenados, luego \(3^{10}\) asignaciones; el rótulo impreso del bloque dice \(3^{12}\). El mínimo decodifica a un recorrido de costo 195,1621, igual al óptimo. El script imprime la comparación y no detiene la ejecución si los costos difieren. Añade dos pruebas ajenas a las instancias de la corrida: GPS de dos ciudades con distancia 42,3, cuyo mínimo cuesta 84,6, y una comparación de orden en cuatro ciudades con semilla 5, donde la asignación alterada queda por encima del orden consistente (\(-42\,288{,}1852\) frente a \(-49\,376{,}5194\)).

En synth03, la energía óptima de referencia recoge el efecto de haber omitido la constante de cada igualdad. La búsqueda exhaustiva de soluciones factibles da \(E_{\mathrm{opt}}=-4\,488{,}727236\) en la formulación tradicional y \(E_{\mathrm{opt}}=-16\,198{,}450462\) en GPS. El costo óptimo del recorrido es 195,162054 y \(A=780{,}648215\). La primera energía es ese costo menos \(6A\), y la segunda es el mismo costo menos \(21A\). En \(n=3\) la transitividad no escribe términos, así que las 21 igualdades agotan la penalización de una solución factible y cada igualdad satisfecha aporta \(-A\). La diferencia entre la energía enumerada y esa expresión queda por debajo de \(10^{-11}\).

## (B) Ecuaciones LaTeX

Las igualdades siguientes son el polinomio que evalúa \(x^{\mathsf T}Qx\) con variables binarias (\(x^2=x\)). Cada restricción de igualdad aparece como \((\sum x-1)^2-1\): el cuadrado es el de la Figura 4.2 y el \(-1\) retira la constante \(+A\) que `eq_one` y los dos bucles tradicionales no escriben en \(Q\). En GPS, \(\rho(0)=\rho(N+1)=0\) y \(\rho(a)=a\) en el resto de los nodos; \(\lambda=A\).

Formulación tradicional:

```latex
\[
H_T=\sum_{i\neq j}\sum_{p=0}^{n-1} d_{ij}\,x_{i,p}\,x_{j,(p+1)\bmod n}
+A\sum_{i=0}^{n-1}\left[\left(\sum_{p=0}^{n-1}x_{i,p}-1\right)^{2}-1\right]
+A\sum_{p=0}^{n-1}\left[\left(\sum_{i=0}^{n-1}x_{i,p}-1\right)^{2}-1\right].
\]
```

Formulación GPS. \(\mathcal{P}\) es el conjunto de pares ordenados \((i,j)\) con \(i,j\in\{0,\ldots,N+1\}\), \(i\neq j\) y \(\{i,j\}\neq\{0,N+1\}\).

```latex
\[
\begin{aligned}
H_{\mathrm{GPS}}={}&
\sum_{(i,j)\in\mathcal{P}} d_{\rho(i)\rho(j)}\,x_{ij}^{1}\\
&+A\sum_{(i,j)\in\mathcal{P}}
\left[\left(\sum_{r=0}^{2}x_{ij}^{r}-1\right)^{2}-1\right]\\
&+A\sum_{i=0}^{N}
\left[\left(\sum_{j:\,(i,j)\in\mathcal{P}}x_{ij}^{1}-1\right)^{2}-1\right]\\
&+A\sum_{j=1}^{N+1}
\left[\left(\sum_{i:\,(i,j)\in\mathcal{P}}x_{ij}^{1}-1\right)^{2}-1\right]\\
&+A\sum_{\substack{0\le i<j\le N+1\\\{i,j\}\neq\{0,N+1\}}}
\left[\left(x_{ij}^{2}+x_{ji}^{2}-1\right)^{2}-1\right]\\
&+\lambda\sum_{\substack{i,j,k\in\{1,\ldots,N\}\\i,j,k\ \text{distintos}}}
\left(x_{ji}^{2}x_{kj}^{2}-x_{ji}^{2}x_{ki}^{2}-x_{kj}^{2}x_{ki}^{2}+x_{ki}^{2}\right).
\end{aligned}
\]
```

## (C) Tablas y códigos

**Tabla 4.4**

*Variables y restricciones por formulación*

| \(n\) | Variables tradicional \(n^2\) | Igualdades tradicional \(2n\) | Variables GPS \(3(n-1)(n+2)\) | Igualdades GPS \((3n^2+7n-6)/2\) | Transitividad GPS \((n-1)(n-2)(n-3)\) |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 9 | 6 | 30 | 21 | 0 |
| 4 | 16 | 8 | 54 | 35 | 6 |
| 5 | 25 | 10 | 84 | 52 | 24 |
| 6 | 36 | 12 | 120 | 72 | 60 |

*Nota.* Las igualdades de GPS son las llamadas a `eq_one`: un estado por par, salida, entrada y orden. La transitividad cuenta las ternas distintas de \(\{1,\ldots,N\}\), cada una con un polinomio de peso \(\lambda\). `qubo_variable_count` devolvería 36, 60, 90 y 126 variables GPS; esa función no construye \(Q\).

**Tabla 4.5**

*Estructura de la matriz \(Q\)*

| Instancia | Formulación | Variables | Términos lineales no nulos | Términos cuadráticos no nulos | Densidad (%) | Grado medio |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| synth03 | Tradicional | 9 | 9 | 36 | 100,00 | 8,00 |
| synth03 | GPS | 30 | 30 | 45 | 10,34 | 3,00 |
| synth04 | Tradicional | 16 | 16 | 96 | 80,00 | 12,00 |
| synth04 | GPS | 54 | 54 | 108 | 7,55 | 4,00 |
| synth05 | Tradicional | 25 | 25 | 200 | 66,67 | 16,00 |
| synth05 | GPS | 84 | 72 | 222 | 6,37 | 5,29 |

*Nota.* Se simetriza \(S=(Q+Q^{\mathsf T})/2\) y se descarta toda entrada con valor absoluto menor o igual que \(10^{-9}\). Un término lineal es una diagonal no nula. Un término cuadrático es un par \(i<j\) con \(S_{ij}\neq 0\). La densidad es el porcentaje de elementos fuera de la diagonal de \(S\) que resultan no nulos; en una matriz simétrica coincide con el porcentaje de pares que interaccionan. El grado medio es el doble de los términos cuadráticos dividido por el número de variables.

**Código 4.2.** Formulación tradicional: `formulations.py`, líneas 10–40 (`build_traditional_qubo`).

**Código 4.3.** Formulación GPS: `formulations.py`, líneas 43–116 (`build_gps_qubo`, incluidos el peso, los pares, el índice de variables y los seis bloques).

## (D) Evidencia

Cada afirmación del apartado queda ligada a una línea del código o a una salida calculada en esta sesión. El intérprete fue `.venv/bin/python`. Las matrices salieron de `load_instance` (`synthetic_instances.py`). Umbral de «no nulo»: \(10^{-9}\), salvo los doce ceros de synth05, que son \(0{,}0\) exacto.

**Peso y formulación tradicional**

- \(A=2\cdot\sum_{i\neq j}d_{ij}\). `_default_penalty` devuelve `float(np.sum(dist_matrix))*2.0` (`formulations.py:6-7`). La diagonal de la instancia es nula (`synthetic_instances.py`, construcción de \(D\)), así que `np.sum` recorre las entradas \(i\neq j\). Para synth03, synth04 y synth05 el valor coincide con el de la Tabla 4.X de la etapa anterior: 780,648215; 1 249,678504; 2 313,640588.
- Índice \(i\cdot n+p\): `formulations.py:16-17`. Orden de \(Q\): `formulations.py:14`.
- Costo \(d_{ij}\,x_{i,p}\,x_{j,(p+1)\bmod n}\), una sola escritura y sin otro factor: `formulations.py:19-24`.
- Penalización por ciudad, diagonal \(-A\) y pareja \(+A\): `formulations.py:26-31`. Penalización por posición: `formulations.py:33-38`. Con \(x^2=x\), ese patrón es \(A(\sum x-1)^2-A\). Hay un bucle de longitud \(n\) por familia, luego \(2n\) restricciones.
- Ambas funciones toman ese \(A\) si no se pasa otro peso (`formulations.py:13` y `:52`). Ninguna llamada del repositorio pasa `penalty` ni `lam`: `run_aws_full.py:200-215`, `qaoa_experiment.py:119-121`, `run_gps_n3_cloud.py:101-102`, `validate_formulations.py:55,63,72,91`, `statistical_analysis_v2.py:146,154`, `figuras_tesis.py:123-124`, `pipeline_figura.py:89-90`.

**GPS: nodos, pares, \(r\), bloques y \(\lambda\)**

- \(N=n-1\), nodos \(0,\ldots,N+1\): `formulations.py:50-51`. Depósito duplicado: `real_city` devuelve 0 si el índice es 0 o \(N+1\) (`formulations.py:55-56`); la distancia usa esa ciudad (`formulations.py:58-59`).
- Pares: \(i\neq j\) y el conjunto \(\{i,j\}\) distinto de \(\{0,N+1\}\) (`formulations.py:61-62`). El comentario de la exclusión está en `formulations.py:45`.
- Índice: los pares en ese orden y, dentro de cada par, \(r=0,1,2\) (`formulations.py:63-64`). Variables: \(3\) por par. Conteos ejecutados: 10, 18, 28 y 40 pares para \(n=3,4,5,6\), luego 30, 54, 84 y 120 variables. La fórmula \(3(n-1)(n+2)\) da los mismos cuatro números. `qubo_variable_count` usa \(3(N+2)(N+1)=3n(n+1)\) (`formulations.py:149-154`) y solo se imprime en `formulations.py:157-159`. Búsqueda de esa función en los `.py` del repositorio: esas dos citas y la copia de `datos_tesis/scripts/formulations.py`.
- \(r=1\) en el costo: `formulations.py:84-85`, coeficiente \(d(i,j)\) sobre la diagonal (`lin`, líneas 67-68). \(r=1\) en salida: `formulations.py:90-93`. \(r=1\) en entrada: `formulations.py:95-98`.
- \(r=0\) y \(r=2\) juntos, y solo ahí junto con \(r=1\), en el un estado por par: `formulations.py:87-88`.
- \(r=2\) en el orden, pares \(i<j\) salvo \(\{0,N+1\}\): `formulations.py:100-103`.
- \(r=2\) en la transitividad, índices distintos de 1 a \(N\): productos \(x_{ji}^{2}x_{kj}^{2}\), \(-x_{ji}^{2}x_{ki}^{2}\), \(-x_{kj}^{2}x_{ki}^{2}\) y término lineal \(+x_{ki}^{2}\), peso `lam_val` (`formulations.py:105-114`). `quad` reparte el coeficiente por mitades en las dos entradas (`formulations.py:70-75`), de modo que \(x^{\mathsf T}Qx\) recupera el monomio completo.
- \(\lambda=A\): `lam_val = lam if lam is not None else A` (`formulations.py:53`). No hay otra asignación en las ejecuciones listadas arriba.
- Rótulos de la figura: `extras_tesis.py:155`. Ecuaciones dibujadas, con el cuadrado y sin restar la constante: `extras_tesis.py:168-176`. La figura se guarda como `fig13_formulaciones.png` (`extras_tesis.py:179-209`).
- `eq_one` escribe \(-w\) en cada diagonal y \(2w\) repartido en cada pareja (`formulations.py:77-82`), que es \(w(\sum x-1)^2-w\) para bits.

**Conteos frente a las fórmulas**

Ejecución de los mismos bucles para \(n=3,4,5,6\):

| \(n\) | Pares | Salida | Entrada | Orden | Igualdades | Fórmula | Ternas | Fórmula | Variables | `qubo_variable_count` |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 3 | 10 | 3 | 3 | 5 | 21 | 21 | 0 | 0 | 30 | 36 |
| 4 | 18 | 4 | 4 | 9 | 35 | 35 | 6 | 6 | 54 | 60 |
| 5 | 28 | 5 | 5 | 14 | 52 | 52 | 24 | 24 | 84 | 90 |
| 6 | 40 | 6 | 6 | 20 | 72 | 72 | 60 | 60 | 120 | 126 |

La fórmula de igualdades está escrita en `figuras_tesis.py:299-309`. La tradicional es \(2n\): 6, 8, 10 y 12. Variables tradicionales \(n^2\): 9, 16, 25 y 36, leídas de `Q.shape` al construir synth03–synth05 y de la fórmula para \(n=6\).

**Estructura de \(Q\)**

Salida del cálculo sobre \(S=(Q+Q^{\mathsf T})/2\):

| Instancia | Formulación | Variables | Lineales | Cuadráticos | Densidad (%) | Grado |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| synth03 | Tradicional | 9 | 9 | 36 | 100,000000 | 8,000000 |
| synth03 | GPS | 30 | 30 | 45 | 10,344828 | 3,000000 |
| synth04 | Tradicional | 16 | 16 | 96 | 80,000000 | 12,000000 |
| synth04 | GPS | 54 | 54 | 108 | 7,547170 | 4,000000 |
| synth05 | Tradicional | 25 | 25 | 200 | 66,666667 | 16,000000 |
| synth05 | GPS | 84 | 72 | 222 | 6,368330 | 5,285714 |

Ninguna fila de \(S\) quedó en cero (`zero_rows = 0` en las seis matrices). La Tabla 4.5 redondea la densidad a dos decimales y el grado de synth05-GPS a 5,29.

**Cancelación en \(n=5\)**

- Doce diagonales exactas en cero, todas ellas \(x_{ij}^{2}\) con \(i,j\in\{1,2,3,4\}\). Hay \(4\cdot 3=12\) de esas variables. Las otras dieciséis variables de estado 2, las que tocan el depósito, tienen diagonal \(-4\,627{,}281175=-2A\).
- Para el par \((1,2)\), el bucle de transitividad lo usa como \(v_{ki}\) exactamente dos veces, y \(N-2=2\). Diagonal esperada: \(-A-A+A\cdot 2=0\). El cálculo dio 0,0.
- En synth03 (\(N=2\)) las dos variables intermedias de estado 2 tienen diagonal \(-1\,561{,}296430=-2A\). En synth04 (\(N=3\)) las seis tienen diagonal \(-1\,249{,}678504=-A\). Ahí el aporte de transitividad es \(\lambda(N-2)=0\) y \(\lambda\), y no cancela los dos \(-A\).

**Energía óptima de synth03**

- Costo óptimo, ciudad 0 fija: 195,16205375718332 en los dos sentidos, \((0,1,2)\) y \((0,2,1)\). \(A=780{,}6482150287335\).
- `optimum_energy("traditional", dist)` (`statistical_analysis_v2.py:142-169`) devolvió \(-4\,488{,}727236415218\). El costo menos \(6A\) es \(-4\,488{,}727236415217\).
- `optimum_energy("gps", dist)` devolvió \(-16\,198{,}45046184622\). El costo menos \(21A\) es \(-16\,198{,}450461846216\). Para \(n=3\) hay 10 pares, por debajo del corte de 12 pares de esa función (`statistical_analysis_v2.py:156-158`), así que la enumeración sí se ejecuta. Cada candidato exige `decode_gps_solution` (`formulations.py:119-146`) y `gps_violations` (`statistical_analysis_v2.py:115-135`).
- Una codificación factible del recorrido óptimo, comprobada con `gps_violations` vacía, reproduce esa energía. En \(n=3\) el bucle de transitividad no itera. Cada `eq_one` satisfecha aporta \(-A\), y hay 21.
- La decodificación tradicional del análisis, distinta de la del script de validación, está en `statistical_analysis_v2.py:107-112`.

**Salida completa de `validate_formulations.py`**

```
--- Traditional (n=4, brute force) ---
real=196.3285 obtained=196.32849620562484 match=True

--- GPS n=2 (brute force) ---
tour=[0, 1] cost=84.6 (real=84.6)

--- GPS n=3 (enumeration over r-assignments, 3^12) ---
real=195.1621 obtained=195.16205375718334 match=True

--- Anti-cycle constraint (eq. 13), N=3 ---
consistent order=-49376.5194 cyclic order=-42288.1852 penalizes_correctly=True
```

Qué instancia usa cada bloque:

- Tradicional, líneas 52–59: `random_instance(4, seed=42)`. Esa función repite el generador de la etapa 1 (`validate_formulations.py:40-48`). `np.allclose` contra `load_instance("synth04")` dio verdadero. Cuatro ciudades.
- GPS de dos ciudades, líneas 61–67: matriz fija `[[0, 42.3], [42.3, 0]]`. No es una instancia synth. El óptimo de ida y vuelta es 84,6.
- GPS del rótulo «n=3», líneas 69–87: `random_instance(3, seed=42)`. `np.allclose` contra `load_instance("synth03")` dio verdadero. El número de ciudades es 3 (\(N=2\), cuatro nodos aumentados). Los pares ordenados del propio bucle son 10, así que el producto recorre \(3^{10}\) asignaciones. El texto impreso dice \(3^{12}\) (`validate_formulations.py:69`).
- Orden, líneas 89–114: `random_instance(4, seed=5)`. `np.allclose` contra synth04 dio falso. Cuatro ciudades, semilla distinta de la del estudio. Compara dos asignaciones escritas a mano; no llama a `gps_violations`.
- El script no contiene `assert`. Con `match=False` también terminaría e imprimiría el fallo. En esta ejecución los tres `match` y `penalizes_correctly` salieron verdaderos, código de salida 0.

## Pendientes

**[VERIFICAR]**

- Correspondencia de los bloques y de los rótulos \(r=0,1,2\) con las ecuaciones 8–13 de González-Bermejo, Alonso-Linaje y Atchade-Adelomou (2022). El módulo las cita en `formulations.py:1` y el cuarto bloque de la validación rotula la prueba como «eq. 13»; este apartado no abrió el PDF.

**[CITA]**

- Formulación QUBO one-hot del vendedor viajero. El encabezado de `formulations.py:1` remite a Lucas (2014). En el repositorio no está la ficha bibliográfica.

**[DECISIÓN DE LA AUTORA]**

- Excluir el par \(\{0, N+1\}\) de la lista de variables (`formulations.py:45`, `formulations.py:61-62`).
- Fijar \(\lambda=A\) y no pasar otro valor en las ejecuciones (`formulations.py:53`).
- Usar el mismo \(A=2\cdot\sum_{i\neq j}d_{ij}\) en las dos formulaciones para que la brecha \((E-E_{\mathrm{opt}})/A\) comparta escala.
- No escribir en \(Q\) la constante \(+A\) de cada restricción de igualdad. La Figura 4.2 dibuja el cuadrado completo (`extras_tesis.py:168-176`).
- Rótulos de la Figura 4.2 —arco directo, precedencia no adyacente, orden inverso— en `extras_tesis.py:155`, además del papel que cada \(r\) tiene en los bloques.
