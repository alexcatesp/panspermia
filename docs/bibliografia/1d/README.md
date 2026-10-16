# Bibliografía de la fase 1d: ¿cuándo compensa aprender?

Búsqueda del 16-10-2026 para la fase 1d (ADR-012): **¿qué estructura temporal del mundo (ritmo, regularidad, intensidad del cambio) hace que evolucionen el aprendizaje en vida, la anticipación o el instinto?**

- `refs.bib`: BibTeX de todo lo citado. Todos los DOI y arXiv se comprobaron en Crossref y en la API de arXiv el 16-10-2026.
- `pdf/`: copia local de los textos de acceso abierto. **No se sube a GitHub** (derechos de autor); en el repositorio quedan las fichas y los enlaces.
- Nivel de lectura de cada ficha: **[completo]** si se leyó el texto completo o un informe detallado; **[resumen]** si solo el resumen y fuentes secundarias.

## 1. Lo que ya se sabe (síntesis)

1. **La teoría clásica**: aprender compensa cuando el entorno cambia **entre generaciones** pero es **regular dentro de una vida** (Stephens 1991; Johnston 1982). Si cambia demasiado deprisa, lo aprendido caduca; si no cambia, basta el instinto. Dunlap y Stephens (2009) separan los «componentes del cambio» y lo comprueban con evolución experimental en moscas (2014).
2. **El mapa de estrategias**: Botero et al. (2015) dividen el espacio (rapidez × previsibilidad del cambio) en regiones donde gana una estrategia: plasticidad reversible, plasticidad irreversible, apuesta repartida (*bet-hedging*) o seguimiento genético. **Cruzar de una región a otra provoca colapsos y extinciones**: puntos de inflexión evolutivos.
3. **En agentes con plasticidad evolucionada**, la dependencia del aprendizaje la controlan la magnitud del cambio, su frecuencia (relación en **campana**: ni muy lento ni muy rápido) y la fiabilidad de la señal de recompensa (Giannakakis et al. 2023). Las neuronas moduladoras evolucionan solas cuando la recompensa cambia de sitio dentro de una vida (Soltoggio et al. 2008). En meta-aprendizaje hay dos regímenes, uno que aprende y otro que codifica la conducta de serie, según la incertidumbre ecológica, la complejidad de la tarea y la duración de la vida. El instinto gana no solo en lo que es estable entre individuos, sino también cuando adaptarse sería útil **pero no da tiempo a aprenderlo en la vida que queda** (Lange y Sprekeler 2020).
4. **El tipo de selección importa**: con competencia por nichos limitados (sin una nota global), la plasticidad persiste incluso en entornos estables si hay variedad de nichos. Con selección por nota global, desaparece y hay más extinciones tempranas (Nisioti y Moulin-Frier 2022).
5. **Cerebros y entornos cambiantes**: la hipótesis del colchón cognitivo (Sol 2009) dice que los cerebros grandes evolucionan para afrontar la variabilidad. Pero en neuroevolución con coste energético, los cerebros grandes surgen en entornos **estables** y ricos, y después ayudan a colonizar los cambiantes (Heesom-Green et al. 2026). En aves, los cerebros grandes preceden a la colonización de hábitats variables y estabilizan las poblaciones (Fristoe et al. 2017).
6. **Evolución digital**: la plasticidad estabiliza la evolución en entornos que cambian de forma cíclica y evita la pérdida de rasgos útiles (Lalejini et al. 2021, Avida). En células virtuales, el cambio frecuente favorece la plasticidad y el infrecuente, la capacidad de evolucionar (Cuypers et al. 2017).
7. **Ritmos y relojes**: relojes biológicos complejos aparecen al evolucionar redes génicas bajo **tiempo meteorológico y estaciones juntos**, no por separado (Troein et al. 2009). Los objetivos que varían de forma modular generan redes modulares (Kashtan y Alon 2005, con dudas de replicación).

## 2. El hueco: qué no está hecho y podemos aportar

Casi todos los trabajos anteriores tienen al menos una de estas limitaciones:
- **Nota explícita** (algoritmo genético con fitness: Giannakakis, Heesom-Green, Soltoggio, Lange);
- **agentes aislados** o en episodios cortos, sin ecología (sin depredación, sin competencia por recursos, sin química);
- **un solo tipo de variación** (cambio aleatorio o ciclo, rara vez ambos y a varias escalas);
- **modelos abstractos** sin cerebro (Botero, Nisioti, Cuypers).

Lo que la fase 1d puede aportar, si sale:
- un **mapa empírico** de qué estructura temporal (ciclo rápido como el día, ciclo lento como las estaciones, cambio impredecible, cambio lento) produce **aprendizaje, anticipación o instinto**;
- con **cerebros recurrentes evolucionados** (CPPN y reglas hebbianas ABCD moduladas);
- en una **ecología abierta sin nota** (miles de agentes, depredación, química) y **reproducible bit a bit**;
- con el valor del aprendizaje medido por **sonda emparejada** (misma época con y sin plasticidad).

Además, dos resultados nuestros ya dialogan con la literatura:
- en el mundo **estable** de la fase 1 los cerebros **encogen**, lo contrario de Heesom-Green et al. (2026), donde el mundo estable deja crecer los cerebros. Diferencias candidatas: nuestra depredación y el coste por neurona;
- en la 1b, 3 de 5 mundos se extinguen al pasar de «alga inocua» a «alga venenosa», coherente con los puntos de inflexión de Botero et al. (2015).

## 3. Implicaciones de diseño para la 1d

- **Duración de la vida** (Lange y Sprekeler): con vidas de ~140 pasos puede no dar tiempo a aprender; barrer la senescencia o la edad de reproducción.
- **Variables independientes, definidas como en la teoría**: periodo del cambio frente a la duración de una vida (~140 pasos) y de una generación (~250–300 pasos), previsibilidad (ciclo frente a cambio aleatorio) y fiabilidad de la señal. Barrer el periodo en escala logarítmica para ver la **campana** de Giannakakis.
- **Medidas**: valor del aprendizaje (sonda emparejada), tasa de aprendizaje efectiva (|Δw| por vida), neuronas ocultas y moduladoras, uso del reloj interno (información mutua entre fase del ciclo y acciones) y anticipación (cambio de conducta antes del cambio ambiental).
- **Separar azar histórico y entorno**: el mismo mundo con varias semillas y varios mundos con la misma semilla.
- **Controles**: un mundo sin cambio y la misma condición con la plasticidad bloqueada genéticamente (η = 0).
- **Historia evolutiva** (Heesom-Green; Fristoe): comparar poblaciones que empiezan en el mundo cambiante con poblaciones que vienen de un mundo estable (migración entre mundos).
- **Puntos de inflexión** (Botero): registrar extinciones y colapsos al cambiar de régimen, y la rampa como variable propia.

## 4. Fichas

| Ref. | Qué hicieron | Qué encontraron | Por qué nos importa | Lectura | PDF |
| --- | --- | --- | --- | --- | --- |
| Stephens 1991, *Behav. Ecol.* 2:77–89 | Modelo de decisión del valor del aprendizaje según la historia vital | Aprender compensa con cambio entre generaciones y regularidad dentro de la vida | Hipótesis central de la 1d | [resumen] | no (de pago) |
| Johnston 1982, *Adv. Study Behav.* 12:65–106 | Revisión de costes y beneficios de aprender | Aprender tiene costes (tiempo, errores, tejido) que la selección pondera | Marco de costes; nuestro coste por neurona | [resumen] | no |
| Dunlap y Stephens 2009, *Proc. R. Soc. B* 276:3201–3208 | Comparación de modelos sobre qué significa «cambio» | Los modelos difieren en la definición de cambio; proponen componentes estandarizados | Definir bien nuestras variables independientes | [resumen] | no |
| Dunlap y Stephens 2014, *PNAS* 111:11750–11755 | Evolución experimental en *Drosophila* | Se evoluciona «aprendizaje preparado» según la fiabilidad de cada señal | Validación experimental de la teoría | [resumen] | enlace PMC4136563 |
| Dunlap y Stephens 2016, *Curr. Opin. Behav. Sci.* 12:73–79 | Revisión | Fiabilidad, incertidumbre y costes en la evolución del aprendizaje | Estado del arte reciente de la teoría | [resumen] | no |
| Botero et al. 2015, *PNAS* 112:184–189 | Modelo de respuestas evolutivas a la selección fluctuante | Regiones donde gana una estrategia; cruzarlas produce colapsos y extinciones | Mapa teórico de la 1d; explica las extinciones de la 1b | [resumen + nota de prensa] | sí |
| Giannakakis, Khajehabdollahi y Levina 2023, arXiv:2303.06734 | GA que evoluciona una regla hebbiana modulada por recompensa (8 parámetros) en agentes estáticos y que se mueven | η crece con la magnitud del cambio, cae con el ruido y tiene forma de campana con la frecuencia; la forma de la regla depende de la tarea; redundancia en agentes con cuerpo | El trabajo más cercano; diferencia: nota explícita, sin ecología | [completo] | sí |
| Giannakakis et al. 2024, arXiv:2403.13649 | Igual, en tarea de forrajeo | Cuellos de botella de la red y estructura de la tarea dan reglas interpretables | Interpretar nuestras reglas ABCD evolucionadas | [resumen] | sí |
| Soltoggio et al. 2008, ALIFE XI, 569–576 | Neuroevolución en laberintos en T con recompensa que cambia dentro de la vida | Las neuronas moduladoras evolucionan solas y mejoran el aprendizaje | Nuestras neuronas moduladoras deberían aparecer en la 1d | [resumen] | enlace (repositorios EPFL y Loughborough) |
| Soltoggio, Stanley y Risi 2018, arXiv:1703.10371 | Revisión de redes plásticas evolucionadas | Panorama del campo | Marco general y vocabulario | [resumen] | sí |
| Lange y Sprekeler 2020, arXiv:2010.04466 | Análisis matemático y meta-aprendizaje de «nature versus nurture» | Dos regímenes (aprender o codificar de serie) según la incertidumbre, la complejidad de la tarea y la duración de la vida; se codifica lo que no da tiempo a aprender | **La duración de la vida es variable de la 1d**: nuestros agentes viven ~140 pasos | [resumen] | sí |
| Nisioti y Moulin-Frier 2022, arXiv:2202.08834 | Modelo mínimo de plasticidad y capacidad de evolucionar con nichos y clima | Con competencia por nichos la plasticidad persiste en entornos estables; la nota global la elimina y aumenta las extinciones | Justifica nuestra selección ecológica sin nota | [completo] | sí |
| Lalejini et al. 2021, *Front. Ecol. Evol.* 9:715381 | Avida en entornos cíclicos | La plasticidad estabiliza la evolución y evita perder rasgos | Precedente en evolución digital | [resumen] | sí |
| Cuypers, Rutten y Hogeweg 2017, *BMC Evol. Biol.* 17:60 | Células virtuales | El cambio frecuente favorece la plasticidad; el infrecuente, la capacidad de evolucionar | Predicción por escala temporal | [resumen] | sí |
| Grove 2014, *Adapt. Behav.* 22:235–254 | Algoritmo evolutivo con inestabilidad climática | Plasticidad bajo variabilidad que desaparece en periodos estables | Comparar con nuestros mundos sin cambio | [resumen] | no |
| Heesom-Green, Shock y Nitschke 2026, arXiv:2609.15569 (GECCO) | NEAT con coste energético en forrajeo estacional (predecible o no) | Los cerebros grandes vienen de evolucionar en estático y luego rinden mejor ante cambios impredecibles | Contraste con nuestra fase 1, donde los cerebros encogen en estático | [completo] | sí |
| Sol 2009, *Biol. Lett.* 5:130–133 | Revisión de la hipótesis del colchón cognitivo | Los cerebros grandes ayudan ante retos ecológicos nuevos | Hipótesis a contrastar | [resumen] | enlace PMC2657766 |
| Fristoe, Iwaniuk y Botero 2017, *Nat. Ecol. Evol.* 1:1706–1715 | Comparativa en aves | Los cerebros grandes estabilizan poblaciones y preceden a la colonización de hábitats variables | Historia evolutiva y migración entre mundos | [resumen] | no |
| Troein et al. 2009, *Curr. Biol.* 19:1961–1964 | Evolución de redes génicas de reloj | Relojes complejos solo con tiempo meteorológico y estaciones juntos | Diseño de ritmos combinados (día + estaciones + ruido) | [resumen] | sí |
| Kashtan y Alon 2005, *PNAS* 102:13773–13778 | Evolución con objetivos que varían de forma modular | Surgen modularidad y motivos de red | Medir modularidad en nuestros cerebros; replicación discutida | [resumen] | enlace |
| Kouvaris et al. 2017, *PLOS Comput. Biol.* 13:e1005358 | Evolución como aprendizaje | La evolución «aprende a generalizar» con entornos variables | Marco para la capacidad de evolucionar | [resumen] | sí |
| Lehman y Miikkulainen 2015, *PLOS ONE* 10:e0132886 | Extinciones en neuroevolución | Los eventos de extinción pueden acelerar la evolución | Lectura de nuestros colapsos | [resumen] | no |
| Omer et al. 2025, arXiv:2508.00527 | Poblaciones microbianas en entornos parcialmente predecibles | La evolución aprende la estructura estadística de las transiciones | Previsibilidad parcial como variable | [resumen] | sí |
| Claret et al. 2026, arXiv:2610.00148 | Sustratos CPPN con neuromodulación | La neuromodulación sola no basta; hacen falta tipos de activación | Afecta a nuestro diseño CPPN | [resumen] | sí |
| Nolfi y Floreano 1999, *Auton. Robots* 7:89–113 | Revisión de aprendizaje y evolución en robots | Interacciones entre aprendizaje y evolución | Marco clásico en robótica evolutiva | [resumen] | no |
| Resendez Prado 2026, arXiv:2604.03565 | Neuroevolución con plasticidad hebbiana en ajedrez | Tres regímenes del efecto Baldwin; la plasticidad acaba aumentando la diversidad | Efecto Baldwin y diversidad | [resumen] | sí |

## 5. Pendiente

- Leer completos Stephens 1991, Botero 2015 y Lange y Sprekeler 2020 antes de fijar los niveles de los barridos.
- Buscar trabajos de evolución de la **anticipación** con redes neuronales (no génicas) en ciclos día y noche: hasta ahora solo hay redes génicas (Troein; Knabe et al., ALIFE X, 2006, sin verificar).
- Buscar trabajos de vida artificial con **mareas** o accesibilidad periódica del terreno.
