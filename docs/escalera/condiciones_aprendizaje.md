# Condiciones para que evolucione el aprendizaje: qué dice la bibliografía y qué tiene nuestro mundo

Revisión pedida por el responsable el 23-10-2026 (13:39), tras ver que el fallo de la tripa ya lo anunciaba la bibliografía. Se cruza cada condición con el mundo de los últimos peldaños (P4-alga con tripa, sustrato 3.0.0) antes de decidir los siguientes. Las claves están en `docs/bibliografia/escalera/refs.bib` (DOI comprobados en Crossref); `1d/` indica la bibliografía de la fase 1d.

## Resumen

En los trabajos en que el aprendizaje evoluciona, el mundo cumple a la vez casi todas las condiciones C1–C6. Nuestro mundo cumple C2, C3 (desde la tripa) y C6. Falla en C4 (equivocarse no cuesta nada) y solo cumple a medias C1 (el cambio es casi predecible al nacer). C5, las decisiones por vida, está sin medir. Además, la bibliografía avisa de que el aprendizaje es raro incluso cuando el mundo lo favorece (C8): con 5 mundos y un criterio de 5/5, un acierto real puede pasar por un fracaso.

## Tabla de condiciones

| # | Condición | Qué dice la bibliografía | Nuestro mundo (P4-alga-tripa) | Estado |
|---|---|---|---|---|
| C1 | **Lo que conviene hacer no se puede saber al nacer, pero se mantiene un tiempo dentro de la vida** | Teoría: aprender compensa cuando el mundo cambia entre generaciones y es estable dentro de cada vida (stephens1991change, dunlap2009components, dunlap2019components). Si es estable entre generaciones, gana el reflejo innato (pontes2020evolutionary). En Pontes, el significado de las pistas se sortea para cada organismo. En Niv, qué flor premia se sortea en cada generación y además se intercambia a mitad de la vida | El alga buena cambia cada 2.000 pasos y los bichos viven unos 300. Solo ~15 % de las vidas ven un cambio, y la mayoría de los hijos nace con la misma alga buena que su padre: lo conveniente es casi predecible al nacer | ◐ a medias |
| C2 | **Hay una pista fiable de qué es lo bueno ahora** | La pista debe predecir la mejor acción dentro de la vida (dunlap2016reliability, pontes2020evolutionary) | El tipo de alga se ve en los rayos (signo del canal de recurso) | ✓ |
| C3 | **El bicho nota el resultado de lo que hace** | Entrada de premio explícita (néctar en niv2002evolution; premio en soltoggio2008evolutionary, `1d/`) o un sistema de valor que evoluciona (pontes2020evolutionary; para medir la ganancia citan el llenado de la tripa, charnov1976optimal) | Desde ADR-024, la tripa. Antes, solo `tanh(E/50)`, que con un bocado apenas cambia (0,007) | ✓ desde la tripa |
| C4 | **Elegir mal se paga** | Elecciones excluyentes con coste: una flor por prueba (niv2002evolution), pasos en vacío que restan (pontes2020evolutionary), veneno que cuesta energía (todd1991exploring), sustrato equivocado castigado (mery2002experimental). Comer quita tiempo de buscar (holling1959some); quedarse o irse son excluyentes (charnov1976optimal, stephens1986foraging) | Comer es gratis, no excluye moverse y el alga vacía no resta. La salida de comer está encendida el 74–99 % del tiempo, también donde no hay nada (bitácora, 23-10, 12:48) | ✗ (lo ataca ADR-025, comer frena) |
| C5 | **Hay bastantes decisiones en una vida para aprovechar lo aprendido** | Si se vive poco, no compensa explorar para aprender (eliassen2007exploration). Niv: 100 elecciones por vida | Vida de 240–320 pasos; plasticidad cada 4 pasos (~70 actualizaciones). Cuántas veces elige entre manchas o algas en una vida: sin medir | ? sin medir |
| C6 | **Antes existen reflejos que sirven de piezas** | El aprendizaje aparece sobre reflejos ya evolucionados, como volver al rastro tras un error (pontes2020evolutionary) | Buscar comida es innato desde P2 | ✓ |
| C7 | **Aprender cuesta, y lo estable se vuelve innato** | La capacidad de aprender tiene coste (mery2003fitness). Lo que se aprende siempre igual pasa a los genes, por el efecto Baldwin (hinton1987learning, mayley1996landscapes) | Cada neurona cuesta 0,02 por paso. En mundos estables el cerebro se vacía (P2, P3), como se predice | ✓ coherente |
| C8 | **Evolucionar el aprendizaje es difícil y raro** | La búsqueda es engañosa: al principio rinde más un truco fijo que aprender (risi2010evolving). Pontes: aprendizaje en el 7 % de los linajes, y en el 2 % el reaprendizaje. Niv: éxito en la mitad de las ejecuciones, con dos saltos de aptitud | 5 mundos por condición y criterio de 5/5. Con éxitos en un 7–50 % de los linajes, lo esperable es que pase en 0–3 de 5 aunque el mundo favorezca aprender | ⚠ el diseño puede no detectarlo |
| C9 | **La codificación favorece redes regulares** | Las codificaciones generativas (tipo CPPN) dan redes más regulares, y las más regulares aprenden mejor (tonelli2013relationships) | Genoma CPPN | ✓ |
| C10 | **Muchos retos distintos en una vida** | Si un individuo afronta muchos problemas distintos, aprender compensa aunque el mundo no cambie entre generaciones (dridi2016environmental) | Un solo reto: qué alga | ◐ bajo |

Otros apoyos: nolfi1996learning (robots que nacen en entornos distintos cada generación heredan una predisposición a aprender y se comportan de forma que realza las diferencias que perciben) y floreano2000evolutionary (evolucionar las reglas de plasticidad en lugar de los pesos da controladores que se adaptan; como nuestras reglas ABCD).

## Qué implica para los próximos peldaños

1. **C4, comer frena (ADR-025).** Es exactamente el ingrediente que falta según la bibliografía. Sigue siendo necesario.
2. **C1, el ritmo del cambio.** Con un cambio cada 2.000 pasos y vidas de 300, el mundo es casi predecible al nacer. Para cumplir C1 como en Pontes y Niv, el alga buena debería sortearse para cada bicho al nacer, o cambiar en un tiempo del orden de una vida.
3. **C8, la estadística.** Si el aprendizaje evoluciona en una fracción de los linajes, 5/5 es un listón que un efecto real casi nunca supera. Habría que pasar a más mundos por condición (10 o 20) y comparar la proporción de mundos que aprenden con su control, en vez de exigir todos.
4. **C5, medir antes.** Cuántas decisiones por vida tiene un bicho (cambios de mancha, encuentros con cada alga), con un diagnóstico en CPU como el de comer.
5. **C10, más adelante.** Más retos en una vida (veneno en P5, olfato, depredadores) deberían favorecer aprender por sí mismos.

## Fuentes leídas

Texto completo: pontes2020evolutionary; niv2002evolution (versión de congreso de 2001, mismo modelo). Resumen o resumen ampliado: eliassen2007exploration, tonelli2013relationships, mayley1996landscapes, nolfi1996learning, risi2010evolving, dridi2016environmental y soltoggio2008evolutionary (`1d/`). Las demás ya estaban en la bibliografía (§15–§18).
