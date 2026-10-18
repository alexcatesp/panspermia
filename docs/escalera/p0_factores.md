# Cierre de P0: factores que hay que decidir antes de P1

**18-10-2026 · decisión del responsable:** no se pasa a P1 hasta estar convencidos de que ninguna decisión de P0 tendrá que revisarse más adelante. Cada factor se apoya en bibliografía. Las referencias están en `docs/bibliografia/escalera/refs.bib`, con los DOI comprobados en Crossref.

**Qué es "de P0":** las reglas de la herencia, la variación, la demografía y la estructura de la población, que existen aunque no haya selección. P0 mide cómo se comportan solas; algunas solo se pueden juzgar del todo con selección (P1), pero **se deciden aquí**, porque cambiarlas después invalidaría todos los peldaños.

**Estados:**
- ✅ cerrado;
- 🔬 en simulación;
- 📋 pendiente de simular;
- 📚 se decide por bibliografía, sin simular;
- ⏭ no es de P0 (se decide en su peldaño).

## A. Variación: cómo muta el genoma

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| A1 | Física de la mutación de **neuronas** | "nest": invierte un hueco al azar; sin selección deriva hacia unas 43 | Infla los cerebros sin que sirvan; en la Tierra se pierde más de lo que se gana | kuo2009deletional, mira2001deletional, lynch2000duplicate, stanley2002neat, yampolsky2001bias, cano2022mutation | P0 con nest, neutral y terrestre (15 mundos) | 🔬 esta noche |
| A2 | Física de la mutación de la **CPPN** | añadir 5 %, quitar 2 %, dividir 3 %, quitar nodo 1 % | En P0 sus nodos pasan de 0,35 a ~11: es el mismo sesgo, en la receta del cerebro | stanley2002neat, langdon1998bloat, banzhaf2002bloat, kuo2009deletional | P0-cppn-neutral (5 mundos); si hace falta, también terrestre | 🔬 en cola |
| A3 | **Tasas de mutación**: gen o constante | σ autoadaptativa y tasa estructural como gen (deriva +75 % en 300 épocas) | Sin selección, la tasa sube por el suelo en 0. En la Tierra, la selección la baja hasta la barrera de la deriva | lynch2016driftbarrier, sniegowski1997mutators, beyer2002es | P0-tasas-fijas (5 mundos). Si se mantiene como gen, el ruido pasa a escala logarítmica (sin artefacto del suelo) | 🔬 en cola |
| A4 | **Cuánto** se muta: σ inicial 0,05, τ = 0,2, 11 % de cambios estructurales por hijo | sin contrastar | Demasiada mutación destruye la información más deprisa de lo que la selección la fija (umbral de error). Demasiado poca estanca | eigen1971selforganization, lynch2016driftbarrier | En P0: velocidad de divergencia neutral (`genome_distance`). El juicio necesita P1 | 📋 análisis de P0 + prueba en P1 |
| A5 | **Techo** del genoma: 64 neuronas y 32 nodos de CPPN | fijo | Con nest, el equilibrio neutral (~43) queda cerca del techo. La evolución abierta necesita poder crecer sin un límite artificial | taylor2016oee, stanley2002neat | Analizar en P0 qué fracción de bichos toca el techo con cada física | 📋 análisis (sin GPU) |
| A6 | **Genoma inicial**: 8 neuronas y CPPN mínima | "empezar mínimo" (NEAT) | Con la física terrestre, el punto de partida pesa: deriva hacia 0 | stanley2002neat | Se decide junto con A1 | 📚 |
| A7 | **Precisión** del genoma: los pesos se guardan en f16 | f16 | Un cambio menor que la resolución de f16 desaparece al guardarse: es otra "física" oculta, un suelo para σ | — (es técnico) | Medir en P0 cuántas mutaciones se pierden por redondeo | 📋 análisis (sin GPU) |

## B. Reproducción y herencia

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| B1 | **Sexo** (recombinación) | solo asexual; el sexo estaba previsto para la fase 3 | Sin recombinación, las mejoras compiten en lugar de sumarse (interferencia clonal) y las mutaciones dañinas se acumulan (trinquete de Muller). En poblaciones grandes, el sexo acelera mucho la adaptación. Añadirlo más tarde invalidaría todo lo anterior | muller1964ratchet, felsenstein1974recombination, colegrave2002sex, mcdonald2016sex | En P0, efectos neutrales (diversidad y ligamiento); su ventaja se ve con selección (P1). Requiere implementar el cruce por índices de la spec | 📋 decidir ahora; P0 y P1 |
| B2 | **Herencia de lo aprendido** | darwiniana: el hijo nace con los pesos innatos, no con los aprendidos | En la Tierra no se heredan los aprendizajes. En algoritmos, heredarlos (lamarckiano) acelera pero se queda en óptimos locales; el efecto Baldwin encuentra el global | whitley1994lamarck, hinton1987learning | Ninguna: se mantiene por principio y por bibliografía | ✅ 📚 |
| B3 | ¿Quién paga la energía del hijo? | dotación regalada (P0, P1) o cedida por el padre (P3+) | — | — | Es de P3 | ⏭ |

## C. Demografía

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| C1 | **Tamaño de la población** (tope) | 4.096 | El azar compite con la selección: una ventaja menor que ~1/N no se impone. Las poblaciones pequeñas y las grandes llegan a la complejidad por caminos distintos. El sexo ayuda más en las grandes | ohta1973nearlyneutral, charlesworth2009ne, labar2016populations, colegrave2002sex | P0-N1024 (5 mundos); quizá también N = 8.192 si cabe en la GPU | 🔬 en cola |
| C2 | **Muerte y vejez** | P0: vida fija de 600 pasos. Desde P1: la vejez se impone (gasto creciente desde 5.000 pasos) | En la Tierra, el envejecimiento **evoluciona**: acumulación de mutaciones (Medawar), pleiotropía antagonista (Williams), soma desechable (Kirkwood). En mundos espaciales, la muerte programada puede verse favorecida. Imponerla o dejarla evolucionar cambia la duración de las generaciones y cuánto compensa aprender | williams1957pleiotropy, kirkwood1977ageing, werfel2015death | En P0 solo reescala el tiempo. La decisión ("ley del mundo" o "gen") se toma ahora y se prueba en P1 o P2 | 📚 decidir ahora |
| C3 | **Población inicial** (512) | 512 | Solo afecta a la primera época: el mundo se llena enseguida | — | Ninguna: irrelevante en P0 | ✅ |
| C4 | **Tope de nacimientos** por paso (32) | 32 | Si se alcanza, frena la reproducción por una razón técnica | — | Comprobar en los datos que nunca se alcanza | 📋 análisis (sin GPU) |

## D. Estructura espacial

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba en P0 | Estado |
|---|---|---|---|---|---|---|
| D1 | **Dónde nace el hijo** | pegado al padre (a 2 radios) | Crea vecindarios de parientes (aislamiento por distancia). Eso favorece la cooperación y la señal, pero la competencia local entre parientes puede anularlo. Cambiarlo más tarde cambiaría toda la evolución social | wright1943isolation, taylor1992viscous, werfel2015death | P0 con nacimiento en un lugar al azar: medir el parentesco entre vecinos con las dos reglas | 📋 simular |
| D2 | **Tamaño del mundo** | 1.024 × 1.024 | Sin comida ni interacción no cambia nada | — | Ninguna en P0 | ⏭ P2 (densidad de comida) |

## E. Codificación del cerebro

| # | Factor | Hoy | Por qué hay que decidirlo | Bibliografía | Prueba | Estado |
|---|---|---|---|---|---|---|
| E1 | Codificación indirecta (CPPN → pesos) | CPPN, al estilo HyperNEAT | Rinde mejor cuanto más regular es el problema y peor en problemas irregulares. Es una decisión de fondo: cambiarla rompe todo | stanley2009hyperneat, clune2011indirect | No se puede juzgar sin selección. Se mantiene por bibliografía | ✅ 📚 |

## Plan para cerrar P0

1. **Esta noche (🔬):** A1, A2, A3 y C1 (35 mundos, hasta las ~11:00 del 19-10).
2. **Análisis sin GPU (📋):** A4, A5, A7 y C4, con los datos de P0 que ya existen.
3. **Simulaciones que faltan (📋):** D1 (dispersión al azar) y B1 (sexo). B1 necesita implementar el cruce, unas horas de trabajo.
4. **Decisiones por bibliografía (📚):** C2, A6, B2 y E1.
5. **Criterio de cierre:** todas las filas en ✅ o ⏭. Las decisiones quedan en una ADR de cierre de P0, que fija la "física" de la herencia para toda la escalera.
