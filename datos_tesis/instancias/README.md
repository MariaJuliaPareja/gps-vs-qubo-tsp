# Datos de entrada: instancias sintéticas del TSP

Paquete de datos de entrada de la tesis. Reúne cuatro instancias sintéticas del problema del agente viajero, de 3 a 6 ciudades, y el script que las genera. Se usan para comparar dos formulaciones QUBO del TSP, GPS y QUBO tradicional, resueltas con QAOA. Cada instancia aporta un archivo de coordenadas y uno de distancias. Los archivos están en `datos_tesis/generador/` y `datos_tesis/instancias/`.

## Contenido

| Archivo | Instancia | Ciudades | Descripción |
|---|---|---|---|
| `generador/synthetic_instances.py` | synth03 a synth06 | 3 a 6 | Genera coordenadas y distancias con semilla fija. |
| `instancias/synth03_coords.csv` | synth03 | 3 | Coordenadas de las ciudades 0, 1 y 2. |
| `instancias/synth03_dist.csv` | synth03 | 3 | Matriz de distancias 3×3. |
| `instancias/synth04_coords.csv` | synth04 | 4 | Coordenadas de las ciudades 0 a 3. |
| `instancias/synth04_dist.csv` | synth04 | 4 | Matriz de distancias 4×4. |
| `instancias/synth05_coords.csv` | synth05 | 5 | Coordenadas de las ciudades 0 a 4. |
| `instancias/synth05_dist.csv` | synth05 | 5 | Matriz de distancias 5×5. |
| `instancias/synth06_coords.csv` | synth06 | 6 | Coordenadas de las ciudades 0 a 5. |
| `instancias/synth06_dist.csv` | synth06 | 6 | Matriz de distancias 6×6. |

Las rutas de la tabla son relativas a `datos_tesis/`.

## Formato de los archivos

`*_coords.csv` es un CSV con encabezado `ciudad,x,y`. Cada fila siguiente es una ciudad: índice entero en `ciudad`, desde 0 hasta n−1, y las coordenadas `x` e `y`. El separador es la coma y el punto es el separador decimal.

`*_dist.csv` es la matriz de distancias n×n. La primera fila empieza por una celda vacía y sigue con los índices de ciudad, que encabezan las columnas. Cada fila de datos empieza por el índice de esa ciudad y continúa con n distancias. Esos índices son los mismos de la columna `ciudad`. El bloque numérico es simétrico y la diagonal es 0; en los cuatro archivos la diferencia con la traspuesta es 0.

## Cómo se generaron

`synthetic_instances.py` fija `BASE_SEED = 42`. `generate_instance` crea `numpy.random.default_rng` con esa semilla, toma n pares uniformes en el cuadrado [0, 100) × [0, 100) y calcula la distancia euclidiana con `numpy.linalg.norm`. La matriz nace en cero y solo se rellenan las entradas i ≠ j, así que queda simétrica y con diagonal nula. Los ocho CSV coinciden exactamente con esa salida para n = 3, 4, 5 y 6.

Desde `generador/`:

```bash
python synthetic_instances.py
```

El comando recalcula las cuatro instancias e imprime el nombre, el número de ciudades y la suma de la matriz de distancias. No escribe los CSV. [COMPLETAR: paso que exporta `instancias/*_coords.csv` e `instancias/*_dist.csv` en el formato descrito arriba.]

Entorno en el que se contrastaron los CSV con el generador: Python 3.14.7 y NumPy 2.4.3.

## Estructura anidada

Las cuatro instancias comparten la semilla 42. Cada llamada abre un generador nuevo y consume los primeros 2n números, de modo que las ciudades de una instancia son el prefijo de la siguiente. Sobre los CSV, coordenadas y submatriz principal de distancias coinciden de forma exacta:

- synth04 contiene las tres ciudades de synth03 y añade la ciudad 3;
- synth05 contiene synth04 y añade la ciudad 4;
- synth06 contiene synth05 y añade la ciudad 5.

No son muestras independientes.

## Por qué no se usa TSPLIB

Las instancias de TSPLIB no son simulables clásicamente a la escala que requieren. La simulación exacta (statevector) ocupa memoria proporcional a 2 elevado al número de qubits. La más pequeña considerada, burma14 (14 nodos), necesita 196 qubits bajo QUBO tradicional, por encima del límite práctico de unos 50 qubits, incluso en supercomputadoras (Boixo et al., 2018; Doi y Horii, 2020). En su lugar se usan estas instancias, de n = 3 a 6, con semilla fija. El criterio coincide con la sección «Por qué no se usa TSPLIB» del README del repositorio.

## Exclusiones

synth06 no se utilizó en el análisis final. Se excluyó por el límite de memoria: con seis ciudades la simulación clásica exacta deja de ser viable, porque la memoria del statevector crece como 2 elevado al número de qubits. El archivo se conserva en el paquete, ya que el generador produce la serie completa de n = 3 a 6.

## Autoría

María Julia Pareja Abarca, Escuela Profesional de Ingeniería de Sistemas, Universidad Católica de Santa María, 2026.
