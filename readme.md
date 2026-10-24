# Efficiency of the Positional Matrix Formulation Versus Unconstrained Quadratic Binary Optimization in Hybrid Quantum Computing

María Julia Pareja Abarca. Undergraduate thesis, School of Systems Engineering, Universidad Católica de Santa María, 2026.

[English](#english) · [Português](#português) · [Español](#español)

## English

This repository compares two QUBO formulations of the traveling salesman problem, GPS and traditional one-hot QUBO, solved with QAOA on a classical statevector simulator. The instances are synthetic, from 3 to 6 cities, with a fixed seed.

The production comparison is synth03, both formulations, on the same machine. Traditional QUBO is also run at n = 4 and n = 5 for the scalability trend. GPS at n > 3 is not simulated. The file-level inventory of the synth03 production runs is in [`datos_tesis/README.md`](datos_tesis/README.md). The instances are described in [`datos_tesis/instancias/README.md`](datos_tesis/instancias/README.md).

### What is in the repository

```
formulations.py              both Q matrices
synthetic_instances.py       instances, seed 42; writes the CSV in this folder
validate_formulations.py     check against brute force and exhaustive enumeration
qaoa_experiment.py           local QAOA run
run_aws_full.py              QAOA run used on EC2
run_gps_n3_cloud.py          synth03, both formulations, one machine
statistical_analysis.py      first analysis plan: Shapiro-Wilk, Wilcoxon, correlation, LOWESS
statistical_analysis_v2.py   analysis used for the thesis
recursos_circuito.py         circuit resources, without simulating the statevector
figuras_tesis.py             figures 01–10 and the result tables
pipeline_figura.py           figure 11, the experimental pipeline
extras_tesis.py              requirements, formulation sheet, one-hot vs GPS animation
datos_tesis/                 production package for synth03
results_aws_final/           synth03, and Traditional at synth04 and synth05
figuras/                     figures and tables, in es/ and en/
recursos_circuito.csv        resource counts for n = 3..6
```

### Formulations

Traditional QUBO places city i at position p. The variable is x_{i,p}. There are n² variables (Lucas, 2014, one-hot). The baseline cited in the thesis, Montañez-Barrera et al. (2024), is DFJ. DFJ carries an exponential number of subtour constraints, and those authors only tested TSP up to 7 cities. The one-hot of n² is the baseline that fits this simulation. That is a scope decision.

GPS follows González-Bermejo et al. (2022), equations 8–13, as implemented in `build_gps_qubo`. N = n − 1. The augmented nodes are 0, …, N+1: 0 is the departure depot and N+1 is the arrival depot. The pair {0, N+1} is excluded. It is a depot-to-depot edge, its cost is zero, and the paper’s constraints do not forbid it. Each remaining pair has three states. r = 1 is the direct arc i → j, r = 0 means i comes before j and the cities are not adjacent, r = 2 means i comes after j. The variable count of this implementation is 3(n−1)(n+2).

| n | Traditional | GPS |
|---|---|---|
| 3 | 9 | 30 |
| 4 | 16 | 54 |
| 5 | 25 | 84 |
| 6 | 36 | 120 |

The default penalty is A = 2 · Σ d_{ij}. The transitivity weight defaults to λ = A. On a binary variable, x_i² = x_i, so a linear term lives on the diagonal of Q. GPS equality constraints, counted from `build_gps_qubo`, are (3n² + 7n − 6)/2. For n = 3 that is 21. Transitivity penalties are (n−1)(n−2)(n−3). Traditional has 2n constraints: each city once, and each position once.

In the original paper the advantage of GPS is against the native formulation (n³) and against MTZ, not against one-hot. Against one-hot, GPS uses more variables by the factor above.

### Instances

`BASE_SEED = 42`. Coordinates are uniform in the square [0, 100) × [0, 100). The distance is Euclidean, the matrix is symmetric, and the diagonal is zero. The four sizes share that seed. Each call opens a new generator and consumes the first 2n numbers, so the cities of one instance are the prefix of the next. They are not independent samples. synth04 contains synth03 and adds city 3, and the same holds up to synth06.

TSPLIB is not used. An exact statevector takes 2^q · 16 bytes, where q is the number of qubits. The smallest TSPLIB instance considered, burma14, needs 196 qubits under traditional QUBO. That is past the practical simulation limit of about 50 qubits (Boixo et al., 2018; Doi and Horii, 2020).

On the machine used for the figures, 31 GB of RAM, the statevector fits while 2^q · 16 B ≤ 31 GB, so q ≤ 30. GPS at n = 3 has 30 qubits: 16 GB. Traditional at n = 5 has 25 qubits. Traditional at n = 6 has 36 qubits, about 1 TB. GPS at n = 4 has 54 qubits. Those last two are not simulated here.

### Runs

The AWS scripts use COBYLA, `--reps 2`, and `--maxiter 30`. `qaoa_experiment.py` defaults to `--reps 2`, `--replicas 5`, `--maxiter 50`, and CPU. A JSON does not store the optimizer, `maxiter`, or the number of layers. Where the log prints `eval N/~30`, the iteration cap of that batch is 30. The defaults in the scripts do not replace a value the log does not print. The command line of the production batches is not in the logs. What the logs and the JSON do establish is written in [`datos_tesis/README.md`](datos_tesis/README.md).

The machine is an EC2 t2.2xlarge, CPU only. The instance type is not written in the JSON. `run_aws_full.py` has no GPU option. The same machine runs both formulations of synth03, so the execution times can be compared with each other.

`results_aws_final/` holds 20 Traditional replicas of synth03 (indices 0–19), 8 of synth04, and 8 of synth05. GPS of synth03 has 17 JSON files from the batch of 19, plus one backup JSON. Replicas 1 and 2 of that batch have no JSON. Their time and objective are in the consolidated CSV, and they have no bitstring. The analysis gives the backup a new replica index when the index collides with a JSON that is already there.

QAOAAnsatz emits an instruction that Aer’s simulator does not run as a basis gate. `qaoa_experiment.py` transpiles the circuit and rebuilds each pub with `SamplerPub.coerce()`. Unpacking the pub as a plain tuple dropped the parameter values for some shapes. `run_aws_full.py` calls `decompose()` instead of transpiling against an AerSimulator backend. That backend path applies a default `coupling_map` and stops around 27–28 qubits, which is a hardware-topology limit and does not apply to a statevector. COBYLA calls the callback on every evaluation, so the evaluation count can pass `maxiter`. The value kept is `best_seen`, the minimum energy seen. If the final decode fails, the script resamples at those parameters. Qiskit stores bit 0 at the right of the bitstring, and the resample reverses it before computing xᵀ Q x.

### What the analysis compares

Raw energies are not comparable. Each QUBO has its own scale. The gap used in the thesis is (E − E_opt)/A. When the row has a bitstring, E is E_recalc = xᵀ Q x, not `objective_value`. E_opt is the minimum energy over feasible solutions of that QUBO.

`statistical_analysis_v2.py` treats the replicas as independent unless `--paired` is set: Mann-Whitney for time, Fisher for feasibility. `--paired` is only for the case where GPS and Traditional shared a seed per replica. Then the tests are Wilcoxon and McNemar. Qubits, depth, and gate count are constant inside a formulation, so they stay descriptive. Correlations pooled across formulations are not reported: they are confounded with the instance size.

synth03/gps/replica 1 is left out of the energy and of the gap. Its `objective_value` is identical to the Traditional E_opt, and that row is treated as contaminated. It stays in the time comparison. The route gap, in `figuras_tesis.py`, is the cost of the decoded tour against the brute-force optimum, and it is defined only for feasible solutions.

### Figures

`figuras_tesis.py` writes figures 01–10 and the tables under `figuras/`, in Spanish and in English. `pipeline_figura.py` writes figure 11. `extras_tesis.py` writes the requirements table, the formulation sheet, and `anim_onehot_vs_gps.gif`. `recursos_circuito.py` writes `recursos_circuito.csv` for n = 3..6, including the sizes that are not simulated. For a missing instance it builds a random Euclidean matrix. The structure of Q does not depend on the distance values.

### Reproduce

```bash
pip install numpy pandas scipy statsmodels matplotlib pillow
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

`qiskit-aer-gpu` is only for `qaoa_experiment.py --device GPU`, and it needs CUDA.

```bash
python validate_formulations.py
python synthetic_instances.py
python recursos_circuito.py
python statistical_analysis_v2.py --results-dir results_aws_final --csv results_aws_final/aws_consolidated.csv
python figuras_tesis.py
python pipeline_figura.py
python extras_tesis.py
```

`synthetic_instances.py` in this folder writes `synth0N_dist.csv` and `synth0N_coords.csv` here. `datos_tesis/generador/synthetic_instances.py` prints the name, the size, and the sum of the distance matrix. It does not write the CSV. The files in `datos_tesis/instancias/` use the format in their own README.

`run_aws_full.py` is the EC2 script. Without `--include_scale` it runs synth03 for the formulations given in `--paired_formulations` (default `traditional,gps`). `--include_scale` adds Traditional on synth04, synth05, and synth06. synth06 asks for about 1 TB and does not fit the machine used.

The CSV in `datos_tesis/instancias/` were checked against the generator with Python 3.14.7 and NumPy 2.4.3.

### References

- González-Bermejo, S., Alonso-Linaje, G., & Atchade-Adelomou, P. (2022). GPS: A new TSP formulation. arXiv:2110.12158
- Lucas, A. (2014). Ising formulations of many NP problems. *Frontiers in Physics*.
- Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization. *Quantum Science and Technology*, 9(2), 025022.
- Boixo, S. et al. (2018). Characterizing quantum supremacy in near-term devices. *Nature Physics*.

## Português

Este repositório compara duas formulações QUBO do problema do caixeiro-viajante, GPS e QUBO tradicional one-hot, resolvidas com QAOA num simulador clássico de vetor de estado. As instâncias são sintéticas, de 3 a 6 cidades, com semente fixa.

A comparação de produção é synth03, as duas formulações, na mesma máquina. O QUBO tradicional também corre em n = 4 e n = 5 para a tendência de escalabilidade. GPS com n > 3 não é simulado. O inventário arquivo a arquivo das execuções de produção de synth03 está em [`datos_tesis/README.md`](datos_tesis/README.md). As instâncias estão descritas em [`datos_tesis/instancias/README.md`](datos_tesis/instancias/README.md).

### O que está no repositório

```
formulations.py              as duas matrizes Q
synthetic_instances.py       instâncias, semente 42; escreve os CSV nesta pasta
validate_formulations.py     conferência contra força bruta e enumeração exaustiva
qaoa_experiment.py           execução local de QAOA
run_aws_full.py              execução de QAOA usada na EC2
run_gps_n3_cloud.py          synth03, as duas formulações, uma máquina
statistical_analysis.py      primeiro plano de análise: Shapiro-Wilk, Wilcoxon, correlação, LOWESS
statistical_analysis_v2.py   análise usada na tese
recursos_circuito.py         recursos do circuito, sem simular o vetor de estado
figuras_tesis.py             figuras 01–10 e as tabelas de resultados
pipeline_figura.py           figura 11, o pipeline experimental
extras_tesis.py              requisitos, folha das formulações, animação one-hot vs GPS
datos_tesis/                 pacote de produção de synth03
results_aws_final/           synth03, e Tradicional em synth04 e synth05
figuras/                     figuras e tabelas, em es/ e en/
recursos_circuito.csv        contagens de recursos para n = 3..6
```

### Formulações

O QUBO tradicional coloca a cidade i na posição p. A variável é x_{i,p}. São n² variáveis (Lucas, 2014, one-hot). A referência citada na tese para o QUBO tradicional, Montañez-Barrera et al. (2024), é DFJ. DFJ carrega um número exponencial de restrições de subciclo, e esses autores só testaram TSP até 7 cidades. O one-hot de n² é a linha de base que cabe nesta simulação. É uma decisão de alcance.

GPS segue González-Bermejo et al. (2022), equações 8–13, como está em `build_gps_qubo`. N = n − 1. Os nós aumentados são 0, …, N+1: 0 é o depósito de saída e N+1 é o depósito de chegada. O par {0, N+1} fica de fora. É uma aresta depósito–depósito, o custo é zero, e as restrições do artigo não a proíbem. Cada par restante tem três estados. r = 1 é o arco direto i → j, r = 0 significa que i vem antes de j e as cidades não são adjacentes, r = 2 significa que i vem depois de j. A contagem de variáveis desta implementação é 3(n−1)(n+2).

| n | Tradicional | GPS |
|---|---|---|
| 3 | 9 | 30 |
| 4 | 16 | 54 |
| 5 | 25 | 84 |
| 6 | 36 | 120 |

A penalidade por defeito é A = 2 · Σ d_{ij}. O peso da transitividade por defeito é λ = A. Numa variável binária, x_i² = x_i, por isso um termo linear fica na diagonal de Q. As igualdades de GPS, contadas a partir de `build_gps_qubo`, são (3n² + 7n − 6)/2. Para n = 3 são 21. As penalidades de transitividade são (n−1)(n−2)(n−3). O tradicional tem 2n restrições: cada cidade uma vez, e cada posição uma vez.

No artigo original, a vantagem de GPS é face à formulação nativa (n³) e face a MTZ, não face ao one-hot. Face ao one-hot, GPS usa mais variáveis pelo fator acima.

### Instâncias

`BASE_SEED = 42`. As coordenadas são uniformes no quadrado [0, 100) × [0, 100). A distância é euclidiana, a matriz é simétrica e a diagonal é zero. Os quatro tamanhos partilham essa semente. Cada chamada abre um gerador novo e consome os primeiros 2n números, de modo que as cidades de uma instância são o prefixo da seguinte. Não são amostras independentes. synth04 contém synth03 e acrescenta a cidade 3, e o mesmo vale até synth06.

TSPLIB não é usado. Um vetor de estado exato ocupa 2^q · 16 bytes, onde q é o número de qubits. A menor instância TSPLIB considerada, burma14, precisa de 196 qubits no QUBO tradicional. Isso passa o limite prático de simulação, cerca de 50 qubits (Boixo et al., 2018; Doi e Horii, 2020).

Na máquina usada para as figuras, 31 GB de RAM, o vetor de estado cabe enquanto 2^q · 16 B ≤ 31 GB, logo q ≤ 30. GPS em n = 3 tem 30 qubits: 16 GB. O tradicional em n = 5 tem 25 qubits. O tradicional em n = 6 tem 36 qubits, cerca de 1 TB. GPS em n = 4 tem 54 qubits. Estes dois últimos não são simulados aqui.

### Execuções

Os scripts da AWS usam COBYLA, `--reps 2` e `--maxiter 30`. `qaoa_experiment.py` usa por defeito `--reps 2`, `--replicas 5`, `--maxiter 50` e CPU. Um JSON não guarda o otimizador, `maxiter` nem o número de camadas. Onde o log imprime `eval N/~30`, o teto de iterações desse lote é 30. Os valores por defeito dos scripts não substituem um valor que o log não imprime. A linha de comando dos lotes de produção não está nos logs. O que os logs e os JSON estabelecem está em [`datos_tesis/README.md`](datos_tesis/README.md).

A máquina é uma EC2 t2.2xlarge, só CPU. O tipo de instância não está escrito nos JSON. `run_aws_full.py` não tem opção de GPU. A mesma máquina corre as duas formulações de synth03, por isso os tempos de execução podem ser comparados entre si.

`results_aws_final/` tem 20 réplicas Tradicionais de synth03 (índices 0–19), 8 de synth04 e 8 de synth05. GPS de synth03 tem 17 JSON do lote de 19, mais um JSON de reserva. As réplicas 1 e 2 desse lote não têm JSON. O tempo e o objetivo estão no CSV consolidado, e não há bitstring. A análise atribui à reserva um índice de réplica novo quando o índice colide com um JSON que já existe.

QAOAAnsatz emite uma instrução que o simulador da Aer não executa como porta de base. `qaoa_experiment.py` transpila o circuito e reconstrói cada pub com `SamplerPub.coerce()`. Desempacotar o pub como uma tupla simples perdia os valores dos parâmetros em alguns formatos. `run_aws_full.py` chama `decompose()` em vez de transpilar contra um backend AerSimulator. Esse caminho aplica um `coupling_map` por defeito e para por volta de 27–28 qubits, que é um limite de topologia de hardware e não se aplica a um vetor de estado. COBYLA chama o callback em cada avaliação, por isso a contagem de avaliações pode passar de `maxiter`. O valor que se guarda é `best_seen`, a energia mínima vista. Se a descodificação final falha, o script reamostra nesses parâmetros. O Qiskit guarda o bit 0 à direita da cadeia de bits, e a reamostragem inverte-a antes de calcular xᵀ Q x.

### O que a análise compara

Energias em bruto não são comparáveis. Cada QUBO tem a sua escala. A lacuna usada na tese é (E − E_opt)/A. Quando a linha tem bitstring, E é E_recalc = xᵀ Q x, não `objective_value`. E_opt é a energia mínima entre as soluções factíveis desse QUBO.

`statistical_analysis_v2.py` trata as réplicas como independentes, salvo com `--paired`: Mann-Whitney para o tempo, Fisher para a factibilidade. `--paired` só vale para o caso em que GPS e Tradicional partilharam uma semente por réplica. Aí os testes são Wilcoxon e McNemar. Qubits, profundidade e número de portas são constantes dentro de uma formulação, por isso ficam descritivos. Correlações agrupadas entre formulações não são reportadas: ficam confundidas com o tamanho da instância.

synth03/gps/réplica 1 fica de fora da energia e da lacuna. O `objective_value` é idêntico ao E_opt Tradicional, e essa linha é tratada como contaminada. Permanece na comparação de tempo. A lacuna de rota, em `figuras_tesis.py`, é o custo do percurso descodificado face ao ótimo por força bruta, e só está definida para soluções factíveis.

### Figuras

`figuras_tesis.py` escreve as figuras 01–10 e as tabelas em `figuras/`, em espanhol e em inglês. `pipeline_figura.py` escreve a figura 11. `extras_tesis.py` escreve a tabela de requisitos, a folha das formulações e `anim_onehot_vs_gps.gif`. `recursos_circuito.py` escreve `recursos_circuito.csv` para n = 3..6, incluindo os tamanhos que não são simulados. Se falta uma instância, constrói uma matriz euclidiana aleatória. A estrutura de Q não depende dos valores das distâncias.

### Reproduzir

```bash
pip install numpy pandas scipy statsmodels matplotlib pillow
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

`qiskit-aer-gpu` é só para `qaoa_experiment.py --device GPU`, e precisa de CUDA.

```bash
python validate_formulations.py
python synthetic_instances.py
python recursos_circuito.py
python statistical_analysis_v2.py --results-dir results_aws_final --csv results_aws_final/aws_consolidated.csv
python figuras_tesis.py
python pipeline_figura.py
python extras_tesis.py
```

`synthetic_instances.py` nesta pasta escreve `synth0N_dist.csv` e `synth0N_coords.csv` aqui. `datos_tesis/generador/synthetic_instances.py` imprime o nome, o tamanho e a soma da matriz de distâncias. Não escreve os CSV. Os arquivos em `datos_tesis/instancias/` usam o formato do README dessa pasta.

`run_aws_full.py` é o script da EC2. Sem `--include_scale` corre synth03 para as formulações de `--paired_formulations` (por defeito `traditional,gps`). `--include_scale` acrescenta Tradicional em synth04, synth05 e synth06. synth06 pede cerca de 1 TB e não cabe na máquina usada.

Os CSV em `datos_tesis/instancias/` foram conferidos com o gerador em Python 3.14.7 e NumPy 2.4.3.

### Referências

- González-Bermejo, S., Alonso-Linaje, G., & Atchade-Adelomou, P. (2022). GPS: A new TSP formulation. arXiv:2110.12158
- Lucas, A. (2014). Ising formulations of many NP problems. *Frontiers in Physics*.
- Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization. *Quantum Science and Technology*, 9(2), 025022.
- Boixo, S. et al. (2018). Characterizing quantum supremacy in near-term devices. *Nature Physics*.

## Español

Este repositorio compara dos formulaciones QUBO del problema del agente viajero, GPS y QUBO tradicional one-hot, resueltas con QAOA en un simulador clásico de statevector. Las instancias son sintéticas, de 3 a 6 ciudades, con semilla fija.

La comparación de producción es synth03, las dos formulaciones, en la misma máquina. El QUBO tradicional también corre en n = 4 y n = 5 para la tendencia de escalabilidad. GPS con n > 3 no se simula. El inventario archivo por archivo de las corridas de producción de synth03 está en [`datos_tesis/README.md`](datos_tesis/README.md). Las instancias están descritas en [`datos_tesis/instancias/README.md`](datos_tesis/instancias/README.md).

### Qué hay en el repositorio

```
formulations.py              las dos matrices Q
synthetic_instances.py       instancias, semilla 42; escribe los CSV en esta carpeta
validate_formulations.py     contraste contra fuerza bruta y enumeración exhaustiva
qaoa_experiment.py           corrida local de QAOA
run_aws_full.py              corrida de QAOA usada en EC2
run_gps_n3_cloud.py          synth03, las dos formulaciones, una máquina
statistical_analysis.py      primer plan de análisis: Shapiro-Wilk, Wilcoxon, correlación, LOWESS
statistical_analysis_v2.py   análisis usado en la tesis
recursos_circuito.py         recursos del circuito, sin simular el statevector
figuras_tesis.py             figuras 01–10 y las tablas de resultados
pipeline_figura.py           figura 11, el pipeline experimental
extras_tesis.py              requisitos, hoja de formulaciones, animación one-hot vs GPS
datos_tesis/                 paquete de producción de synth03
results_aws_final/           synth03, y Tradicional en synth04 y synth05
figuras/                     figuras y tablas, en es/ y en/
recursos_circuito.csv        conteos de recursos para n = 3..6
```

### Formulaciones

El QUBO tradicional ubica la ciudad i en la posición p. La variable es x_{i,p}. Son n² variables (Lucas, 2014, one-hot). La referencia citada en la tesis para el QUBO tradicional, Montañez-Barrera et al. (2024), es DFJ. DFJ carga un número exponencial de restricciones de subtour, y esos autores solo probaron TSP hasta 7 ciudades. El one-hot de n² es la línea base que cabe en esta simulación. Es una decisión de alcance.

GPS sigue a González-Bermejo et al. (2022), ecuaciones 8–13, como está en `build_gps_qubo`. N = n − 1. Los nodos aumentados son 0, …, N+1: 0 es el depósito de salida y N+1 es el depósito de llegada. El par {0, N+1} queda fuera. Es una arista depósito–depósito, el costo es cero, y las restricciones del artículo no la prohíben. Cada par restante tiene tres estados. r = 1 es el arco directo i → j, r = 0 significa que i va antes que j y las ciudades no son adyacentes, r = 2 significa que i va después de j. El conteo de variables de esta implementación es 3(n−1)(n+2).

| n | Tradicional | GPS |
|---|---|---|
| 3 | 9 | 30 |
| 4 | 16 | 54 |
| 5 | 25 | 84 |
| 6 | 36 | 120 |

La penalización por defecto es A = 2 · Σ d_{ij}. El peso de la transitividad por defecto es λ = A. En una variable binaria, x_i² = x_i, así que un término lineal queda en la diagonal de Q. Las igualdades de GPS, contadas desde `build_gps_qubo`, son (3n² + 7n − 6)/2. Para n = 3 son 21. Las penalizaciones de transitividad son (n−1)(n−2)(n−3). El tradicional tiene 2n restricciones: cada ciudad una vez, y cada posición una vez.

En el artículo original, la ventaja de GPS es frente a la formulación nativa (n³) y frente a MTZ, no frente al one-hot. Frente al one-hot, GPS usa más variables por el factor de arriba.

### Instancias

`BASE_SEED = 42`. Las coordenadas son uniformes en el cuadrado [0, 100) × [0, 100). La distancia es euclidiana, la matriz es simétrica y la diagonal es cero. Los cuatro tamaños comparten esa semilla. Cada llamada abre un generador nuevo y consume los primeros 2n números, de modo que las ciudades de una instancia son el prefijo de la siguiente. No son muestras independientes. synth04 contiene synth03 y añade la ciudad 3, y lo mismo vale hasta synth06.

TSPLIB no se usa. Un statevector exacto ocupa 2^q · 16 bytes, donde q es el número de qubits. La instancia TSPLIB más pequeña considerada, burma14, necesita 196 qubits bajo QUBO tradicional. Eso pasa el límite práctico de simulación, unos 50 qubits (Boixo et al., 2018; Doi y Horii, 2020).

En la máquina usada para las figuras, 31 GB de RAM, el statevector cabe mientras 2^q · 16 B ≤ 31 GB, así que q ≤ 30. GPS en n = 3 tiene 30 qubits: 16 GB. El tradicional en n = 5 tiene 25 qubits. El tradicional en n = 6 tiene 36 qubits, cerca de 1 TB. GPS en n = 4 tiene 54 qubits. Estos dos últimos no se simulan aquí.

### Corridas

Los scripts de AWS usan COBYLA, `--reps 2` y `--maxiter 30`. `qaoa_experiment.py` usa por defecto `--reps 2`, `--replicas 5`, `--maxiter 50` y CPU. Un JSON no guarda el optimizador, `maxiter` ni el número de capas. Donde el log imprime `eval N/~30`, el tope de iteraciones de ese lote es 30. Los valores por defecto de los scripts no sustituyen un valor que el log no imprime. La línea de comando de los lotes de producción no está en los logs. Lo que los logs y los JSON sí dejan establecido está en [`datos_tesis/README.md`](datos_tesis/README.md).

La máquina es una EC2 t2.2xlarge, solo CPU. El tipo de instancia no está escrito en los JSON. `run_aws_full.py` no tiene opción de GPU. La misma máquina corre las dos formulaciones de synth03, así que los tiempos de ejecución se pueden comparar entre sí.

`results_aws_final/` tiene 20 réplicas Tradicionales de synth03 (índices 0–19), 8 de synth04 y 8 de synth05. GPS de synth03 tiene 17 JSON del lote de 19, más un JSON de respaldo. Las réplicas 1 y 2 de ese lote no tienen JSON. El tiempo y el objetivo están en el CSV consolidado, y no hay bitstring. El análisis asigna al respaldo un índice de réplica nuevo cuando el índice choca con un JSON que ya existe.

QAOAAnsatz emite una instrucción que el simulador de Aer no ejecuta como compuerta de base. `qaoa_experiment.py` transpila el circuito y reconstruye cada pub con `SamplerPub.coerce()`. Desempaquetar el pub como una tupla simple perdía los valores de los parámetros en algunos formatos. `run_aws_full.py` llama a `decompose()` en lugar de transpilar contra un backend AerSimulator. Ese camino aplica un `coupling_map` por defecto y se detiene alrededor de 27–28 qubits, que es un límite de topología de hardware y no aplica a un statevector. COBYLA llama al callback en cada evaluación, así que el conteo de evaluaciones puede pasar de `maxiter`. El valor que se guarda es `best_seen`, la energía mínima vista. Si la decodificación final falla, el script remuestrea en esos parámetros. Qiskit guarda el bit 0 a la derecha del bitstring, y el remuestreo lo invierte antes de calcular xᵀ Q x.

### Qué compara el análisis

Las energías en crudo no son comparables. Cada QUBO tiene su escala. La brecha usada en la tesis es (E − E_opt)/A. Cuando la fila tiene bitstring, E es E_recalc = xᵀ Q x, no `objective_value`. E_opt es la energía mínima entre las soluciones factibles de ese QUBO.

`statistical_analysis_v2.py` trata las réplicas como independientes, salvo con `--paired`: Mann-Whitney para el tiempo, Fisher para la factibilidad. `--paired` solo corresponde al caso en que GPS y Tradicional compartieron semilla por réplica. Ahí las pruebas son Wilcoxon y McNemar. Qubits, profundidad y número de compuertas son constantes dentro de una formulación, así que quedan descriptivos. No se reportan correlaciones agrupadas entre formulaciones: quedan confundidas con el tamaño de la instancia.

synth03/gps/réplica 1 queda fuera de la energía y de la brecha. Su `objective_value` es idéntico al E_opt de Tradicional, y esa fila se trata como contaminada. Se conserva en la comparación de tiempo. La brecha de ruta, en `figuras_tesis.py`, es el costo del tour decodificado frente al óptimo por fuerza bruta, y solo está definida para soluciones factibles.

### Figuras

`figuras_tesis.py` escribe las figuras 01–10 y las tablas en `figuras/`, en español y en inglés. `pipeline_figura.py` escribe la figura 11. `extras_tesis.py` escribe la tabla de requisitos, la hoja de formulaciones y `anim_onehot_vs_gps.gif`. `recursos_circuito.py` escribe `recursos_circuito.csv` para n = 3..6, incluidos los tamaños que no se simulan. Si falta una instancia, construye una matriz euclidiana aleatoria. La estructura de Q no depende de los valores de las distancias.

### Reproducir

```bash
pip install numpy pandas scipy statsmodels matplotlib pillow
pip install qiskit qiskit-aer qiskit-algorithms qiskit-optimization
```

`qiskit-aer-gpu` es solo para `qaoa_experiment.py --device GPU`, y necesita CUDA.

```bash
python validate_formulations.py
python synthetic_instances.py
python recursos_circuito.py
python statistical_analysis_v2.py --results-dir results_aws_final --csv results_aws_final/aws_consolidated.csv
python figuras_tesis.py
python pipeline_figura.py
python extras_tesis.py
```

`synthetic_instances.py` en esta carpeta escribe `synth0N_dist.csv` y `synth0N_coords.csv` aquí. `datos_tesis/generador/synthetic_instances.py` imprime el nombre, el tamaño y la suma de la matriz de distancias. No escribe los CSV. Los archivos de `datos_tesis/instancias/` usan el formato del README de esa carpeta.

`run_aws_full.py` es el script de EC2. Sin `--include_scale` corre synth03 para las formulaciones de `--paired_formulations` (por defecto `traditional,gps`). `--include_scale` añade Tradicional en synth04, synth05 y synth06. synth06 pide cerca de 1 TB y no cabe en la máquina usada.

Los CSV de `datos_tesis/instancias/` se contrastaron con el generador en Python 3.14.7 y NumPy 2.4.3.

### Referencias

- González-Bermejo, S., Alonso-Linaje, G., & Atchade-Adelomou, P. (2022). GPS: A new TSP formulation. arXiv:2110.12158
- Lucas, A. (2014). Ising formulations of many NP problems. *Frontiers in Physics*.
- Montañez-Barrera, J. A., Willsch, D., Maldonado-Romo, A., & Michielsen, K. (2024). Unbalanced penalization. *Quantum Science and Technology*, 9(2), 025022.
- Boixo, S. et al. (2018). Characterizing quantum supremacy in near-term devices. *Nature Physics*.

María Julia Pareja Abarca, Escuela Profesional de Ingeniería de Sistemas, Universidad Católica de Santa María, 2026.
