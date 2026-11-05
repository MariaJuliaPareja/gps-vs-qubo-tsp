# 4.1.1 Etapa 1: Generación de instancias

## (A) Texto del apartado

La primera etapa construye las instancias del problema del agente viajero sobre las que después se comparan el QUBO Tradicional y la formulación GPS. No se emplearon ejemplares de TSPLIB. La instancia más pequeña considerada en el proyecto, burma14, tiene 14 ciudades: el QUBO Tradicional, de n² variables, exigiría 196 qubits, y GPS, cuyo conteo en esta implementación es 3(n−1)(n+2), exigiría 624. Un vector de estado de q qubits ocupa 2^q · 16 bytes. Con 31 GB de memoria, ese criterio admite a lo sumo 30 qubits, de modo que burma14 queda fuera del alcance de la simulación. Las instancias de trabajo son, por ello, sintéticas y de tres, cuatro y cinco ciudades. El procedimiento que las produce se muestra en el Código 4.X. [DECISIÓN DE LA AUTORA: explicar si, además del límite de memoria, hubo otro motivo para descartar TSPLIB.]

Cada instancia se obtiene con el generador `default_rng` de NumPy, iniciado siempre con la semilla 42. Las coordenadas salen de una distribución uniforme en el cuadrado [0, 100)²: el generador entrega valores en [0, 1) y el código los multiplica por 100. La distancia entre dos ciudades distintas es la euclidiana, calculada con la norma del vector que las separa. La matriz nace en ceros y solo se rellenan las entradas fuera de la diagonal, así que la diagonal es nula. La norma es simétrica, y la matriz de distancias también lo es. [DECISIÓN DE LA AUTORA: explicar por qué se fijaron la semilla 42 y el cuadrado [0, 100)².]

Las tres instancias comparten esa semilla y, en cada llamada, el generador se abre de nuevo. La instancia de n ciudades consume los primeros 2n números aleatorios, de modo que sus ciudades son el prefijo de las de la instancia de n + 1. Se comprobó que las coordenadas y la submatriz principal de synth03 coinciden con las tres primeras ciudades de synth04, y que synth04 queda contenido del mismo modo en synth05. Aumentar n agrega ciudades y no modifica las anteriores. Las instancias no son muestras independientes entre tamaños. [DECISIÓN DE LA AUTORA: explicar por qué se prefirió este anidamiento frente a una semilla distinta para cada tamaño.]

El costo óptimo de cada instancia se obtiene por enumeración de recorridos. El procedimiento fija la ciudad 0 como inicio y recorre las permutaciones de las ciudades restantes, es decir (n−1)! secuencias, y conserva el ciclo de menor costo. Como la matriz es simétrica, un recorrido y su inverso tienen el mismo costo, y el número de recorridos no dirigidos distintos es (n−1)!/2: uno para n = 3, tres para n = 4 y doce para n = 5. En n = 5 la enumeración inspecciona 24 secuencias, así que el óptimo exacto es calculable de forma exhaustiva. Los valores quedan en la Tabla 4.X. En los tres casos el inverso del recorrido también alcanza ese costo.

Las matrices no se leen desde archivo durante la corrida: cada ejecución vuelve a llamar al generador y las construye en memoria. El generador define además synth06, de seis ciudades. El script de producción ejecuta synth03 en ambas formulaciones y, solo si se activa la opción de escalamiento, synth04, synth05 y synth06 en el QUBO Tradicional. Sin esa opción, synth06 no entra en la corrida. En los resultados archivados no hay archivos de synth06, y el paquete de instancias indica que no se usó en el análisis final. [VERIFICAR: que la línea de comando de la EC2 no haya incluido synth06 mediante la opción de escalamiento; esa línea no está guardada en el repositorio.]

## (B) Tabla

**Tabla 4.X**

*Características de las instancias sintéticas*

| Instancia | n | Recorridos distintos | Recorrido óptimo | Costo óptimo | Σ de todas las entradas de D | A |
| --- | ---: | ---: | --- | ---: | ---: | ---: |
| synth03 | 3 | 1 | 0–1–2–0 (inverso 0–2–1–0) | 195.1621 | 390.3241 | 780.6482 |
| synth04 | 4 | 3 | 0–1–3–2–0 (inverso 0–2–3–1–0) | 196.3285 | 624.8393 | 1249.6785 |
| synth05 | 5 | 12 | 0–1–3–2–4–0 (inverso 0–4–2–3–1–0) | 226.9425 | 1156.8203 | 2313.6406 |

*Nota.* «Recorridos distintos» es (n−1)!/2. El enumerador del costo óptimo visita las (n−1)! secuencias que empiezan en la ciudad 0; la simetría de D identifica cada recorrido con su inverso. Σ es `np.sum(D)`, esto es, las n² entradas, diagonal nula incluida. Por la simetría equivale a 2·Σ_{i<j} d_{ij}. El peso A de `_default_penalty` es 2·Σ, no 2·Σ_{i<j}. Las ciudades se numeran desde 0, como en el generador.

Coordenadas a dos decimales, en el orden de ciudad 0 en adelante. synth03: (77.40, 43.89), (85.86, 69.74), (9.42, 97.56). synth04 añade (76.11, 78.61). synth05 añade (12.81, 45.04).

Matrices de distancias a dos decimales, con la diagonal en cero.

synth03:

|  | 0 | 1 | 2 |
| --- | ---: | ---: | ---: |
| 0 | 0.00 | 27.20 | 86.61 |
| 1 | 27.20 | 0.00 | 81.35 |
| 2 | 86.61 | 81.35 | 0.00 |

synth04:

|  | 0 | 1 | 2 | 3 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 0.00 | 27.20 | 86.61 | 34.74 |
| 1 | 27.20 | 0.00 | 81.35 | 13.18 |
| 2 | 86.61 | 81.35 | 0.00 | 69.34 |
| 3 | 34.74 | 13.18 | 69.34 | 0.00 |

synth05:

|  | 0 | 1 | 2 | 3 | 4 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 0.00 | 27.20 | 86.61 | 34.74 | 64.59 |
| 1 | 27.20 | 0.00 | 81.35 | 13.18 | 77.11 |
| 2 | 86.61 | 81.35 | 0.00 | 69.34 | 52.63 |
| 3 | 34.74 | 13.18 | 69.34 | 0.00 | 71.65 |
| 4 | 64.59 | 77.11 | 52.63 | 71.65 | 0.00 |

**Código 4.X.** Función generadora: `synthetic_instances.py`, líneas 15-23. La semilla por defecto está en la línea 12 y el catálogo synth03–synth06, en las líneas 5-10.

```python
def generate_instance(n: int, seed: int = BASE_SEED):
    rng = np.random.default_rng(seed)
    coords = rng.random((n, 2)) * 100
    dist = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                dist[i, j] = np.linalg.norm(coords[i] - coords[j])
    return dist, coords
```

## (C) Evidencia

Las instancias de trabajo son sintéticas, de n = 3, 4 y 5, y el generador también define n = 6 (`synthetic_instances.py:5-10`). La semilla por defecto es 42 (`synthetic_instances.py:12`, `synthetic_instances.py:15`). `load_instance` no pasa otra semilla (`synthetic_instances.py:26-29`).

El generador es `np.random.default_rng`. Las coordenadas son `rng.random((n, 2)) * 100`, uniformes en [0, 100)² (`synthetic_instances.py:16-17`). La matriz parte de ceros y la distancia euclidiana solo se escribe si i ≠ j (`synthetic_instances.py:18-22`). La simetría no está impuesta por una asignación extra: se sigue de que la norma de u − v es la de v − u. La comprobación numérica dio matrices simétricas y diagonal nula en las tres instancias.

El anidamiento se sigue de abrir un generador nuevo con la misma semilla en cada llamada (`synthetic_instances.py:16`): la instancia de n + 1 repite los primeros 2n uniformes y añade dos más. La comparación directa de arreglos confirmó que las coordenadas y la submatriz principal de synth03 son las de synth04, y las de synth04 son las de synth05.

El costo óptimo del recorrido está en `costo_optimo`: mínimo sobre `([0] + permutación)` de `range(1, n)`, con cierre `(i + 1) % n` (`figuras_tesis.py:321-324`). Eso es (n−1)! secuencias, no (n−1)!/2. El conteo de recorridos distintos de la tabla es la identificación de cada ciclo con su inverso, válida porque D es simétrica; esa división no está escrita en el código. La enumeración de esta corrida encontró dos secuencias de igual costo mínimo en cada instancia, una inversa de la otra. Los costos sin redondear son 195.1620537572, 196.3284962056 y 226.9424609130.

`statistical_analysis_v2.py:148-152` no calcula ese costo de recorrido ni fija la ciudad 0. Recorre `itertools.permutations(range(n))`, es decir n! asignaciones, y minimiza la energía del QUBO Tradicional. No debe citarse como el enumerador del costo óptimo de la Tabla 4.X.

`_default_penalty` devuelve `float(np.sum(dist_matrix)) * 2.0` (`formulations.py:6-7`). `np.sum` suma las n² entradas. Con diagonal nula y simetría, esa suma es 2·Σ_{i<j} d_{ij}, y A resulta 4·Σ_{i<j} d_{ij}. Los valores sin redondear de la suma completa y de A son, para synth03, 390.3241075144 y 780.6482150287; para synth04, 624.8392517643 y 1249.6785035286; para synth05, 1156.8202937533 y 2313.6405875067.

La corrida llama a `load_instance`, que regenera la matriz en memoria (`run_aws_full.py:197`, `run_aws_full.py:214`, `synthetic_instances.py:29`). El bloque que escribe CSV solo corre si el generador se ejecuta como programa (`synthetic_instances.py:32-37`). Los scripts de QAOA no leen esos CSV.

Sin la opción `--include_scale`, `main` solo llama a synth03 (`run_aws_full.py:197-204`). Con esa opción, el defecto de `--scale_instances` es `synth04,synth05,synth06` y solo se resuelve el QUBO Tradicional (`run_aws_full.py:180-186`, `run_aws_full.py:207-216`). No hay ningún JSON de synth06 en el repositorio. `datos_tesis/instancias/README.md:57` dice que synth06 no se utilizó en el análisis final. La línea de comando real no está en el repositorio.

burma14 y los 196 qubits del QUBO Tradicional están en `readme.md:267`. El 624 no está escrito como literal: sale de `3 * (n - 1) * (n + 2)` con n = 14 (`extras_tesis.py:27`), esto es 3·13·16. El tope de 30 qubits está en `readme.md:269`: 2^q · 16 bytes ≤ 31 GB implica q ≤ 30. El mismo tope se calcula en `extras_tesis.py:17-18` con `RAM_GB = 31`.

## Pendientes

1. [DECISIÓN DE LA AUTORA: explicar si, además del límite de memoria, hubo otro motivo para descartar TSPLIB.]
2. [DECISIÓN DE LA AUTORA: explicar por qué se fijaron la semilla 42 y el cuadrado [0, 100)².]
3. [DECISIÓN DE LA AUTORA: explicar por qué se prefirió este anidamiento frente a una semilla distinta para cada tamaño.]
4. [VERIFICAR: que la línea de comando de la EC2 no haya incluido synth06 mediante la opción de escalamiento; esa línea no está guardada en el repositorio.]
