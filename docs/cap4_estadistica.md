# Estadística y pruebas

## (A) Texto

### Estadística descriptiva

La estadística descriptiva resume el tiempo, la factibilidad, el óptimo alcanzado y las dos brechas en cada grupo de instancia y formulación. El conjunto es el de la etapa anterior: 56 réplicas, con 20 de GPS y 20 de la formulación tradicional en synth03, y 8 tradicionales en synth04 y en synth05. El tiempo se resume con la mediana y el intervalo intercuartílico, y se acompañan la media, la desviación estándar y los extremos, porque los grupos son pequeños y la serie de GPS está cargada hacia un extremo.

Las proporciones llevan el intervalo de Wilson al 95 %, que sigue definido cuando la proporción es 0 o se acerca a 1 [CITA: Wilson]. Los recursos del circuito son constantes dentro de cada formulación y no aportan dispersión; su conteo está en la Etapa 3. La energía de cada réplica es \(x^{\mathsf T}Qx\) cuando existe el bitstring, y el objetivo archivado cuando no existe. La brecha energética es \((E-E_{\mathrm{opt}})/A\) y se calcula sobre todas las réplicas retenidas para esa magnitud, factibles o no. La réplica GPS 1 de synth03 queda fuera de la energía y de la brecha, y permanece en el tiempo y en la factibilidad.

El óptimo alcanzado usa el mismo conjunto que la factibilidad: una réplica cuenta como éxito si es factible y \(|E-E_{\mathrm{opt}}|\) no pasa de \(10^{-6}|E_{\mathrm{opt}}|\). La brecha de ruta, en porcentaje, compara el costo del ciclo decodificado con el costo óptimo del vendedor viajero, y solo entra una solución factible cuyo ciclo existe. El tiempo hasta una solución óptima con probabilidad 0,99 es \(\mathrm{TTS}_{99}=t\cdot\ln(0{,}01)/\ln(1-p)\), donde \(t\) es la mediana del tiempo y \(p\) la proporción que alcanza \(E_{\mathrm{opt}}\) [CITA: TTS]. Si \(p=0\), el índice no está definido y se informa la cota inferior obtenida al sustituir \(p\) por el extremo superior del intervalo de Wilson. Si \(p=1\), \(\mathrm{TTS}_{99}\) coincide con \(t\).

La réplica 19 de GPS procede del respaldo y su permanencia sigue abierta, de modo que todo resultado de GPS se da en dos escenarios. El escenario A la conserva (20 réplicas en synth03) y el B la retira (19). La formulación tradicional no se desdobla. Los valores están en la Tabla X y en la Tabla X+1. En synth03 tradicional, factibilidad y óptimo coinciden en 18/20. La mediana de su brecha energética es 0,000 y la media es 0,180, porque las dos réplicas no factibles son las que se apartan de \(E_{\mathrm{opt}}\).

La brecha de ruta de las 18 soluciones factibles de synth03 tradicional queda en el orden de \(10^{-14}\,\%\). En GPS, en los dos escenarios, y en la tradicional de synth04 y de synth05, no hay solución factible: la brecha de ruta no está definida y \(\mathrm{TTS}_{99}\) se sustituye por su cota inferior.

### Estadística inferencial

Las réplicas se generaron sin semilla fija y sin emparejar una corrida GPS con una tradicional, así que las dos muestras de synth03 se tratan como independientes. La factibilidad se contrasta con la prueba exacta de Fisher y el tiempo con la U de Mann-Whitney, ambas bilaterales [CITA: Fisher] [CITA: Mann-Whitney]. McNemar y Wilcoxon quedan reservados al caso, no usado aquí, en que cada índice de réplica hubiera compartido la semilla. Shapiro-Wilk se calcula sobre el tiempo de cada grupo solo como diagnóstico: el programa guarda el resultado y no lo usa para elegir la prueba. El nivel de significación es \(\alpha=0{,}05\). El contraste inferencial se limita a \(n=3\), único tamaño en el que se ejecutaron las dos formulaciones.

En GPS, Shapiro-Wilk del tiempo da \(W=0{,}788\) y \(p=5{,}84\times 10^{-4}\) en el escenario A, y \(W=0{,}798\) y \(p=1{,}08\times 10^{-3}\) en el escenario B. En la formulación tradicional, \(p=3{,}29\times 10^{-1}\) para \(n=3\), \(p=4{,}20\times 10^{-1}\) para \(n=4\) y \(p=3{,}10\times 10^{-1}\) para \(n=5\), con \(W=0{,}947\), \(W=0{,}919\) y \(W=0{,}903\). El diagnóstico describe la forma de cada serie y no sustituye a las pruebas de las hipótesis.

### Test 1

El Test 1 compara, en synth03, la factibilidad de las dos formulaciones. La hipótesis nula afirma que la probabilidad de una solución factible es la misma en GPS y en la formulación tradicional. La hipótesis alterna afirma que esas probabilidades difieren. El estadístico es la prueba exacta de Fisher sobre la tabla de 2 por 2 cuyas filas son factible y no factible y cuyas columnas son tradicional y GPS. La prueba es bilateral. Se rechaza la hipótesis nula cuando \(p<\alpha\), con \(\alpha=0{,}05\). El odds ratio es \((a\cdot d)/(b\cdot c)\) en esa tabla. Si la celda factible de GPS es 0 y la no factible es positiva, el cociente es infinito.

En el escenario A la tabla tiene 18 y 0 en la fila factible, y 2 y 20 en la fila no factible. El odds ratio es infinito y \(p=3{,}35\times 10^{-9}\). Se rechaza la hipótesis nula. [VINCULAR CON H1 DEL CAPÍTULO I] La sensibilidad retira las réplicas GPS 1 y 2, que no tienen bitstring y entran a la factibilidad por el criterio de energía de \(n=3\). La tabla pasa a 18 y 0 frente a 2 y 18, el odds ratio sigue siendo infinito y \(p=5{,}69\times 10^{-9}\). También se rechaza la hipótesis nula.

En el escenario B las celdas de GPS son 0 y 19, con \(p=3{,}35\times 10^{-9}\). Sin las réplicas 1 y 2 quedan 0 y 17, con \(p=1{,}19\times 10^{-8}\). El odds ratio permanece infinito. En los cuatro contrastes se rechaza la hipótesis nula al nivel 0,05. Las cuatro tablas están en la Tabla X+2.

### Test 2

El Test 2 compara, en synth03, el tiempo de ejecución de las dos formulaciones. La hipótesis nula afirma que la distribución del tiempo es la misma en GPS y en la formulación tradicional. La hipótesis alterna afirma que las distribuciones difieren. El estadístico es la U de Mann-Whitney bilateral, con GPS como primera muestra. La correlación biserial por rangos es \(r=2U/(n_{\mathrm{GPS}}\cdot n_{\mathrm{trad}})-1\). El signo positivo indica que la primera muestra, GPS, tiende a tiempos mayores que la tradicional. El valor \(r=1\) corresponde a la separación completa: cada tiempo de GPS supera a cada tiempo tradicional, y entonces \(U=n_{\mathrm{GPS}}\cdot n_{\mathrm{trad}}\). Se rechaza la hipótesis nula cuando \(p<\alpha\).

En el escenario A, \(U=400\), con 20 y 20 réplicas, \(r=1\) y \(p=6{,}80\times 10^{-8}\). En el escenario B, \(U=380\), con 19 y 20 réplicas, \(r=1\) y \(p=1{,}01\times 10^{-7}\). En ambos se rechaza la hipótesis nula al nivel 0,05. [VINCULAR CON H1 DEL CAPÍTULO I] El valor \(p\) es el que devuelve la llamada del programa de análisis, que no fija el método exacto de la U. El detalle de esa llamada está en la evidencia. La réplica GPS 1 entra en las dos muestras de tiempo.

### Análisis de escalabilidad

Sobre la formulación tradicional, el suavizado LOWESS del tiempo frente a \(n\), con fracción 1,0 y cero iteraciones de robustez, vale 4,321 s en \(n=3\), 3,528 s en \(n=4\) y 295,238 s en \(n=5\) [CITA: LOWESS]. El de la brecha energética vale 0,180, 4,232 y 2,511 en los mismos tres tamaños (Tabla X+3). Con tres abscisas distintas y esa fracción, el valor suavizado en cada \(n\) coincide con la media aritmética del grupo. El trazo une esos tres puntos con carácter orientativo y no es una prueba inferencial. GPS no entra en este suavizado, porque esa formulación solo se ejecutó en \(n=3\).

## (B) Tablas

Las Tablas X y X+1 redondean a tres decimales. La sección (C) conserva más cifras. Los intervalos de Wilson usan \(z=1{,}96\).

**Tabla X**

*Tiempo de ejecución y diagnóstico de Shapiro-Wilk*

| Instancia | Formulación | Escenario | R | Mediana (s) | Q1 (s) | Q3 (s) | RIC (s) | Media (s) | DE (s) | Mínimo (s) | Máximo (s) | W | p |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| synth03 | GPS | A | 20 | 16 797,196 | 16 361,616 | 16 836,279 | 474,663 | 16 628,180 | 333,713 | 15 670,230 | 16 953,235 | 0,788 | 5,84 × 10⁻⁴ |
| synth03 | GPS | B | 19 | 16 788,057 | 16 348,909 | 16 824,279 | 475,370 | 16 614,404 | 336,964 | 15 670,230 | 16 953,235 | 0,798 | 1,08 × 10⁻³ |
| synth03 | Tradicional | — | 20 | 4,349 | 4,282 | 4,395 | 0,113 | 4,321 | 0,105 | 4,100 | 4,482 | 0,947 | 3,29 × 10⁻¹ |
| synth04 | Tradicional | — | 8 | 3,538 | 3,490 | 3,560 | 0,070 | 3,528 | 0,078 | 3,419 | 3,637 | 0,919 | 4,20 × 10⁻¹ |
| synth05 | Tradicional | — | 8 | 295,688 | 294,718 | 296,421 | 1,702 | 295,238 | 4,039 | 287,049 | 301,203 | 0,903 | 3,10 × 10⁻¹ |

*Nota.* RIC es Q3 − Q1. El escenario A incluye la réplica 19 de GPS y el B la excluye. La réplica GPS 1 entra en todas las filas de tiempo. Q1 y Q3 usan la interpolación lineal de pandas.

**Tabla X+1**

*Factibilidad, óptimo, brechas y TTS99*

| Instancia | Formulación | Escenario | Factibles | Proporción | IC 95 % | Óptimas | Proporción | IC 95 % | n de la brecha | Media | Mediana | DE | Mínimo | Máximo | n de ruta | Media de ruta (%) | Máximo de ruta (%) | TTS99 (s) |
| --- | --- | --- | --- | ---: | --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |
| synth03 | GPS | A | 0/20 | 0,000 | [0,000; 0,161] | 0/20 | 0,000 | [0,000; 0,161] | 19 | 4,617 | 3,889 | 3,283 | 1,111 | 13,222 | 0 | no definida | no definida | no definido; cota inferior 440 262,312 |
| synth03 | GPS | B | 0/19 | 0,000 | [0,000; 0,168] | 0/19 | 0,000 | [0,000; 0,168] | 18 | 4,756 | 3,892 | 3,320 | 1,111 | 13,222 | 0 | no definida | no definida | no definido; cota inferior 419 843,544 |
| synth03 | Tradicional | — | 18/20 | 0,900 | [0,699; 0,972] | 18/20 | 0,900 | [0,699; 0,972] | 20 | 0,180 | 0,000 | 0,555 | 0,000 | 1,820 | 18 | 4,85 × 10⁻¹⁵ | 1,46 × 10⁻¹⁴ | 8,697 |
| synth04 | Tradicional | — | 0/8 | 0,000 | [0,000; 0,324] | 0/8 | 0,000 | [0,000; 0,324] | 8 | 4,232 | 3,989 | 0,714 | 3,843 | 5,972 | 0 | no definida | no definida | no definido; cota inferior 41,543 |
| synth05 | Tradicional | — | 0/8 | 0,000 | [0,000; 0,324] | 0/8 | 0,000 | [0,000; 0,324] | 8 | 2,511 | 2,057 | 0,884 | 1,960 | 3,945 | 0 | no definida | no definida | no definido; cota inferior 3 472,135 |

*Nota.* La brecha energética de GPS excluye la réplica 1 y, en el escenario B, también la 19. Factibilidad, óptimo y tiempo conservan la réplica 1. La cota de TTS99 usa el extremo superior del IC de Wilson de \(p\) cuando \(p=0\). En synth03 tradicional, \(\ln(0{,}01)/\ln(0{,}1)=2\), así que TTS99 es el doble de la mediana.

**Tabla X+2**

*Test 1, prueba exacta de Fisher bilateral en synth03, y Test 2, U de Mann-Whitney bilateral*

| Contraste | Factible, tradicional | Factible, GPS | No factible, tradicional | No factible, GPS | Odds ratio | p | Decisión |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Fisher, escenario A | 18 | 0 | 2 | 20 | infinito | 3,35 × 10⁻⁹ | Rechazar H0 |
| Fisher, A sin réplicas GPS 1 y 2 | 18 | 0 | 2 | 18 | infinito | 5,69 × 10⁻⁹ | Rechazar H0 |
| Fisher, escenario B | 18 | 0 | 2 | 19 | infinito | 3,35 × 10⁻⁹ | Rechazar H0 |
| Fisher, B sin réplicas GPS 1 y 2 | 18 | 0 | 2 | 17 | infinito | 1,19 × 10⁻⁸ | Rechazar H0 |

| Contraste | n GPS | n tradicional | U | r | p | Decisión |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Mann-Whitney, escenario A | 20 | 20 | 400 | 1 | 6,80 × 10⁻⁸ | Rechazar H0 |
| Mann-Whitney, escenario B | 19 | 20 | 380 | 1 | 1,01 × 10⁻⁷ | Rechazar H0 |

*Nota.* \(\alpha=0{,}05\). El odds ratio es infinito porque la celda factible de GPS es 0 y la no factible es positiva. \(r=1\) indica que todos los tiempos de GPS superan a todos los de la formulación tradicional.

**Tabla X+3**

*LOWESS de la formulación tradicional, frac = 1,0 e it = 0*

| n | Tiempo suavizado (s) | Brecha energética suavizada |
| ---: | ---: | ---: |
| 3 | 4,321 | 0,180 |
| 4 | 3,528 | 4,232 |
| 5 | 295,238 | 2,511 |

*Nota.* Cada valor coincide con la media del grupo en ese \(n\). El suavizado es orientativo.

## (C) Cifras completas, escenarios A y B

La tradicional no tiene escenario. Donde una celda no aplica, se deja en blanco. Las proporciones y los intervalos usan la fórmula de Wilson con \(z=1{,}96\).

| Indicador | GPS A | GPS B | Tradicional synth03 | Tradicional synth04 | Tradicional synth05 |
| --- | ---: | ---: | ---: | ---: | ---: |
| R de tiempo, factibilidad y óptimo | 20 | 19 | 20 | 8 | 8 |
| Mediana del tiempo (s) | 16797,196304 | 16788,057274 | 4,348653 | 3,537833 | 295,687745 |
| Q1 (s) | 16361,616073 | 16348,908977 | 4,282081 | 3,490136 | 294,718425 |
| Q3 (s) | 16836,278822 | 16824,278610 | 4,394957 | 3,559866 | 296,420738 |
| RIC (s) | 474,662749 | 475,369633 | 0,112875 | 0,069730 | 1,702313 |
| Media del tiempo (s) | 16628,179955 | 16614,403629 | 4,320690 | 3,527745 | 295,238114 |
| DE del tiempo (s) | 333,713474 | 336,964377 | 0,105209 | 0,077622 | 4,038785 |
| Mínimo del tiempo (s) | 15670,229562 | 15670,229562 | 4,099672 | 3,418632 | 287,049299 |
| Máximo del tiempo (s) | 16953,234515 | 16953,234515 | 4,482491 | 3,636951 | 301,203468 |
| Shapiro-Wilk W | 0,788457 | 0,798385 | 0,947404 | 0,918741 | 0,903386 |
| Shapiro-Wilk p | 5,841909 × 10⁻⁴ | 1,082857 × 10⁻³ | 3,294008 × 10⁻¹ | 4,197304 × 10⁻¹ | 3,098248 × 10⁻¹ |
| Factibles k/R | 0/20 | 0/19 | 18/20 | 0/8 | 0/8 |
| IC de Wilson, factibilidad | [0; 0,161130] | [0; 0,168184] | [0,698962; 0,972134] | [0; 0,324416] | [0; 0,324416] |
| Óptimas k/R | 0/20 | 0/19 | 18/20 | 0/8 | 0/8 |
| IC de Wilson, óptimo | [0; 0,161130] | [0; 0,168184] | [0,698962; 0,972134] | [0; 0,324416] | [0; 0,324416] |
| n de la brecha energética | 19 | 18 | 20 | 8 | 8 |
| Media de la brecha | 4,617255 | 4,756494 | 0,180226 | 4,232213 | 2,510591 |
| Mediana de la brecha | 3,889049 | 3,892421 | 0,000000 | 3,988727 | 2,056628 |
| DE de la brecha | 3,282817 | 3,319757 | 0,554754 | 0,713530 | 0,883643 |
| Mínimo de la brecha | 1,110951 | 1,110951 | 0,000000 | 3,842897 | 1,959653 |
| Máximo de la brecha | 13,221902 | 13,221902 | 1,819684 | 5,972137 | 3,944846 |
| n de la brecha de ruta | 0 | 0 | 18 | 0 | 0 |
| Media de la brecha de ruta (%) | no definida | no definida | 4,854378 × 10⁻¹⁵ | no definida | no definida |
| Máximo de la brecha de ruta (%) | no definida | no definida | 1,456313 × 10⁻¹⁴ | no definida | no definida |
| TTS99 (s) | no definido | no definido | 8,697307 | no definido | no definido |
| Cota inferior de TTS99 (s) | 440262,312452 | 419843,543716 |  | 41,543270 | 3472,135401 |
| Fisher, tabla factible / no factible | 0 / 20 | 0 / 19 | 18 / 2 |  |  |
| Fisher p | 3,351553383 × 10⁻⁹ | 3,351553383 × 10⁻⁹ |  |  |  |
| Fisher, odds ratio | infinito | infinito |  |  |  |
| Fisher sin réplicas 1 y 2, celdas GPS | 0 / 18 | 0 / 17 |  |  |  |
| Fisher p, sin réplicas 1 y 2 | 5,688248154 × 10⁻⁹ | 1,188278018 × 10⁻⁸ |  |  |  |
| Mann-Whitney U | 400 | 380 |  |  |  |
| Mann-Whitney r | 1 | 1 |  |  |  |
| Mann-Whitney p, llamada del programa | 6,795615128 × 10⁻⁸ | 1,012364823 × 10⁻⁷ |  |  |  |
| Mann-Whitney p, método exacto | 1,450888910 × 10⁻¹¹ | 2,901777821 × 10⁻¹¹ |  |  |  |
| LOWESS del tiempo (s), n = 3, 4, 5 |  |  | 4,320690; 3,527745; 295,238114 |  |  |
| LOWESS de la brecha, n = 3, 4, 5 |  |  | 0,180226; 4,232213; 2,510591 |  |  |

*Nota.* La fila de Fisher p del escenario A y la del B coinciden hasta \(3{,}35\times 10^{-9}\). En cifras completas, A es \(3{,}3515533829892784\times 10^{-9}\) y B es \(3{,}3515533829892775\times 10^{-9}\), tomadas de la orientación que usa el programa (filas: tradicional, GPS; columnas: factible, no factible). La tabla de esta sección está traspuesta a la orientación pedida y el odds ratio no cambia. El p exacto de Mann-Whitney no es el que imprime el programa; se lista para dejar constancia de la diferencia.

## (D) Evidencia

**Carga y energía**

- Entrada: `results_aws_final` y `results_aws_final/aws_consolidated.csv` (`statistical_analysis_v2.py:306-307`). Las figuras usan las mismas rutas (`figuras_tesis.py:21-22`) y llaman a `load_results` y `evaluate_quality` (`figuras_tesis.py:19` y `:107`).
- Consolidación, reindexación del respaldo como réplica 19 e incorporación de las réplicas GPS 1 y 2 sin bitstring: `statistical_analysis_v2.py:63-100`.
- Energía de trabajo del análisis: si hay bitstring, \(E\) es \(x^{\mathsf T}Qx\); si no, el objetivo (`statistical_analysis_v2.py:217-219`). Las figuras hacen lo mismo en `E_usada` (`figuras_tesis.py:109-110`). Tolerancia relativa \(10^{-6}\) (`statistical_analysis_v2.py:23`).
- Factibilidad con bitstring: tradicional, `statistical_analysis_v2.py:195-201`; GPS, `:202-210`. Sin bitstring y con \(n=3\) y matriz simétrica, factible si el objetivo coincide con \(E_{\mathrm{opt}}\) (`:211-214`).
- Óptimo en el programa: solo si la fila es factible, y compara el objetivo archivado con \(E_{\mathrm{opt}}\) (`statistical_analysis_v2.py:220-221`). Recalculado con \(E\) en lugar del objetivo, ninguna fila cambia de condición. La única discrepancia entre \(x^{\mathsf T}Qx\) y el objetivo es synth05 tradicional, réplica 4, y esa fila no es factible, así que el óptimo sigue en falso.
- Réplica GPS 1 excluida de la brecha: `figuras_tesis.py:2-3` y `:111`. El tiempo del diagrama de synth03 usa la serie completa (`figuras_tesis.py:194`).

**Intervalos, pruebas y suavizado**

- Intervalo de Wilson con \(z=1{,}96\): `figuras_tesis.py:88-95`. El análisis tiene otra implementación, `scipy.stats.binomtest.proportion_ci(method="wilson")` (`statistical_analysis_v2.py:236-240`). Para 18/20, la fórmula de las figuras da [0,69896179; 0,97213411] y SciPy da [0,69896635; 0,97213352]. La diferencia está en el orden de \(10^{-6}\). Las tablas de esta sección usan la fórmula de las figuras. Ningún CSV de `figuras/` guarda el intervalo, así que no hay conflicto con un archivo de salida.
- Fisher bilateral, por defecto de `scipy.stats.fisher_exact`, tabla del programa `[[factibles tradicional, no factibles tradicional], [factibles GPS, no factibles GPS]]`: `statistical_analysis_v2.py:273-278`. SciPy 1.18.1. El odds ratio es `inf` en los cuatro contrastes.
- Mann-Whitney bilateral, GPS como primera muestra, \(r=2U/(n_1 n_2)-1\): `statistical_analysis_v2.py:253-259`. La llamada no pasa `method`. En SciPy 1.18.1 ese defecto devuelve el mismo p que `method="asymptotic"`. Con `method="exact"`, el escenario A da \(p=1{,}450888910\times 10^{-11}\) y el B da \(p=2{,}901777821\times 10^{-11}\). [VERIFICAR: si el capítulo debe publicar el p asintótico, que es el de la llamada escrita, o el exacto. Las dos decisiones rechazan H0 al nivel 0,05.] No hay empates de tiempo entre GPS y la tradicional: el mínimo de GPS es 15 670,230 s y el máximo tradicional es 4,482 s.
- Shapiro-Wilk: el programa guarda solo el p (`statistical_analysis_v2.py:248-250`). El W de esta sección es el estadístico de la misma función `scipy.stats.shapiro`.
- Brecha de ruta: `figuras_tesis.py:326-342`. El óptimo de ruta fija la ciudad 0 y permuta el resto (`:327-330`). Solo entran filas factibles con `tour_cost` (`:335-336`).
- LOWESS del tiempo en el análisis: `statistical_analysis_v2.py:302-303`, `frac=1.0`, `it=0`, y se conserva la primera ordenada de cada \(n\). La figura del tiempo hace la misma llamada (`figuras_tesis.py:257-258`). La figura de la brecha la hace en `figuras_tesis.py:215-216` sobre la brecha tradicional. En los tres tamaños, todas las ordenadas suavizadas de un mismo \(n\) son idénticas e iguales a la media del grupo.
- TTS99 no está implementado. Una búsqueda de `TTS` en `figuras_tesis.py` no devuelve coincidencias, y no existe `figuras/tabla_tts.csv`. Las cotas de esta sección se calcularon aparte, con la mediana de pandas y el extremo superior de Wilson de `figuras_tesis.py:88-95`.

**Diferencias con las tablas ya escritas por `figuras_tesis.py`**

- `figuras/tabla_resultados.csv`, fila GPS de \(n=3\): el archivo guarda 19 réplicas y mediana de tiempo 16 806,33533386502 s. El código actual (`figuras_tesis.py:312-324`) separa el conteo: la mediana del tiempo y el número de réplicas salen del grupo completo, y la brecha sale del grupo sin `excluir_energia`. Recalculado así, la mediana de GPS en el escenario A es 16 797,196304 s y el número de réplicas es 20. La causa es que el CSV se escribió cuando el filtro de la réplica 1 se aplicaba antes de la mediana y del conteo. No se regeneró el CSV. Las columnas de brecha de esa fila sí coinciden con el escenario A (respaldo incluido, réplica 1 fuera): media 4,617254958793153, mediana 3,889049014476974, DE 3,2828168948788763.
- Las filas tradicionales de `tabla_resultados.csv` coinciden con este cálculo en réplicas, factibles, mediana del tiempo y brecha (media, mediana y DE).
- `figuras/tabla_brecha_ruta.csv` coincide en las cuatro filas, incluida GPS con 20 réplicas, 0 factibles y brecha no definida, y la tradicional de synth03 con media \(4{,}854377662604044\times 10^{-15}\,\%\) y máximo \(1{,}456313298781213\times 10^{-14}\,\%\). Esa tabla nunca quitó la réplica 1 del conteo de réplicas (`figuras_tesis.py:337`).
- `tabla_tts` no existe en el programa ni en `figuras/`. No hay cifra de TTS contra la cual contrastar.

**Respaldo**

- [VERIFICAR: esta sección presenta los escenarios A y B porque la permanencia de la réplica 19 sigue marcada como pendiente y podría corresponder a un ensayo con maxiter 5. El JSON `results_aws_final/backup_rep1/synth03_gps_0.json` tiene tiempo 16 889,930 s y objetivo −14 550,540, que coinciden con la línea `OK (16889.9s, fval=-14550.54)` de `gps_batch_final.log` (`eval N/~30`). No coinciden con `gps_test_fix.log`, que cierra en 847,1 s y objetivo −9 259,23. El tiempo del respaldo es 1,006 veces la mediana de las otras 19 réplicas GPS, no unas seis veces menor.]
