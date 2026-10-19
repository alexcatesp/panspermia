# Cierre de P0: factores que hay que decidir antes de P1

**18-10-2026 · decisión del responsable:** no se pasa a P1 hasta estar convencidos de que ninguna decisión de P0 tendrá que revisarse más adelante. Cada factor se apoya en bibliografía. Las referencias están en `docs/bibliografia/escalera/refs.bib`, con los DOI comprobados en Crossref.

**Qué es "de P0":** las reglas de la herencia, la variación, la demografía y la estructura de la población, que existen aunque no haya selección. P0 mide cómo se comportan solas; algunas solo se pueden juzgar del todo con selección (P1), pero **se deciden aquí**, porque cambiarlas después invalidaría todos los peldaños.

**Estados:**
- ✅ cerrado;
- 🔬 en simulación;
- 📋 pendiente de simular;
- 📚 se decide por bibliografía, sin simular;
- ⚖ simulado; falta la decisión del responsable;
- ⏭ no es de P0 (se decide en su peldaño).

## A. Variación: cómo muta el genoma

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| A1 | Física de la mutación de **neuronas** | "nest": invierte un hueco al azar; sin selección deriva hacia unas 43 | Infla los cerebros sin que sirvan; en la Tierra se pierde más de lo que se gana | kuo2009deletional, mira2001deletional, lynch2000duplicate, stanley2002neat, yampolsky2001bias, cano2022mutation | P0 con nest, neutral y terrestre (✅ 15 mundos; 5/5 en las dos comparaciones). P1 con las tres (✅ 15 mundos): la selección vacía el cerebro con todas (nest 0,11–0,42; neutral 0,05–0,12; terrestre 0,05–0,10). **Responsable (19-10, 23:28): neutral para toda la escalera; al final, los peldaños clave se repiten con la terrestre (robustez)** | ✅ |
| A2 | Física de la mutación de la **CPPN** | añadir 5 %, quitar 2 %, dividir 3 %, quitar nodo 1 % | En P0 sus nodos pasan de 0,35 a ~11: es el mismo sesgo, en la receta del cerebro | stanley2002neat, langdon1998bloat, banzhaf2002bloat, kuo2009deletional | P0-cppn-neutral (✅ 5/5): ya no se infla, pero pierde aristas. **Responsable (19-10, 07:22): decidir tras P1-peaje-cppn-neutral** | 🔬 P1 en cola |
| A3 | **Tasas de mutación**: gen o constante | σ autoadaptativa y tasa estructural como gen (deriva +75 % en 300 épocas) | Sin selección, la tasa sube por el suelo en 0. En la Tierra, la selección la baja hasta la barrera de la deriva | lynch2016driftbarrier, sniegowski1997mutators, beyer2002es | P0-tasas-fijas (✅ 5/5, efecto pequeño). Si se mantiene como gen, el ruido pasa a escala logarítmica (sin artefacto del suelo). **Responsable (19-10, 07:20): decidir tras P1-peaje-tasas-fijas frente a P1-peaje** | 🔬 P1 en cola |
| A4 | **Cuánto** se muta: σ inicial 0,05, τ = 0,2, 11 % de cambios estructurales por hijo | sin contrastar | Demasiada mutación destruye la información más deprisa de lo que la selección la fija (umbral de error). Demasiado poca estanca | eigen1971selforganization, lynch2016driftbarrier | En P0: velocidad de divergencia neutral (`genome_distance`). El juicio necesita P1 | 📋 análisis de P0 + prueba en P1 |
| A5 | **Techo** del genoma: 64 neuronas y 32 nodos de CPPN | fijo | Con nest, el equilibrio neutral (~43) queda cerca del techo. La evolución abierta necesita poder crecer sin un límite artificial | taylor2016oee, stanley2002neat | Analizar en P0 qué fracción de bichos toca el techo con cada física. Hecho: el de neuronas no limita con ninguna física; el de la CPPN sí (8–34 %) | ⚖ tras A2 |
| A6 | **Genoma inicial**: 8 neuronas y CPPN mínima | "empezar mínimo" (NEAT) | Con la física terrestre, el punto de partida pesa: deriva hacia 0 | stanley2002neat, lynch2003origins | Se decide junto con A1: con la física neutral, el tamaño inicial es el punto alrededor del cual deriva | ✅ con A1: 8 neuronas, centro de la deriva neutral |
| A7 | **Precisión** del genoma: los pesos se guardan en f16 | f16 | Un cambio menor que la resolución de f16 desaparece al guardarse: es otra "física" oculta, un suelo para σ | — (es técnico) | Medir en P0 cuántas mutaciones se pierden por redondeo. Hecho: entre el 6 y el 10 % | ⚖ tras A3 |

## B. Reproducción y herencia

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| B1 | **Sexo** (recombinación) | solo asexual; el sexo estaba previsto para la fase 3 | Sin recombinación, las mejoras compiten en lugar de sumarse (interferencia clonal) y las mutaciones dañinas se acumulan (trinquete de Muller). En poblaciones grandes, el sexo acelera mucho la adaptación. Añadirlo más tarde invalidaría todo lo anterior | muller1964ratchet, felsenstein1974recombination, colegrave2002sex, mcdonald2016sex; ligamiento: hill1966linkage, thompson2014supergenes, charlesworth2000ydegeneration, birky1995uniparental | P0-feliz-sexual (✅ 5 mundos): **el cruce por índice rompe la receta del cerebro** (entre el 83 y el 88 % de los nodos de la CPPN quedan sin salida). Era un error de implementación: **corregido (ADR-018, la CPPN se hereda entera, como un supergén) y se repite** (P0-feliz-sexual-bloques). Repetición (✅ 5 mundos): la receta queda sana (3–8 % de nodos sin salida) y la variedad no se pierde. **Responsable (19-10, 15:14): decidir tras P1-peaje-sexual-bloques** (supergén o marcas históricas) | 🔬 P1 en cola |
| B2 | **Herencia de lo aprendido** | darwiniana: el hijo nace con los pesos innatos, no con los aprendidos | Heredar lo aprendido (lamarckiano) acelera en mundos **estables** (Ackley y Littman 1994), pero cae más en óptimos locales (Whitley et al. 1994) y es **peor cuando el mundo cambia**: hereda lo que servía en un mundo que ya no existe (Sasaki y Tokoro 2000). Aprender sin heredarlo también acelera la evolución (efecto Baldwin; Hinton y Nowlan 1987), según la pendiente de la ganancia (Paenke et al. 2007). Además, con una codificación indirecta (CPPN) no se puede reescribir la receta a partir de los pesos aprendidos | whitley1994lamarck, ackley1994lamarck, sasaki2000lamarck, hinton1987learning, paenke2007plasticity | Ninguna en P0 (no hay nada que aprender). La transmisión de lo aprendido entre bichos (cultura) sería un peldaño social, no genético | ✅ 📚 |
| B3 | ¿Quién paga la energía del hijo? | dotación regalada (P0, P1) o cedida por el padre (P3+) | — | — | Es de P3 | ⏭ |

## C. Demografía

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| C1 | **Tamaño de la población** (tope) | 4.096 | El azar compite con la selección: una ventaja menor que ~1/N no se impone. Las poblaciones pequeñas y las grandes llegan a la complejidad por caminos distintos. El sexo ayuda más en las grandes | ohta1973nearlyneutral, charlesworth2009ne, labar2016populations, colegrave2002sex | P0-N1024 (✅ 5 mundos): el cerebro crece igual (29 frente a 30 neuronas), pero con mucha menos variedad (32–100 clados frente a 540–740). **Responsable (19-10, 12:04): se queda en 4.096** | ✅ |
| C2 | **Muerte y vejez** | P0: vida fija de 600 pasos. Desde P1: la vejez se impone (gasto creciente desde 5.000 pasos) | En la Tierra, el envejecimiento **evoluciona**: acumulación de mutaciones (Medawar), pleiotropía antagonista (Williams), soma desechable (Kirkwood). En mundos espaciales, la muerte programada puede verse favorecida. Imponerla o dejarla evolucionar cambia la duración de las generaciones y cuánto compensa aprender | williams1957pleiotropy, kirkwood1977ageing, werfel2015death | En P0 solo reescala el tiempo. La decisión ("ley del mundo" o "gen") se toma ahora y se prueba en P1 o P2 | 📚 decidir ahora |
| C3 | **Población inicial** (512) | 512 | Solo afecta a la primera época: el mundo se llena enseguida | — | Ninguna: irrelevante en P0 | ✅ |
| C4 | **Tope de nacimientos** por paso (32) | 32 | Si se alcanza, frena la reproducción por una razón técnica | — | Comprobar en los datos que nunca se alcanza. Hecho: se alcanza por las cohortes sincronizadas, sin perder nacimientos | ✅ (vigilar en P1) |

## D. Estructura espacial

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| D1 | **Dónde nace el hijo** | pegado al padre (a 2 radios) | Crea vecindarios de parientes (aislamiento por distancia). Eso favorece la cooperación y la señal, pero la competencia local entre parientes puede anularlo. Cambiarlo más tarde cambiaría toda la evolución social | wright1943isolation, taylor1992viscous, west2002kincompetition, werfel2015death | P0-feliz-nacer-azar (✅ 5 mundos) y control (✅ 1 mundo, idéntico bit a bit). **En P0 no cambia nada genético** (5/5 idénticos); solo el parentesco del vecindario: junto al padre, 22–62 veces el global; al azar, ≈ 1. **Responsable (19-10, 11:15): junto al padre por ahora; las dos opciones se prueban en el peldaño social** | ✅ ⏭ social |
| D2 | **Tamaño del mundo** | 1.024 × 1.024 | Sin comida ni interacción no cambia nada | — | Ninguna en P0 | ⏭ P2 (densidad de comida) |

## E. Codificación del cerebro

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| E1 | Codificación indirecta (CPPN → pesos) | CPPN, al estilo HyperNEAT | Rinde mejor cuanto más regular es el problema y peor en problemas irregulares. Es una decisión de fondo: cambiarla rompe todo | stanley2009hyperneat, clune2011indirect | No se puede juzgar sin selección. Se mantiene por bibliografía | ✅ 📚 |

## Plan para cerrar P0

1. **Cola solo de P0 (✅ terminada el 19-10 a las 12:02, `scratchpad/p0_solo.sh`, decisión del 18-10 a las 22:44):** A1 → A3 → A2 → B1 → D1 → C1. Son 36 mundos más, unas 19 h, hasta el 19-10 por la tarde. Sin E2 ni otras fases.
2. **Análisis sin GPU (📋):** A4, A5, A7 y C4, con los datos de P0 que ya existen.
3. **B1 y D1** ya están implementados (rama `escalera-p0y`, ADR-017) y en la cola.
4. **Decisiones por bibliografía (📚):** C2, A6, B2 y E1.
5. **A2, A3 y B1 en P1 (responsable, 19-10, 23:39):** decidir caso a caso; lo que P1 no pueda juzgar (en P1 la selección solo quita) se prueba en P2 antes de fijarlo.
6. **Integración:** al cerrar P0, unir las ramas `escalera`, `escalera-mut`, `escalera-p0x`, `escalera-p0y` y `escalera-p0z` en un sustrato único, con tests y determinismo, antes de P2.
7. **Criterio de cierre:** todas las filas en ✅ o ⏭. Las decisiones quedan en una ADR de cierre de P0, que fija la "física" de la herencia para toda la escalera.


## Resultados

### 18-10-2026, 23:18 · P0-feliz completo (mutación de siempre, 5 mundos) y análisis sin GPU

Ventana de las épocas 151–300; los valores son por semilla, s0 a s4.

- **A1 · neuronas:** 24,1 · 23,8 · 28,9 · 21,0 · 24,5. Siguen creciendo (+4,6 a +11,0 por 100 épocas). En la época 300 la media es 25–35 y el máximo 42–47.
- **A2 · CPPN:**
  - nodos ocultos de 0,33 a 10,3–12,7;
  - aristas de 49 a 64–73;
  - en la época 300, **entre el 8 y el 34 % de los bichos tienen la CPPN en su techo (18 nodos ocultos)**. El techo de la CPPN ya frena el sesgo.
- **A3 · tasas (época 300):** la mediana de σ va de 0,013 a 0,055 y la de la tasa estructural de 1,05 a 2,58 según el mundo. Sin selección, **cada mundo acaba con un régimen de mutación distinto solo por azar**, y eso añade ruido a todas las comparaciones entre mundos.
- **A4 · cuánto se muta:** la distancia genética media sube casi en línea recta, de 10,5 a 49,0 (continua) y de 34 a 135 (estructural) en s0. Es la deriva neutral y no satura. **P0 no puede decir si es "demasiado"**: hace falta selección (carga mutacional) → se prueba en la entrada de P1.
- **A5 · techo:**
  - **neuronas:** ningún bicho pasa de 56 de 64 (máximo 47); el techo de neuronas no limita en 300 épocas;
  - **CPPN:** sí limita (ver A2).
- **A7 · f16:** el redondeo a f16 **borra entre el 6 y el 10 % de las pequeñas perturbaciones de los pesos**. Es un suelo oculto de la mutación, mayor cuanto menor es σ y cuanto mayor es el peso.
- **C4 · tope de nacimientos:**
  - en P0 se alcanza en **todos** los pasos con nacimientos (32 justos), pero porque la población muere y renace en **cohortes sincronizadas de 32**: el arranque simultáneo, la vida fija y el tope fabrican una "cinta transportadora" de 128 cohortes;
  - no se pierden nacimientos (32 mueren y 32 nacen);
  - riesgo para P1+: tras una mortandad grande, la recuperación quedaría limitada a 32 por paso. Hay que vigilarlo en P1.

### 19-10-2026, 03:08 · A1: P0 con mutación neutral y terrestre (10 mundos)

La cola terminó a las 02:56. Ventana de las épocas 151–300; los valores son por semilla, s0 a s4. Datos en `runs/fase1d/_analisis_A1.json`, `_host_P0-feliz-neutral.json`, `_host_P0-feliz-terrestre.json` y `_dist_neuronas.json`.

**Neuronas ocultas, media tardía:**

| Física | s0 | s1 | s2 | s3 | s4 | En la época 300 |
|---|---|---|---|---|---|---|
| nest (la de siempre) | 24,1 | 23,8 | 28,9 | 21,0 | 24,5 | 25–35 de media; siguen creciendo |
| neutral | 8,0 | 7,9 | 8,0 | 8,0 | 8,8 | 6,1–11,2 de media, desviación típica de 4,5 a 7,7; entre el 3 y el 8 % sin neuronas ocultas |
| terrestre | 1,6 | 1,7 | 0,8 | 1,3 | 1,9 | 0,7–1,3 de media; **entre el 51 y el 67 % sin neuronas ocultas**; máximo de 8 a 12 |

**Contrastes prerregistrados (ADR-015):**
- neutral < nest: **5/5** (p = 0,031), con diferencias de −13,0 a −20,9 neuronas;
- terrestre < neutral: **5/5** (p = 0,031), con diferencias de −6,2 a −7,2.

**Lectura:**
- **nest** infla el cerebro sin que sirva para nada. Es un sesgo de la mutación, no de la selección.
- **neutral** conserva la media en el punto de partida (8) y solo ensancha la distribución por deriva: el tamaño del cerebro queda libre para que lo decida la selección.
  - Matiz: el suelo en 0 rebota, así que a muy largo plazo la media sube despacio (s4: +3,4 por 100 épocas). Hay que vigilarlo en peldaños largos.
- **terrestre** vacía el cerebro en 300 épocas. Con selección, solo sobrevivirían las neuronas cuya ventaja supere la barrera de la deriva (lynch2016driftbarrier). Es el modo "procariota", de genoma compacto (mira2001deletional, kuo2009deletional).

**Control:** la CPPN, el cuerpo, las tasas de mutación, f16 y los nacimientos son **idénticos** en las tres físicas (mismo valor en cada semilla). La física de neuronas solo cambia las neuronas: la comparación es limpia.

**Para la decisión:**
- desde P1, cada neurona cuesta energía (`C_NEURON` = 0,02 por paso; "tejido caro", aiello1995expensive);
- con la física neutral, la presión hacia cerebros pequeños vendría del mundo y no de la mutación;
- con la terrestre, las dos presiones se sumarían.

A6 (genoma inicial) se decide con A1: con la física neutral, las 8 neuronas iniciales son el centro de la deriva.

### 19-10-2026, 07:13 · A3 (tasas fijas) y A2 (CPPN neutral), 10 mundos

Los bloques terminaron a las 04:48 y a las 06:36. Ventana de las épocas 151–300; los valores son por semilla, s0 a s4. Datos en `runs/fase1d/_analisis_A2A3.json`, `_host_P0-feliz-tasas-fijas.json`, `_host_P0-feliz-cppn-neutral.json` y `_dist_cppn.json`.

**A3 · tasas fijas** (σ = 0,05 y tasa estructural = 1 en todos los bichos; neuronas y CPPN con la mutación de siempre):
- neuronas ocultas, media tardía: 23,7 · 21,4 · 23,4 · 20,9 · 22,3, frente a 24,1 · 23,8 · 28,9 · 21,0 · 24,5 en P0-feliz;
  - contraste prerregistrado (ADR-016), menos neuronas que P0-feliz: **5/5** (p = 0,031). Pero el efecto es pequeño: de −0,05 a −5,5;
  - la deriva de las tasas solo explica una parte pequeña del crecimiento; la mayor parte viene de la física de las neuronas (A1);
- CPPN en su techo en la época 300: entre el 3 y el 14 % (entre el 8 y el 34 % con las tasas como gen);
- **f16 (A7): con σ fija en 0,05, el redondeo solo borra el 0,7 % de las perturbaciones** (entre el 6 y el 10 % cuando σ deriva hacia abajo). El problema de f16 es sobre todo una consecuencia de que σ derive. Con tasas fijas, f16 basta;
- todos los mundos mutan igual: desaparece el ruido entre mundos que añadían las tasas al azar.

**A2 · CPPN neutral** (añadir y quitar aristas al 3,5 %, dividir y quitar nodo al 2 %; neuronas y tasas como siempre):
- nodos ocultos de la CPPN, media tardía: 1,6 · 1,6 · 2,9 · 2,0 · 3,0, frente a 10,3–12,7 con la de siempre;
  - contraste prerregistrado: **5/5** (p = 0,031);
  - **nadie toca el techo** (como mucho, un 0,1 % en la época 300). Con esta física, el techo de la CPPN (A5) deja de ser un problema;
- **pero pierde aristas**: la media baja de 48 a 33–38 en la ventana y a 26–35 en la época 300. Entre el 0 y el 10 % de los bichos tienen 10 aristas o menos, y el mínimo es de 2.
  - Causa: la CPPN mínima empieza con las 48 aristas posibles entre entradas y salidas (añadir a menudo no encuentra hueco), y quitar un nodo se lleva sus aristas (dos o más) mientras que dividir solo suma una neta.
  - Igual que con las neuronas, el punto de partida y las reglas empujan solos. Una CPPN casi sin aristas da pesos casi constantes: un cerebro sin forma;
- la física de la CPPN no cambia las neuronas: `hidden_mean` sale idéntico al de P0-feliz en cada semilla (control limpio).

**Para decidir:**
- **A3:** fijar las tasas en P0 elimina una deriva sin selección y el ruido entre mundos, y resuelve f16. Dejarlas como gen solo tiene sentido con selección (en la Tierra, la selección baja la tasa hasta la barrera de la deriva, lynch2016driftbarrier).
- **A2:** la CPPN neutral resuelve el inflado y el techo, pero necesita un ajuste para no vaciarse de aristas (por ejemplo, que quitar un nodo deje reconectadas sus aristas, o equilibrar añadir y quitar contando las aristas que arrastra cada operación).
- **A7** se decide con A3: con tasas fijas, f16.

### 19-10-2026, 08:50 · B1: P0 con reproducción sexual (5 mundos)

El bloque terminó a las 08:35 (entre 0,38 y 0,44 h por mundo; población llena). Ventana de las épocas 151–300, con el valor de la época 300 entre paréntesis. Datos en `runs/fase1d/_analisis_B1.json` y `_b1_cppn.json`.

| Medida | Asexual (P0-feliz) | Sexual |
|---|---|---|
| Neuronas ocultas | 21,0–28,9 (25,3–35,4) | 26,4–28,4 (29,4–34,1): algo más en 4 de 5; el cruce no cambia mucho el tamaño, como se esperaba |
| Nodos ocultos de la CPPN | 10,3–12,7 (11,9–16,5) | 12,5–15,0 (16,3–16,9, cerca del techo de 18) |
| Aristas de la CPPN | 64–73, y suben | 44–46, y bajan (≈ 41) |
| **Nodos de la CPPN sin ninguna salida** (época 300) | 3–5 % | **83–88 %** |
| Aristas directas entre entradas y salidas | 22–28 | 14–17 |
| Distancia genética estructural | 122–152, y sube (135–168) | 112–117, estancada (111–115) |
| Distancia genética continua | 23–41 | 34–41 |
| Clados vivos | 540–740 | 98–119 |
| Parentesco local frente a global | — (se mide en D1) | 0,24–0,34 frente a 0,010–0,011 |

**Lectura:**
- **El cruce, tal como está programado, destroza la receta del cerebro.** Cada nodo de la CPPN viene de un progenitor junto con sus aristas de *entrada*. Pero sus aristas de *salida* están en las columnas de otros nodos, que la mitad de las veces vienen del otro progenitor. Así, casi todos los nodos ocultos se quedan sin salida: son peso muerto. Se acumulan sin que nadie lo note (cerca del techo), y la receta se reduce a las aristas directas.
- La causa de fondo: **un mismo índice no significa lo mismo en dos linajes.** Tras cientos de generaciones, el nodo 10 de un bicho y el nodo 10 de otro nacieron de divisiones distintas. Es el problema de las "convenciones en competencia", que NEAT resolvió con marcas históricas (números de innovación) que identifican cada gen por su origen (stanley2002neat). Aquí los índices se usaron como si fueran esas marcas, y no lo son.
- **La recombinación mantiene unida a la población:** la distancia estructural deja de crecer y aparecen muchos menos clados nuevos. Es lo esperado: el sexo mezcla los linajes (felsenstein1974recombination).
- **Parentesco espacial fuerte:** un vecino es del mismo clado 25–35 veces más a menudo que un bicho al azar. Es la línea de base para D1.

**Para decidir B1:** el resultado no juzga el sexo, sino el operador de cruce. Opciones:
1. **cruce por bloques:** la receta del cerebro (CPPN) entera de un progenitor, y las neuronas, el cuerpo y los genes de vida mezclados. Es sencillo y no rompe nada; se parece a genes ligados en un cromosoma;
2. **marcas históricas al estilo NEAT:** cada arista y cada nodo llevan un número de origen y se alinean por él. Es lo correcto según la bibliografía, pero cambia el formato del genoma (versión mayor del sustrato);
3. seguir **asexual** y dejar el sexo para más adelante, con el riesgo de invalidar lo anterior.

### 19-10-2026, 11:10 · D1: el hijo nace al azar (5 mundos) y control (1 mundo)

El bloque terminó a las 10:50 (0,39 h por mundo; población llena). Datos en `runs/fase1d/_analisis_D1.json` (medidas por época) y `_analisis_D1_kin.json` (parentesco calculado a posteriori desde los checkpoints de P0-feliz, que no lo medía).

| Medida (época 300) | Junto al padre (P0-feliz) | Al azar |
|---|---|---|
| Neuronas, receta, distancias genéticas, clados | — | **idénticas bit a bit** en los 5 mundos |
| Movimiento y conducta (empuje, novedad, agregación) | — | distintos (cada bicho ve otro entorno) |
| Parentesco local (vecino del mismo clado) | 0,17–0,34 (épocas 100–200: 0,30–0,47) | 0,004–0,010 |
| Parentesco global (dos bichos al azar) | 0,004–0,010 | 0,004–0,010 |
| Cociente local / global | **22–62** (5/5) | **1,00–1,03** (5/5) |

- **Control** (P0-feliz-control-kin s0): idéntico a P0-feliz s0 en todas las medidas salvo el tiempo de reloj. La medida de parentesco solo observa.
- **Lectura:** en P0 nadie interactúa ni hay selección, y quién se reproduce no depende de dónde esté. Por eso el lugar de nacimiento no puede cambiar la genética: solo reparte a los parientes por el mapa. Nacer junto al padre crea vecindarios de parientes (aislamiento por distancia, wright1943isolation); nacer al azar los borra del todo.
- **Por qué importa más adelante:** en los peldaños sociales (señal, ataque), el parentesco local puede favorecer la ayuda entre vecinos, pero la competencia entre parientes puede anularlo (taylor1992viscous, west2002kincompetition).
- **Propuesta:** mantener «junto al padre» (lo terrestre, sin coste en P0) y conservar «al azar» como interruptor de control para los peldaños sociales.
- **Decisión del responsable (11:15):** se mantiene «junto al padre» y la elección se prueba con las dos opciones cuando haya señal o ataque. Para P0, D1 queda cerrado.

### 19-10-2026, 12:04 · C1: P0 con 1.024 bichos (5 mundos)

La cola de P0 terminó a las 12:02 (0,22 h por mundo frente a 0,39 h con 4.096). Datos en `runs/fase1d/_analisis_C1.json`. Valores de la época 300 (media ± desviación entre semillas).

| Medida | N = 4.096 (P0-feliz) | N = 1.024 |
|---|---|---|
| Neuronas ocultas | 30,1 ± 3,9 | 29,3 ± 4,5 |
| Nodos ocultos de la CPPN | 14,5 ± 1,8 | 12,8 ± 2,6 |
| Distancia genética continua | 39,9 ± 10,7 | 32,9 ± 6,7 |
| Distancia genética estructural | 152 ± 14 | 122 ± 20 |
| Clados vivos | 540–740 | 32–100 |
| Diversidad de clados (Shannon) | 5,4–6,0 | 3,2–3,6 |

- **Lectura:** sin selección, el tamaño medio del cerebro lo fija el sesgo de la mutación, no el tamaño de la población (lo esperado por la teoría neutral). N cambia sobre todo la **variedad**: con 1.024 hay muchos menos linajes, menos distancia entre bichos y algo más de diferencia entre mundos. El efecto importante de N (que el azar tape ventajas menores que ~1/N; ohta1973nearlyneutral) solo se ve con selección.
- **Pausa de capacidad** en P0-feliz-N1024 s0, en la última época (300): `patch_gain` y `maze_gain` = 0,25 (umbrales 0,20 y 0,25), con un 100 % de éxito de 64 sondas frente a una línea de base aleatoria del 75 %. Sin selección no puede haber capacidad evolucionada: es otro falso positivo de una prueba con poco margen sobre el azar, como los de E0 y E2. El mundo había terminado; no se crea `CAPABILITY_REVIEW.json`.
- **Decisión del responsable (12:04):** el tope de población se queda en 4.096: más variedad y selección más fina, por 1,8 veces más tiempo por mundo.

### 19-10-2026, 15:14 · B1 repetido: sexo con la receta entera (5 mundos)

El bloque terminó a las 14:01 (0,39–0,41 h por mundo; población llena). Rama `escalera-p0z`, sustrato 2.5.0 (ADR-018). Datos en `runs/fase1d/_analisis_B1b.json` y `_b1b_cppn.json`. Ventana de las épocas 151–300, con la época 300 entre paréntesis.

| Medida | Asexual | Sexual, cruce por índice (con error) | **Sexual, receta entera** |
|---|---|---|---|
| Nodos de la CPPN sin salida (época 300) | 3–5 % | 83–88 % | **3–8 %** |
| Aristas de la CPPN | 64–73 (66–81) | 44–46 (≈ 41) | **69–73 (72–78)** |
| Aristas directas entrada→salida | 22–28 | 14–17 | **20–23** |
| Neuronas ocultas | 21,0–28,9 (25–35) | 26,4–28,4 (29–34) | 26,7–30,1 (31–35) |
| Distancia estructural | 122–152 (135–168) | 112–117, estancada | **148–156 (152–163)**, sube |
| Distancia continua | 23–41 | 34–41 | 37–45 |
| Parentesco local / global (época 300) | 0,17–0,34 / 0,004–0,010 | 0,26–0,36 / 0,016–0,022 | 0,29–0,46 / 0,016–0,023 |

- **El error está corregido:** la receta del cerebro queda tan conectada como sin sexo, y la variedad estructural ya no se estanca.
- **Sin selección, el sexo no cambia casi nada**, como predice la teoría neutral (la recombinación no altera la diversidad media si nadie selecciona). Su ventaja (que las mejoras se sumen en vez de competir; hill1966linkage, felsenstein1974recombination) solo puede verse con selección.
- **Ojo con los clados en los mundos sexuales:** el hijo hereda la generación mayor de sus dos padres, así que la población cruza a la vez los múltiplos de 50 generaciones y los clados se renuevan casi al mismo tiempo. La cuenta de clados en una época concreta (≈ 100–120) no es comparable con la de los asexuales; la media de la ventana sí lo es (324–362 frente a 343–356).
- **Decisión del responsable (15:14):** probarlo en P1 (P1-peaje-sexual-bloques, 5 mundos, cola `p1z.json` de la rama `escalera-p0z`, `scratchpad/tras_p1.sh` tras `tras_p0.sh`). Después se decide si basta el supergén o hacen falta marcas históricas.

### 19-10-2026, 23:28 · A1 con selección: P1 con las tres físicas (15 mundos)

P1-peaje (nest, referencia) terminó a las 23:22; neutral y terrestre, a las 20:12. Todos llenos (4.096), sin extinciones ni pausas. Datos en `runs/fase1d/_analisis_A1_P1.json` y `_ladder_P1.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | nest | neutral | terrestre |
|---|---|---|---|
| Neuronas ocultas | 0,11–0,42 (0,05–0,10) | 0,05–0,12 (0,04–0,11) | 0,05–0,10 (0,04–0,10) |
| Empuje | 0,004–0,10 | 0,02–0,08 | 0,02–0,11 |
| Sinapsis | 1–398 | 16–632 | 23–187 |
| Distancia estructural | 13–27 | 16–65 | 55–89 |
| En P0 (sin selección), neuronas | 21–29, y crecen | 7,9–8,8 | 0,8–1,9 |

- **Pregunta prerregistrada de P1 (¿funciona la selección? menos empuje):** se cumple 5/5 con las tres físicas (p = 0,031 en cada una).
- **La selección se impone a la física de la mutación:** con peaje y sin comida, pensar y moverse solo cuestan, y las tres acaban casi sin cerebro y quietas. Nest deja algo más (5/5 por encima de neutral en la ventana, < 0,4 neuronas): su empuje hacia arriba se nota incluso con selección.
- **Decisión del responsable (23:28):** física **neutral** para toda la escalera (A1) y genoma inicial de 8 neuronas (A6, centro de la deriva neutral). Es la hipótesis nula: el cerebro solo crece si la selección lo pide. Al terminar la escalera, los peldaños clave se repetirán con la **terrestre** como prueba de robustez. No es "la Tierra" en general: en bacterias domina la pérdida de ADN (kuo2009deletional, mira2001deletional), pero la duplicación es la gran fuente de genes nuevos (lynch2000duplicate) y en poblaciones pequeñas el genoma crece (lynch2003origins).
- **Nota:** las pruebas de P1 que siguen en cola (tasas fijas, CPPN neutral, sexo) usan nest y se comparan con P1-peaje (nest), emparejadas por semilla. La comparación es válida; la física elegida se aplicará desde el cierre de P0.

