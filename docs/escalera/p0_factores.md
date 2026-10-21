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
| A2 | Física de la mutación de la **CPPN** | añadir 5 %, quitar 2 %, dividir 3 %, quitar nodo 1 % | En P0 sus nodos pasan de 0,35 a ~11: es el mismo sesgo, en la receta del cerebro | stanley2002neat, langdon1998bloat, banzhaf2002bloat, kuo2009deletional | P0-cppn-neutral (✅ 5/5): ya no se infla, pero pierde aristas. **Responsable (19-10, 07:22): decidir tras P1-peaje-cppn-neutral.** P1 hecho (20-10, 07:06): la de siempre se infla incluso con selección; la neutral no, y con selección conserva las aristas. **Responsable (20-10, 07:10): neutral corregida** (añadir y quitar equilibrados; se comprueba en P0 en la integración) | ✅ neutral corregida |
| A3 | **Tasas de mutación**: gen o constante | σ autoadaptativa y tasa estructural como gen (deriva +75 % en 300 épocas) | Sin selección, la tasa sube por el suelo en 0. En la Tierra, la selección la baja hasta la barrera de la deriva | lynch2016driftbarrier, sniegowski1997mutators, beyer2002es | P0-tasas-fijas (✅ 5/5, efecto pequeño). Si se mantiene como gen, el ruido pasa a escala logarítmica (sin artefacto del suelo). **Responsable (19-10, 07:20): decidir tras P1-peaje-tasas-fijas frente a P1-peaje.** P1 hecho (20-10, 02:32): con selección, σ baja 10 veces y la tasa estructural de 8 a 20. **Responsable (20-10, 07:01): fijas; en P2, gemelo con las tasas como gen** | ✅ fijas (P2: gemelo) |
| A4 | **Cuánto** se muta: σ inicial 0,05, τ = 0,2, 11 % de cambios estructurales por hijo | sin contrastar | Demasiada mutación destruye la información más deprisa de lo que la selección la fija (umbral de error). Demasiado poca estanca | eigen1971selforganization, lynch2016driftbarrier | En P0: velocidad de divergencia neutral (`genome_distance`). El juicio necesita P1. P1 con tasas fijas: la selección limpia en 5/5 y la carga es pequeña (vida −1 %). **Responsable (20-10, 09:28): se mantienen σ = 0,05 y tasa 1** | ✅ 0,05 y 1 (gemelo de P2: σ baja 3–8 veces, pero sin vivir más; se mantiene) |
| A5 | **Techo** del genoma: 64 neuronas y 32 nodos de CPPN | fijo | Con nest, el equilibrio neutral (~43) queda cerca del techo. La evolución abierta necesita poder crecer sin un límite artificial | taylor2016oee, stanley2002neat | Analizar en P0 qué fracción de bichos toca el techo con cada física. Hecho: el de neuronas no limita con ninguna física; el de la CPPN sí (8–34 %), salvo con la CPPN neutral | ✅ se mantiene (con A1 y A2 neutrales nadie lo toca; vigilarlo en P2) |
| A6 | **Genoma inicial**: 8 neuronas y CPPN mínima | "empezar mínimo" (NEAT) | Con la física terrestre, el punto de partida pesa: deriva hacia 0 | stanley2002neat, lynch2003origins | Se decide junto con A1: con la física neutral, el tamaño inicial es el punto alrededor del cual deriva | ✅ con A1: 8 neuronas, centro de la deriva neutral |
| A7 | **Precisión** del genoma: los pesos se guardan en f16 | f16 | Un cambio menor que la resolución de f16 desaparece al guardarse: es otra "física" oculta, un suelo para σ | — (es técnico) | Medir en P0 cuántas mutaciones se pierden por redondeo. Hecho: entre el 6 y el 10 % (9–22 % en P1 con σ como gen; 0,7 % con σ fija) | ✅ f16, con A3 (tasas fijas) |

## B. Reproducción y herencia

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| B1 | **Sexo** (recombinación) | solo asexual; el sexo estaba previsto para la fase 3 | Sin recombinación, las mejoras compiten en lugar de sumarse (interferencia clonal) y las mutaciones dañinas se acumulan (trinquete de Muller). En poblaciones grandes, el sexo acelera mucho la adaptación. Añadirlo más tarde invalidaría todo lo anterior | muller1964ratchet, felsenstein1974recombination, colegrave2002sex, mcdonald2016sex; ligamiento: hill1966linkage, thompson2014supergenes, charlesworth2000ydegeneration, birky1995uniparental | P0-feliz-sexual (✅ 5 mundos): **el cruce por índice rompe la receta del cerebro** (entre el 83 y el 88 % de los nodos de la CPPN quedan sin salida). Era un error de implementación: **corregido (ADR-018, la CPPN se hereda entera, como un supergén) y se repite** (P0-feliz-sexual-bloques). Repetición (✅ 5 mundos): la receta queda sana (3–8 % de nodos sin salida) y la variedad no se pierde. **Responsable (19-10, 15:14): decidir tras P1-peaje-sexual-bloques** (supergén o marcas históricas) | ✅ asexual (P2: el sexo gana en 4/5 hasta la época 300 y en 3/5 hasta la 600) |
| B2 | **Herencia de lo aprendido** | darwiniana: el hijo nace con los pesos innatos, no con los aprendidos | Heredar lo aprendido (lamarckiano) acelera en mundos **estables** (Ackley y Littman 1994), pero cae más en óptimos locales (Whitley et al. 1994) y es **peor cuando el mundo cambia**: hereda lo que servía en un mundo que ya no existe (Sasaki y Tokoro 2000). Aprender sin heredarlo también acelera la evolución (efecto Baldwin; Hinton y Nowlan 1987), según la pendiente de la ganancia (Paenke et al. 2007). Además, con una codificación indirecta (CPPN) no se puede reescribir la receta a partir de los pesos aprendidos | whitley1994lamarck, ackley1994lamarck, sasaki2000lamarck, hinton1987learning, paenke2007plasticity | Ninguna en P0 (no hay nada que aprender). La transmisión de lo aprendido entre bichos (cultura) sería un peldaño social, no genético | ✅ 📚 |
| B3 | ¿Quién paga la energía del hijo? | dotación regalada (P0, P1) o cedida por el padre (P3+) | — | — | Es de P3. P3-escalera (21-10, 11:53): con el padre pagando no hay extinción, pero el mundo se sigue llenando (4.096); el freno es el tope, no la comida. P3-escaso (20:01, ½ de comida): la comida frena (población 2.516–2.690, 5/5); la selección elige hijos baratos (umbral 10–19, fracción 0,26–0,40) | 🔬 cedida por el padre (P3-escaso ✓); pendiente del responsable |

## C. Demografía

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| C1 | **Tamaño de la población** (tope) | 4.096 | El azar compite con la selección: una ventaja menor que ~1/N no se impone. Las poblaciones pequeñas y las grandes llegan a la complejidad por caminos distintos. El sexo ayuda más en las grandes | ohta1973nearlyneutral, charlesworth2009ne, labar2016populations, colegrave2002sex | P0-N1024 (✅ 5 mundos): el cerebro crece igual (29 frente a 30 neuronas), pero con mucha menos variedad (32–100 clados frente a 540–740). **Responsable (19-10, 12:04): se queda en 4.096** | ✅ |
| C2 | **Muerte y vejez** | P0: vida fija de 600 pasos. Desde P1: la vejez se impone (gasto creciente desde 5.000 pasos) | En la Tierra, el envejecimiento **evoluciona**: acumulación de mutaciones (Medawar), pleiotropía antagonista (Williams), soma desechable (Kirkwood). En mundos espaciales, la muerte programada puede verse favorecida. Imponerla o dejarla evolucionar cambia la duración de las generaciones y cuánto compensa aprender | williams1957pleiotropy, kirkwood1977ageing, werfel2015death | En P0 solo reescala el tiempo. La decisión ("ley del mundo" o "gen") se toma ahora y se prueba en P1 o P2. **Responsable (20-10, 09:28): ley del mundo en toda la escalera; la vejez como gen, en un peldaño propio tras P5** | ✅ ley (gen: peldaño propio) |
| C3 | **Población inicial** (512) | 512 | Solo afecta a la primera época: el mundo se llena enseguida | — | Ninguna: irrelevante en P0 | ✅ |
| C4 | **Tope de nacimientos** por paso (32) | 32 | Si se alcanza, frena la reproducción por una razón técnica | — | Comprobar en los datos que nunca se alcanza. Hecho: se alcanza por las cohortes sincronizadas, sin perder nacimientos | ✅ (vigilar en P1) |

## D. Estructura espacial

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| D1 | **Dónde nace el hijo** | pegado al padre (a 2 radios) | Crea vecindarios de parientes (aislamiento por distancia). Eso favorece la cooperación y la señal, pero la competencia local entre parientes puede anularlo. Cambiarlo más tarde cambiaría toda la evolución social | wright1943isolation, taylor1992viscous, west2002kincompetition, werfel2015death | P0-feliz-nacer-azar (✅ 5 mundos) y control (✅ 1 mundo, idéntico bit a bit). **En P0 no cambia nada genético** (5/5 idénticos); solo el parentesco del vecindario: junto al padre, 22–62 veces el global; al azar, ≈ 1. **Responsable (19-10, 11:15): junto al padre por ahora; las dos opciones se prueban en el peldaño social** | ✅ ⏭ social |
| D2 | **Tamaño del mundo** | 1.024 × 1.024 | Sin comida ni interacción no cambia nada | — | Ninguna en P0. P2 con el examen limpio: no buscan (≤ 11 %) porque la comida cubre el 87 % del suelo. **Responsable (21-10): P2-buscar con comida dispersa (K_CUT 1,5, ADR-022).** P2-buscar (15:38): no buscan (examen 1/5); con energía regalada, la comida escasa da un mundo como P1 | ✗ P2-buscar (con hijos regalados, la comida dispersa no enseña a buscar); pendiente del responsable |

## E. Codificación del cerebro

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| E1 | Codificación indirecta (CPPN → pesos) | CPPN, al estilo HyperNEAT | Rinde mejor cuanto más regular es el problema y peor en problemas irregulares. Es una decisión de fondo: cambiarla rompe todo | stanley2009hyperneat, clune2011indirect | No se puede juzgar sin selección. Se mantiene por bibliografía | ✅ 📚 |

## Plan para cerrar P0

1. **Cola solo de P0 (✅ terminada el 19-10 a las 12:02, `scratchpad/p0_solo.sh`, decisión del 18-10 a las 22:44):** A1 → A3 → A2 → B1 → D1 → C1. Son 36 mundos más, unas 19 h, hasta el 19-10 por la tarde. Sin E2 ni otras fases.
2. **Análisis sin GPU (📋):** A4, A5, A7 y C4, con los datos de P0 que ya existen.
3. **B1 y D1** ya están implementados (rama `escalera-p0y`, ADR-017) y en la cola.
4. **Decisiones por bibliografía (📚):** C2, A6, B2 y E1.
5. **A2, A3 y B1 en P1 (responsable, 19-10, 23:39):** decidir caso a caso; lo que P1 no pueda juzgar (en P1 la selección solo quita) se prueba en P2 antes de fijarlo. ✅ Decididos el 20-10: A3 tasas fijas (07:01), A2 CPPN neutral corregida (07:10), B1 asexual (09:17). **Gemelos de P2:** tasas como gen y sexo (con tasas fijas). A4 y C2, decididos a las 09:28: **todas las filas en ✅ o ⏭**.
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

### 20-10-2026, 02:32 · A3 con selección: P1 con tasas fijas frente a P1-peaje (5 mundos)

P1-peaje-tasas-fijas (rama `escalera-p0x`) terminó a las 02:26, 0,62 h por mundo. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (nest, tasas como gen), emparejado por semilla. Datos en `runs/fase1d/_analisis_A3_P1.json`, `_host_P1-peaje.json` y `_host_P1-peaje-tasas-fijas.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | Tasas como gen (P1-peaje) | Tasas fijas | Signo |
|---|---|---|---|
| σ de los pesos, mediana en la época 300 | **0,0046–0,0069** (empieza en 0,05) | 0,05 | — |
| Tasa estructural, mediana en la época 300 | **0,05–0,13** (empieza en 1) | 1 | — |
| Neuronas ocultas | 0,11–0,42 (0,05–0,10) | 0,48–0,54 (0,49–0,56) | 5/5 más con fijas |
| Distancia estructural | 13–27 | 63–79 | 5/5 más con fijas |
| Vida media (pasos) | 521–528 | 516–518 | 5/5 menos con fijas |
| Nacimientos por época | 7.746–7.848 | 7.895–7.920 | 5/5 más con fijas |
| CPPN en el techo, época 300 | 0 % | 0–38 % | — |
| Perturbaciones borradas por f16 (A7) | **9–22 %** | 0,7 % | — |

- **Con selección, las tasas como gen bajan solas, y mucho:** σ cae unas 10 veces y la tasa estructural entre 8 y 20 veces, en los 5 mundos. En P0, sin selección, subían (σ 0,013–0,055 y tasa 1,05–2,58, por el suelo en 0). Es lo que predice la teoría para un mundo que no cambia: si casi toda mutación es dañina, la selección baja la tasa hasta la barrera de la deriva (lynch2016driftbarrier). Con las tasas como gen, el genoma aprende a mutar menos.
- **Con tasas fijas, la población carga con más mutaciones dañinas:** más neuronas que cuestan (equilibrio entre mutación y selección), más variedad estructural, vidas algo más cortas y más nacimientos. El efecto es pequeño y no amenaza a nadie (siempre 4.096).
- **Lo que P1 no puede juzgar:** en un mundo sin nada que ganar, mutar menos siempre conviene. En un mundo que cambia o con mejoras por descubrir (P2 en adelante), mutar poco frena la adaptación y los mutadores pueden ganar (sniegowski1997mutators, taddei1997mutator). Si las tasas se dejan como gen, P1 las hunde y P2 empezaría con poblaciones casi congeladas.
- **A7 depende de A3:** con σ como gen y selección, el redondeo a f16 borra entre el 9 y el 22 % de las perturbaciones de los pesos (más que en P0). Si las tasas son gen, f16 se convierte en un suelo real de la mutación; con tasas fijas, basta.
- **Decisión del responsable (07:01):** tasas **fijas** (σ = 0,05, tasa estructural = 1) en el sustrato integrado; con ellas, **f16 basta** (A7). En P2 se añade un gemelo con las tasas como gen, para ver si mutar menos frena la adaptación cuando hay algo que ganar. Si la ganara, la tasa como gen exigiría revisar A7 (precisión de los pesos).

### 20-10-2026, 07:06 · A2 con selección: P1 con CPPN neutral frente a P1-peaje (5 mundos)

P1-peaje-cppn-neutral (rama `escalera-p0x`) terminó a las 05:32. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (CPPN de siempre), emparejado por semilla. Datos en `runs/fase1d/_analisis_A2_P1.json` y `_dist_cppn_P1.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | CPPN de siempre (P1-peaje) | CPPN neutral | Signo |
|---|---|---|---|
| Nodos ocultos de la CPPN | 0,8–11,2 (1,1–12,0) | 0,4–2,7 (0,4–2,9) | 4/5 menos con neutral |
| Aristas de la CPPN | 51–61 (52–61) | 35–45 (34–45) | 5/5 menos con neutral |
| Mínimo de aristas, época 300 | 39–57 | 29–36 (nadie con 10 o menos) | — |
| Neuronas ocultas | 0,11–0,42 | 0,09–0,22 | 3/5 menos |
| Empuje, vida media y nacimientos | iguales | iguales | — |

- **La receta del cerebro no paga peaje:** en P1 cuestan las neuronas y moverse, no los nodos de la CPPN. Por eso, con la mutación de siempre, la CPPN sigue inflándose incluso con selección (hasta 12 de 18 nodos en s0) y la selección no lo corrige. Con tasas fijas (A3, ya decidido), la de siempre llega al techo en 3 de 5 mundos (27–38 % de los bichos en la época 300).
- **La neutral no se infla y, con selección, ya no se vacía:** en P0 perdía aristas (26–35 en la época 300, mínimo 2). En P1 se queda en 34–45, y nadie baja de 29: los bichos con la receta casi vacía dejan menos hijos. El sesgo hacia perder aristas sigue ahí (la media baja de 48), pero la selección lo frena.
- **No cambia nada de lo que la selección mide:** empuje, vida y nacimientos salen iguales. El cerebro no se resiente.
- **Lo que P1 no puede juzgar:** si una receta más pequeña limita construir cerebros complejos cuando compensa (P2 en adelante).
- **Bibliografía** (`docs/bibliografia/escalera/README.md`, §11): el inflado sin ganancia es un fallo conocido de los operadores (soule1998removal, langdon1998bloat). De los remedios clásicos (coste por tamaño, operadores de tamaño neutro, igualación de operadores), el que encaja con los principios es el de **operadores equilibrados** (langdon2000sizefair): la misma hipótesis nula que en A1.
- **Decisión del responsable (07:10):** CPPN **neutral corregida**: añadir y quitar aristas equilibrados, contando las que arrastra quitar un nodo, para que el tamaño esperado no cambie por sí solo. Se implementa en la rama de integración y se comprueba en P0 (5 mundos) antes de P2. Con A1 y A2 neutrales, el techo (A5) no limita; se vigila en P2. Pagar por la receta (soule1998parsimony, lynch2015bioenergetic) queda de reserva si en P2 se inflara sin motivo.

### 20-10-2026, 09:01 · B1 con selección: P1 con sexo frente a P1-peaje (5 mundos)

P1-peaje-sexual-bloques (rama `escalera-p0z`, cruce corregido de ADR-018) terminó a las 08:54, 0,67 h por mundo. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (asexual), emparejado por semilla; las dos con las tasas de mutación como gen. Datos en `runs/fase1d/_analisis_B1_P1.json`, `_host_P1-peaje-sexual-bloques.json` y `_b1_cppn_P1.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | Asexual (P1-peaje) | Sexual | Signo | Asexual con tasas fijas (A3) |
|---|---|---|---|---|
| σ, mediana en la época 300 | 0,0046–0,0069 | **0,015–0,033** | 5/5 mayor | 0,05 |
| Tasa estructural, mediana | 0,05–0,13 | **0,67–0,97** | 5/5 mayor | 1 |
| Neuronas ocultas | 0,11–0,42 (0,05–0,10) | 0,45–0,79 (0,47–0,79) | 5/5 más | 0,48–0,54 |
| Empuje | 0,004–0,10 | 0,16–0,24 | 5/5 más | 0,02–0,20 |
| Distancia genética (pesos) | 8–15 | 29–43 | 5/5 más | 14–16 |
| Distancia estructural | 13–27 | 97–116 | 5/5 más | 63–79 |
| Vida media (pasos) | 521–528 | 514–520 | 5/5 menos | 516–518 |
| Nodos de la CPPN sin salida, época 300 | 0–10 % | 3–7 % | — | — |

- **Pregunta prerregistrada de P1 (menos empuje que en P0):** se cumple también con sexo (0,16–0,24 frente a 5–7).
- **Con sexo, la selección purga peor en P1:** queda más cerebro, más movimiento, más variedad y vidas algo más cortas. La causa principal es la tasa de mutación: con sexo apenas baja (σ de 0,05 a 0,015–0,033, la tasa estructural de 1 a 0,7–1), mientras que sin sexo cae 10 veces. Es lo que predice la teoría: el cruce separa al gen que sube la tasa de las mutaciones malas que causa, y la selección deja de verlo (johnson1999mutation, lynch2010mutationrate). Por tanto, esta comparación mezcla dos cosas: el sexo y la tasa de mutación.
- **Frente al asexual con tasas fijas** (más parecido en tasas), el sexo deja algo más de cerebro y movimiento (4/5 en empuje) y mucha más variedad estructural, con tasas menores. El efecto propio del sexo existe, pero es pequeño.
- **El cruce corregido funciona:** los nodos de la CPPN sin salida son el 3–7 % (con el error eran el 83–88 %).
- **Lo que P1 no puede juzgar:** la gran ventaja del sexo, juntar en un hijo mejoras que aparecieron en bichos distintos (colegrave2002sex, hill1966linkage), necesita mejoras que ganar (P2). La ventaja de limpiar mutaciones malas (kondrashov1988deleterious) no aparece en P1.
- **Decisión del responsable (09:17):** el sustrato integrado sigue **asexual** (spec v1). En P2 se añade un gemelo con sexo (cruce corregido, ADR-018) y tasas fijas, donde puede demostrar su ventaja. El cruce queda en el código como opción (`REPRODUCTION`). Si en P2 el sexo gana, se adopta desde P2 y se anota que P0 y P1 fueron asexuales; los dos peldaños son de purga, donde el sexo apenas cambia la respuesta a su pregunta.

### 20-10-2026, 09:28 · A4 y C2 decididos: P0 cerrado

- **A4 · cuánto se muta:** se mantienen σ = 0,05 y tasa estructural = 1 (un 11 % de cambios estructurales por hijo). En P0 la variedad crece sin estancarse; en P1, con esas tasas fijas, la selección sigue limpiando en 5/5 y la carga es pequeña (vida un 1 % más corta). No hay señal de exceso (umbral de error, eigen1971selforganization) ni de defecto. Se revisa si el gemelo de P2 con tasas como gen las lleva lejos de estos valores.
- **C2 · muerte y vejez:** ley del mundo en toda la escalera (P0: vida fija de 600 pasos; desde P1, coste creciente desde 5.000 pasos). Es la hipótesis nula y un interruptor menos. La vejez como gen (williams1957pleiotropy, kirkwood1977ageing, werfel2015death) será un peldaño propio cuando aprender compense (tras P5), con su pregunta prerregistrada.
- **Todas las filas están en ✅ o ⏭.** Faltan la ADR de cierre de P0 y la rama de integración (plan, puntos 6 y 7).

### 20-10-2026, 12:31 · Comprobación de la integración (ADR-019): P0-escalera (5 mundos) y control

- **Control (10:17–10:39):** la rama `escalera-int`, con la física de la spec v1 elegida a mano, coincide **bit a bit** con P0-feliz s0: 0 diferencias en 300 épocas (todas las medidas salvo el tiempo de cálculo). Unir las ramas no cambió nada de lo que ya había.
- **P0-escalera (10:39–12:28), 5 mundos con la física nueva** (época 300; entre paréntesis, media de 151–300):
  - **neuronas ocultas:** 6,5–8,8 (7,4–9,1), cerca de las 8 iniciales; P0-feliz llegaba a 25–35. Ningún bicho cerca del techo de 64 (máximo 22);
  - **CPPN:** 48–54 aristas y 4,0–5,7 nodos ocultos; **aristas − nodos = 44–49 (media 46,5)**, como en la deriva pura medida sin selección (47–48). No se hincha como la de siempre (64–81 aristas, 12–16 nodos) ni se vacía como la neutral (26–35 aristas). Nodos en el techo: 0–0,2 %;
  - **σ = 0,05 y tasa = 1** en todos los bichos (0,04999 por el redondeo a f16). El redondeo borra un 0,7 % de las perturbaciones de pesos;
  - la distancia genética de pesos baja a 15 (22–41 en P0-feliz) y la estructural queda en 76–105, como con la CPPN neutral. El empuje (5–8) es como en P0-feliz: sin selección, nada lo mueve.
- **Veredicto: la comprobación pasa en los cuatro criterios del ADR-019.** El sustrato 2.6.0 es la base de P2. Datos: `runs/fase1d/_analisis_P0int.json`, `_host_P0-escalera.json`.

### 20-10-2026, 16:44 · P1-escalera: P1 con la física integrada (5 mundos)

Criterio prerregistrado en `diseno.md` v0.5. Medias de las épocas 151–300:

| Medida | P0-escalera | P1-escalera | P1-peaje-tasas-fijas (reglas viejas) |
|---|---|---|---|
| Empuje (**primaria**: menor) | 6,4–8,1 | **0,05–0,13 (5/5)** | 0,02–0,20 |
| Neuronas ocultas | 7,4–9,1 | **0,19 (5/5)** | 0,48–0,54 |
| Masa | 1,3–2,2 | 0,27 (5/5) | 0,26–0,29 |
| Vida media | 600 (fija) | 523–524 | 516–518 |
| Nodos de la CPPN | 3,7–4,8 | 3,7–5,1 | 6,5–14,4 |
| Aristas − nodos de la CPPN | 46–47 | 43–48 | 52–58 |
| Distancia estructural | 78–100 | 57–67 | 63–79 |

- **P1 funciona con la física de la escalera:** primaria y secundarias en 5/5 (prueba de signos, p = 0,031). VA = 0 en las 8 sondas de cada mundo (no hay nada que aprender) y la población siempre llena (4.096).
- **Lo que cambia frente a las reglas viejas:** el cerebro se vacía más (0,19 frente a 0,5 neuronas con tasas fijas), porque la mutación neutral ya no añade neuronas inútiles; la CPPN no se hincha con selección (aristas − nodos como sin selección), y los mundos son muy parecidos entre sí.
- **Carga de las tasas fijas:** la vida (523–524) queda entre la de P1-peaje con tasas como gen (521–528) y la de las tasas fijas con la física vieja (516–518). El gemelo de P2 la medirá con comida.
- Datos: `runs/fase1d/P1-escalera`, `_analisis_P1int.json`. **P1-escalera es el padre de P2.**

### 21-10-2026, 01:20 · P2 completo: base y dos gemelos (15 mundos)

Criterios prerregistrados en `diseno.md` v0.6. Medias de las épocas 151–300, emparejadas por semilla (s0–s4). 8 mundos se pausaron por la batería y se reanudaron según el ADR-020 (la ventana 151–300 está completa en los 15).

| Medida | P1-escalera | **P2-escalera** | P2-tasas-gen | P2-sexual |
|---|---|---|---|---|
| Vida media (**primaria**: mayor que en P1) | 523–524 | **3.578–7.585 (5/5)** | 2.791–7.694 (3/5 frente a la base) | 5.248–6.711 (4/5 frente a la base) |
| Empuje (secundaria) | 0,05–0,13 | **9,0–10,8 (5/5)** | 8,4–9,6 | 8,7–9,3 |
| Comida ingerida por época (miles) | 0 | 345–482 | 301–436 (3/5) | 378–423 (3/5) |
| Neuronas ocultas (51–100 → 151–300) | 0,19 | 7,2–7,7 → 4,1–6,4 | 7,0–7,8 → 3,0–6,7 | 7,5–7,8 → 3,8–5,7 |
| Neuronas ocultas en la época 300 | — | 2,2–5,5 (máx. 6–10) | 1,4–6,1 | 2,5–3,9 |
| Nodos ocultos de la CPPN | 3,7–5,1 | 0,5–0,9 | 0,7–2,5 | 0,3–1,1 |
| Aristas − nodos de la CPPN | 43–48 | 47–50 | 46–49 | 47–49 |
| VA de la ingesta (gemelo congelado) | 0 | −0,016 a −0,004 | −0,065 a +0,006 | −0,010 a +0,004 |
| Muertes por hambre / por vejez (por época) | 7.810 / 0 | 223–823 / 318–344 | 216–1.207 / 288–356 | 289–453 / 316–332 |
| Generación máxima | 642–645 | 61–80 | 61–88 | 135–153 |
| σ y tasa estructural (época 300) | 0,05 / 1 | 0,05 / 1 | **0,006–0,019 / 1,08–1,45** | 0,05 / 1 |

- **P2 funciona:** con comida en manchas quietas, los bichos viven entre 7 y 14 veces más que en P1 y se mueven 100 veces más (primaria y secundaria en 5/5, p = 0,031). Mueren de vejez unos 330 por época: casi la mitad de las muertes.
- **El cerebro no se vacía como en P1, pero tampoco crece:** tras las 8 neuronas iniciales, baja despacio (7,6 → 4–6 → 2–5 en la época 300). La CPPN pierde casi todos sus nodos ocultos y conserva las aristas. La prolongación hasta 600 épocas dirá si se estabiliza.
- **Buscar comida es innato, no aprendido:** VA ≈ 0 en los 15 mundos (el gemelo sin plasticidad come lo mismo). La batería lo confirma: llegan a la mancha lejana el 88–98 % de las veces (el azar, el 73–80 %).
- **Gemelo de tasas como gen (A4):** la selección **baja σ entre 3 y 8 veces** (de 0,05 a 0,006–0,019) y **sube la tasa estructural** (de 1 a 1,08–1,45) en 5/5, pero no viven más ni comen más que la base (3/5 en las dos). Con σ tan baja, el redondeo a f16 borra el 2–6 % de las perturbaciones (0,5 % con σ fija). Según la regla prerregistrada (revisar A4 solo si además viven más), **A4 se mantiene**.
- **Gemelo sexual (B1):** vive más que la base en 4 de 5 mundos (s3 no) y come más en 3 de 5. **No llega al 5/5 prerregistrado: se sigue asexual.** Es más regular entre mundos (vida 5.248–6.711 frente a 3.578–7.585), con menos muertes por hambre en 4/5 y el doble de generaciones (el hijo hereda la generación del padre más avanzado, así que el contador corre más; no es más reproducción: nacen menos). Indicio, no decisión: la prolongación a 600 épocas lo mira con más tiempo.
- Datos: `runs/fase1d/P2-escalera*`, `_analisis_P2int.json`, `_host_P2-escalera*.json` (`scratchpad/p2_an.py`, `p2_host.sh`).

### 21-10-2026, 06:39 · P2 hasta 600 épocas: base y sexual (10 mundos)

Copias de P2-escalera y P2-escalera-sexual continuadas desde la época 300 (`scratchpad/p2largo.sh`, 01:11–06:39; umbral de mancha y laberinto a 0,4, ampliación del ADR-020). Ningún mundo se pausó ni se extinguió. Medias por ventana (rango de los 5 mundos):

| Medida | Mundo | 51–150 | 151–300 | 301–450 | 451–600 |
|---|---|---|---|---|---|
| Neuronas ocultas | base | 6,9–7,6 | 4,1–6,4 | 1,9–4,4 | **1,5–2,9** |
| | sexual | 7,0–7,6 | 3,8–5,7 | 2,1–3,0 | **1,5–2,3** |
| Empuje | base | 9,7–11,3 | 9,0–10,8 | 8,4–9,8 | 8,0–8,7 |
| | sexual | 9,5–10,2 | 8,7–9,3 | 8,0–8,6 | 7,6–8,1 |
| Masa | base | 0,66–0,89 | 0,41–0,68 | 0,34–0,52 | 0,31–0,40 |
| Vida media | base | 3.540–5.535 | 3.578–7.585 | 3.319–8.026 | 4.185–9.410 |
| | sexual | 4.731–6.113 | 5.248–6.711 | 5.837–8.864 | 5.148–10.349 |
| Comida por época (miles) | base | 413–492 | 345–482 | 318–434 | 307–416 |
| | sexual | 434–473 | 378–423 | 358–406 | 325–410 |
| Sexual > base en vida / comida | | 4/5 · 3/5 | 4/5 · 3/5 | 3/5 · 3/5 | **3/5 · 3/5** |

- **El cerebro no se estabiliza: se sigue vaciando**, en los 10 mundos, de 7 neuronas a 1,5–2,9 (época 600: 0,8–2,7 en la base y 1,1–2,1 con sexo), igual que el cuerpo (masa) y, más despacio, el empuje. Todo indica que ir hacia la comida quieta no necesita neuronas ocultas: con 1–2 de media siguen llegando a la mancha el 84–99 % de las veces (los sentidos conectados a los músculos bastan). Con la comida quieta, la selección hace lo mismo que en P1, pero más despacio: quitar lo que cuesta y no hace falta.
- **Comen menos y viven igual o más:** la ingesta baja un 15–25 % mientras la vida se mantiene o sube; gastan menos (menos masa y empuje).
- **Aprender sigue sin servir:** VA de la ingesta entre −0,03 y +0,04 en todas las ventanas.
- **El sexo no gana con el tiempo:** su ventaja en vida pasa de 4/5 a 3/5, y la ingesta se queda en 3/5. Mantiene más variedad estructural (distancia 44–51 frente a 19–35) y clados vivos. **B1 queda cerrado: asexual.**
- **Batería:** ganancia en la mancha de 0,11–0,27 (umbral 0,4); el éxito sigue en el 84–99 % con un cerebro casi vacío. Confirma que la prueba no mide cerebro (ADR de revisión antes de P3).
- **Para P3 y P4:** mientras la comida no se mueva ni haya nada que recordar, el cerebro no compensa. Es la pregunta de P4 (comida móvil).
- Datos: `runs/fase1d/P2-escalera-600`, `P2-escalera-sexual-600`, `_analisis_P2largo.json` (`scratchpad/p2l_an.py`).

### 21-10-2026, 11:53 · P3-escalera: hijos pagados (5 mundos)

Criterio prerregistrado en `diseno.md` v0.7. Rama `escalera-int` (`c01b46b`), examen sin química (ADR-021). 09:11–11:53; ningún mundo se pausó ni se extinguió. Medias de las épocas 151–300, emparejadas por semilla con P2-escalera:

| Medida | P2-escalera | **P3-escalera** | P3 frente a P2 |
|---|---|---|---|
| Población (**primaria**: menor que en P2) | 4.096 | **4.096** | **0/5: no pasa** |
| Época en que se llena el mundo | 2 | 6–54 | — |
| Vida media | 3.578–7.585 | 4.727–7.141 | mayor en 4/5 |
| Empuje | 9,0–10,8 | 7,9–9,9 | menor en 4/5 |
| Comida ingerida por época (miles) | 345–482 | 345–467 | mayor en 3/5 |
| Neuronas ocultas | 4,1–6,4 | 1,6–7,8 | menos en 3/5 |
| VA de la ingesta | −0,016 a −0,004 | −0,057 a +0,010 | ≈ 0 |
| Nacimientos por época | 541–1.157 | 582–884 | — |
| Muertes por hambre / por vejez (por época) | 223–823 / 318–344 | 234–506 / 345–387 | — |
| Generación máxima | 61–80 | 60–212 | — |
| Examen limpio: mancha (éxito / ganancia) | — | 0,03–0,08 / −0,13 a −0,02 | sin pausa |
| Examen limpio: laberinto (ganancia) | — | 0,00–0,01 | sin pausa |

Genes de reproducción de los vivos (`scratchpad/p3_genes.py`, épocas 100, 200 y 300; al nacer, el umbral medio es 55 y la fracción 0,5):

| Mundo | Umbral (época 300, p10–p90) | Fracción al hijo | Vivos por encima del umbral (100 / 200 / 300) |
|---|---|---|---|
| s0 | 21,8 (17,7–27,0) | 0,40 | 51 / 93 / 65 % |
| s1 | 36,5 (20,0–49,9) | 0,55 | 64 / 70 / 40 % |
| s2 | 30,2 (24,9–36,1) | 0,48 | 94 / 92 / 40 % |
| s3 | 22,2 (17,6–27,7) | 0,49 | 84 / 83 / 85 % |
| s4 | 51,4 (42,1–65,2) | 0,62 | 89 / 83 / 77 % |

- **La primaria no pasa (0/5).** Con los hijos pagados, el mundo tarda más en llenarse (de la época 2 a la 6–54), pero se llena y se queda lleno. En s0 y s3 baja a veces de 4.096 dentro de la época (mínimo 3.786), pero vuelve a llenarse.
- **El freno no es la comida, sino el tope de 4.096 plazas.** Entre el 40 y el 94 % de los vivos tienen energía de sobra para reproducirse y esperan un hueco libre. La comida de P2 (87 % del suelo) alimenta a más bichos de los que caben. La pregunta "¿limita la comida a la población?" no se puede contestar con esta comida: la respuesta del mundo es "aún no".
- **La selección sí ve los genes nuevos:** el umbral baja de 55 a 22–36 en 4 de 5 mundos (tener hijos antes, cuando hay que pelear por un hueco); s4 lo mantiene en 51 con hijos más ricos (0,62). Son dos estrategias distintas, sin ganador claro.
- **Secundarias:** viven algo más (4/5) y empujan algo menos (4/5); el cerebro sigue sin hacer falta (VA ≈ 0 y menos neuronas en 3/5). Con comida quieta, los hijos pagados no cambian lo que importa para el cerebro.
- **Examen limpio:** encuentran la mancha lejana el 3–8 % de las veces, peor que los controles fijos (ganancia negativa). No hubo pausas: con el examen limpio, ninguna señal.
- **Conclusión:** negativo según el criterio prerregistrado, pero por techo: no se ha medido lo que se quería medir. Siguiente paso, con el responsable.
- Datos: `runs/fase1d/P3-escalera`, `_analisis_P3int.json`, `_genes_P3int.json` (`scratchpad/p3_an.py`, `p3_genes.py`).

### 21-10-2026, 15:38 · P2-buscar: comida dispersa (5 mundos)

Criterio prerregistrado en `diseno.md` v0.8 (ADR-022). Rama `escalera-buscar` (`fff4e79`, sustrato 2.7.0, `K_CUT` 1,5), examen sin química. Tests en GPU: 80 en verde (11:53–12:27); mundos 12:27–15:38, sin pausas ni extinciones. Secundarias: medias de las épocas 151–300, emparejadas por semilla con P2-escalera.

| Medida | P2-escalera | **P2-buscar** | P2-buscar frente a P2 |
|---|---|---|---|
| Examen limpio en la época 300 (**primaria**: mayor que en P2) | 0,00 / 0,03 / 0,11 / 0,02 / 0,11 | **0,016 en los 5** | **1/5: no pasa** |
| Ganancia en la mancha (época 300) | — | −0,16 a −0,05 | sin pausa |
| Laberinto (éxito) | — | 0,00 | — |
| Vida media | 3.578–7.585 | **533–545** | menor en 5/5 (como P1: 523–524) |
| Empuje | 9,0–10,8 | 2,4–3,9 | menor en 5/5 |
| Comida ingerida por época (miles) | 345–482 | 18–53 | 7–25 veces menos |
| Comida en pie (alga total) | 10.304–19.154 | 415–1.701 | 10–40 veces menos |
| Neuronas ocultas (época 300) | 4,1–6,4 (151–300) | 0,6–0,9 (0,5–0,85) | menos en 5/5 |
| VA de la ingesta | −0,016 a −0,004 | **−0,45 a −0,12** | aprender perjudica |
| Nacimientos / muertes por hambre (por época) | 541–1.157 / 223–823 | 7.512–7.681 / 7.508–7.681 | — |
| Muertes por vejez (por época) | 318–344 | 0–4 | — |
| Generación máxima | 61–80 | 528–593 | — |

- **La primaria no pasa (1/5).** Nadie aprende a buscar: encuentran la mancha lejana el 1,6 % de las veces (1 de 64), peor que los controles fijos (6–17 %).
- **El mundo se parece a P1, no a P2.** Viven lo mismo que con el peaje y sin comida (533–545 pasos frente a 523), casi todos mueren de hambre y nadie llega a viejo. El cerebro se vacía (0,6–0,9 neuronas), como en P1.
- **Por qué:** los 4.096 bichos se comen la comida en cuanto crece (queda entre 10 y 40 veces menos alga en pie que en P2). Encontrar una mancha apenas alarga la vida, porque casi siempre está vacía. Y como los hijos nacen con energía regalada (`repro_mode` "edad"), la población sigue llena sin comer. Buscar no compensa: la selección premia gastar poco, igual que en P1.
- **Aprender perjudica (indicio):** el gemelo con la plasticidad apagada come entre un 12 y un 45 % más en los 5 mundos. Con tan poca comida, lo que se aprende en vida parece desviar al bicho del reflejo innato. Es la primera VA claramente distinta de cero de la escalera; hay que confirmarla antes de interpretarla.
- **Para P3:** aquí la comida sí es el freno (se agota), pero la población no baja porque la energía de los hijos se regala. Es justo lo que P3 cambia.
- **Conclusión:** negativo. Datos: `runs/fase1d/P2-buscar`, `_analisis_P2buscar.json` (`scratchpad/p2b_an.py`).

### 21-10-2026, 20:01 · P3-escaso: hijos pagados con la mitad de comida (5 mundos)

Criterio prerregistrado en `diseno.md` v0.9. Rama `escalera-int` (`f02e61f`), `k_mean` 1,902, examen sin química. 16:56–20:01; ningún mundo se pausó ni se extinguió (mínimo al arrancar: 16–73 bichos). Medias de las épocas 151–300, emparejadas por semilla con P3-escalera:

| Medida | P3-escalera | **P3-escaso** | P3-escaso frente a P3 |
|---|---|---|---|
| Población (**primaria**: menor que 4.096) | 4.096 | **2.516–2.690** (mínimo 2.381) | **5/5: pasa** |
| Vivos con energía para un hijo (época 300) | 40–85 % | **1–3 %** | la comida frena |
| Umbral para tener hijos (época 300; al nacer, 55) | 22–51 | **10,5–19,3** (suelo: 10) | más bajo en 5/5 |
| Fracción de energía al hijo (época 300; al nacer, 0,5) | 0,40–0,62 | **0,26–0,40** | más baja en 5/5 |
| Vida media | 4.727–7.141 | **483–688** | 7–14 veces menor |
| Energía media | 70–168 | 6–9 | — |
| Nacimientos / muertes por hambre (por época) | 582–884 / 234–506 | 3.792–5.587 / 3.770–5.587 | — |
| Muertes por vejez (por época) | 345–387 | 0–32 | — |
| Generación máxima | 60–212 | 335–452 | — |
| Comida ingerida por época (miles) | 345–467 | 176–192 | la mitad |
| Empuje | 7,9–9,9 | 6,4–7,8 | menor en 5/5 |
| Masa | 0,32–0,67 | 0,26–0,28 | menor en 5/5 |
| Neuronas ocultas | 1,6–7,8 | **0,05–1,45** (época 300: 0,06–1,51) | menos en 5/5 |
| VA de la ingesta | −0,057 a +0,010 | −0,021 a +0,009 | ≈ 0 |
| Examen limpio: mancha (éxito / ganancia, época 300) | 0,03–0,08 / −0,13 a −0,02 | 0,00–0,05 / −0,13 a −0,06 | sin pausa |
| Examen limpio: laberinto | 0,00–0,01 | 0,00–0,02 | sin pausa |

Genes de reproducción: `scratchpad/p3e_genes.py`, `_genes_P3escaso.json`.

- **La primaria pasa (5/5):** con la mitad de comida y los hijos pagados, la población se estabiliza en unos 2.500–2.700 bichos, un 35–39 % por debajo del tope. Ahora **la comida es el freno**: solo el 1–3 % de los vivos tienen energía para un hijo (en P3-escalera, el 40–94 %).
- **La selección elige hijos baratos y muchos:** el umbral baja casi al suelo (10,5–11,4 en 3/5) y la fracción cedida al hijo cae de 0,5 a 0,26–0,40. Cada hijo nace con unas 3–5 unidades de energía y vive unos 500–700 pasos; casi nadie llega a viejo. Es una estrategia "r" (muchos hijos pequeños), no una de buscadores mejores.
- **El cerebro se vacía todavía más:** 0,05–1,45 neuronas (menos que en P3-escalera en 5/5), cuerpo más pequeño y empuje menor. VA ≈ 0. Con comida quieta y escasa, la selección ahorra en todo: cuerpo, cerebro y dote del hijo.
- **Examen limpio:** encuentran la mancha lejana el 0–5 % de las veces, peor que los controles fijos. Sin pausas.
- **Conclusión: positivo** según el criterio prerregistrado (la comida limita la población). P3-escaso es el primer mundo de la escalera donde la comida decide quién tiene hijos. Pero, igual que en P2, buscar comida quieta no necesita cerebro.
- Datos: `runs/fase1d/P3-escaso`, `_analisis_P3escaso.json`, `_genes_P3escaso.json` (`scratchpad/p3e_an.py`, `p3e_genes.py`).
