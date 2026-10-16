# Fase 1d · Diseño experimental (protocolo prerregistrado)

**Versión 0.2 · 16-10-2026 · aprobada por el responsable (E0–E2 primero; tamaño del mundo según E0).** Las hipótesis, las medidas y el plan de análisis se fijan **antes** de ver los datos. Cualquier cambio posterior se anota en el registro de cambios del final, con fecha y motivo. Bibliografía y claves: [`docs/bibliografia/1d/`](../bibliografia/1d/README.md).

## 1. Pregunta

**¿Qué estructura temporal del mundo hace que evolucionen el aprendizaje en vida, la anticipación o el instinto?**

La teoría (Stephens 1991; Botero et al. 2015; Lange y Sprekeler 2020) y la neuroevolución con nota explícita (Giannakakis et al. 2023) predicen una respuesta. Nuestra contribución sería comprobarla, o refutarla, en una **ecología abierta sin nota**, con miles de agentes, depredación y química, con cerebros recurrentes cuyas reglas de plasticidad (ABCD moduladas) evolucionan, y con reproducibilidad bit a bit.

## 2. Escalas de tiempo de referencia

Medidas en el mundo de la fase 1b (semillas 0 y 2):

| Escala | Valor aproximado |
| --- | --- |
| Duración media de una vida (τ_vida) | ~140 pasos |
| Tiempo de generación (τ_gen; reproducción posible desde 200 pasos) | ~250–300 pasos |
| Época | 1.000 pasos (~3,5 generaciones) |

Todas las escalas del entorno se expresan **en múltiplos de τ_vida** para que los resultados sean comparables con la teoría.

Aviso: los ~140 pasos son la **edad media de los vivos**, no la duración media de la vida. Coinciden si el riesgo de morir es constante, y aquí la depredación y el hambre dominan sobre la senescencia, que empieza a los 5.000 pasos. El experimento 0 medirá τ_vida y τ_gen directamente (edad al morir y edad de los padres al reproducirse) antes de fijar los periodos.

## 3. Hipótesis y predicciones

| ID | Hipótesis | Predicción falsable |
| --- | --- | --- |
| **H1** | Aprender compensa con cambio **impredecible** de periodo intermedio | El valor del aprendizaje (VA) tiene forma de **campana** frente al periodo T del cambio, con el máximo en T ≈ 1–4 τ_vida y VA ≈ 0 para T ≪ τ_vida y para T → ∞ |
| **H2** | El cambio **predecible** favorece la anticipación, no el aprendizaje | Con el mismo periodo, un ciclo regular da menos VA que el cambio aleatorio y más **uso del reloj** (información mutua entre la fase del ciclo y las acciones) y más **anticipación** (cambio de conducta *antes* del cambio ambiental) |
| **H3** | El cambio **lento** lo resuelve la evolución (instinto) | Con T ≫ τ_gen la población sigue el cambio por selección: VA ≈ 0 y la preferencia innata se invierte en cada ciclo |
| **H4** | Con vidas cortas no da tiempo a aprender | Alargar la vida respecto al periodo del cambio (edad de reproducción y riesgo de depredación) aumenta el VA a igual T |
| **H5** | Cerebros e historia evolutiva | El tamaño del cerebro sigue al VA solo si el coste neuronal lo permite. Las poblaciones que vienen de un mundo estable rinden distinto al pasar a uno cambiante (Heesom-Green et al. 2026) |
| **H6** | Puntos de inflexión | Al cambiar bruscamente de régimen hay colapsos y extinciones (Botero et al. 2015), y una rampa gradual los reduce |

## 4. Mundo base

Mundo de la 1b (química, dos tipos de alga con signo visible en los rayos, veneno con rampa y `TOXIC_FACTOR = 0,5`) con **un único cambio**: la regla que decide qué alga es tóxica se sustituye por el **programa temporal** del experimento. Todo lo demás queda fijo.

**Viabilidad antes que nada (experimento 0).** Con la 1b solo sobreviven 2 de 5 semillas, y una tasa alta de extinción confundiría las medidas (sesgo de supervivencia). El experimento 0 calibra el mundo base hasta que **≥ 90 % de las semillas** sobreviva en el control sin cambio. Si hace falta, se suaviza la rampa o el veneno, nunca con una nota.

## 5. Manipulaciones

### E1 · Ritmo y previsibilidad del cambio (núcleo de la fase)

Cuál de los dos tipos de alga es tóxico cambia según un **programa** aplicado por **parches** (rejilla de 8 × 8 parches de 128 × 128 unidades):

- **Aleatorio** (impredecible): cada parche invierte su estado de forma independiente con probabilidad **2/T** por paso (proceso de Poisson, estancia media T/2, la misma frecuencia que el periódico). Los cambios son locales y no simultáneos, así que no hay colapsos sincronizados (ADR-008).
- **Periódico** (predecible): todos los parches invierten su estado cada T/2 pasos con una fase común, y el **reloj interno** de los agentes tiene el mismo periodo (`CLOCK_PERIOD = T`), así que el ciclo es anticipable.
- **Periodo T**, en escala logarítmica: **0,25 · 1 · 4 · 16 τ_vida** (≈ 35, 140, 560 y 2.240 pasos).
- **Controles**: T = ∞ (asignación fija, que nunca cambia) y un mundo sin alga tóxica.

→ 2 programas × 4 periodos + 2 controles = **10 condiciones**.

### E2 · Gemelo sin plasticidad (control causal de E1)

Cada condición de E1 se repite con la **plasticidad desactivada durante toda la evolución** (`plastic=False`). La diferencia en supervivencia, población e ingesta entre el mundo normal y su gemelo mide el valor de *poder* evolucionar el aprendizaje, no solo el de usarlo en una época → **10 condiciones**.

### E3 · Día y noche

El rebrote de algas oscila con periodo 100 pasos (< τ_vida) y amplitud {0, 0,8}, con el reloj sincronizado. Pregunta: ¿surgen actividad rítmica y anticipación (empezar a comer antes del «amanecer»)? → **2 condiciones**.

### E4 · Estaciones

La capacidad de carga oscila con periodo 2.000 pasos (~14 τ_vida) y amplitud {0, 0,6}. Pregunta: ¿surgen almacenamiento (emisión de nutriente antes del invierno) o migración? → **2 condiciones**.

### E5 · Duración de la vida (H4)

Con E1 aleatorio y T = 4 τ_vida, edad mínima de reproducción {100, 200, 400} → **3 condiciones** (la de 200 se comparte con E1).

### E6 · Coste neuronal (H5)

Con E1 aleatorio y T = 4 τ_vida, `C_NEURON` {0,005, 0,02, 0,08} → **3 condiciones** (la de 0,02 se comparte).

### E7 · Historia evolutiva (H5, H6)

Poblaciones de 300 épocas en el control T = ∞ se trasladan a E1 aleatorio con T = 4 τ_vida, de golpe o con una rampa de 40 épocas, y se comparan con poblaciones que siempre vivieron allí → **2 condiciones**.

### E8 · Fiabilidad del aviso (añadido en la v0.5, a propuesta del responsable)

En la naturaleza lo tóxico suele **avisar** (color, olor, sabor amargo), y los animales aprenden con un solo mal trago. En E1 no hay aviso: el tipo de alga se ve, pero no si es tóxica aquí y ahora. E8 añade un **olor de aviso** en las celdas de alga tóxica, presente con probabilidad **r ∈ {0, 0,5, 0,8, 1}** por parche y cambio (nunca en alga buena: si aparece, no miente). Las condiciones son E1 aleatorio con T = 4 τ_vida, veneno 0,3 y 5 semillas → **4 condiciones**.

Predicción (Dunlap y Stephens 2009, `dunlap2009components`): con r = 1 gana el instinto («evita ese olor»), VA bajo y cerebros pequeños; con r = 0 aprender es la única vía; con r intermedio, mezcla de instinto y aprendizaje.

Implementación pendiente: necesita un canal sensorial nuevo (un cuarto campo químico o una marca en el canal de recurso de los rayos). Si cambia `OBS_DIM`, el sustrato sube de versión mayor. Se decide al programarlo, después de E1 y E2.

### Aplazado

- **Mareas**: requieren terreno o paredes móviles. Irán en la fase 1e.
- **Combinaciones** (día + estaciones + cambio aleatorio): Troein et al. (2009) sugieren que la complejidad surge al combinarlas. Se lanzan solo si E1–E4 dan efectos claros.

## 6. Réplicas y semillas

- **5 semillas por condición** sobre el **mismo mundo** (mismo `node_id`). La variación entre semillas mide el **azar histórico**.
- En las condiciones centrales de E1 (aleatorio, T = 1 y 4 τ_vida) se añaden **3 mundos distintos** con la misma semilla, para medir el **efecto del mundo**. Separa las dos causas que hoy van juntas.
- Duración: **300 épocas** por ejecución (~1.000 generaciones), con un checkpoint cada 50 épocas.

## 7. Medidas

**Primaria**:
- **VA, valor del aprendizaje**, con la sonda emparejada (`scripts/learning_probe.py`) en las épocas 100, 200 y 300: la misma época desde el mismo checkpoint y con la misma aleatoriedad, con y sin plasticidad.
- `VA = log((población_plástica + 1) / (población_congelada + 1))` (v0.4); resumen por condición con la mediana entre semillas. La versión relativa, `(plástica − congelada) / congelada`, se conserva como secundaria.
- También se registran la ingesta, los nacimientos y la fracción de alga tóxica ingerida.

**Secundarias**:
- neuronas ocultas y **moduladoras** (`hid_type`) expresadas;
- η efectiva media (|Δw| por paso);
- **uso del reloj**: información mutua entre la fase del reloj y las acciones (comer, empuje, emitir);
- **anticipación**: en los programas periódicos, cambio en la fracción tóxica ingerida en los T/8 pasos **antes** frente a **después** de cada inversión;
- **curva de recuperación** (v0.5): fracción de alga tóxica ingerida según los pasos transcurridos desde el último cambio del parche donde se come (intervalos 0–8, 8–16, …, ≥ 2.048). Responde a si los agentes **captan el cambio** (la fracción cae con el tiempo desde el cambio) y si **aprenden a aprender** (Harlow 1949: la caída se acelera con las generaciones; comparación de los primeros 64 pasos en las épocas 41–100 y en las últimas 100);
- supervivencia, épocas hasta la extinción y colapsos (población < 10 % del máximo);
- diversidad: grupos conductuales, archivo de novedad y clados.

**Observación pura**: ninguna medida entra en la reproducción (principio 1).

## 8. Plan de análisis

- **H1**: ajustar VA frente a log T (programa aleatorio) con un modelo cuadrático. Hay campana si el término cuadrático es negativo con IC del 95 % por debajo de 0 y el máximo cae dentro del rango probado. Se usa *bootstrap* por semillas.
- **H2**: comparar aleatorio y periódico en cada T, en VA, uso del reloj y anticipación. Prueba de permutación pareada por semilla y corrección de Holm por los 4 periodos.
- **H3–H6**: comparaciones planificadas con permutación, con el efecto expresado como diferencia de medias e IC del 95 %.
- **Extinciones**: se informan siempre. Las medidas se calculan sobre las ejecuciones supervivientes, señalando el posible sesgo.
- Umbral de significación α = 0,05 tras la corrección. Los análisis exploratorios se etiquetan como tales.

## 9. Presupuesto de cálculo

| Bloque | Condiciones | Ejecuciones (×5 semillas) |
| --- | --- | --- |
| E0 (calibración) | ~4 | ~20 cortas (100 épocas) |
| E1 | 10 | 50 |
| E2 | 10 | 50 |
| E3 + E4 | 4 | 20 |
| E5 + E6 | 4 nuevas | 20 |
| E7 | 2 | 10 |
| Mundos extra de E1 | 3 × 2 | 6 |
| **Total** | | **~156 ejecuciones de 300 épocas ≈ 47.000 épocas** |

A ~5 s por época (N = 4.096) son **~65 h**, unos 2,7 días de GPU continua. Con N = 2.048 (por medir) podría bajar a ~1,5 días. Orden recomendado: E0 → E1 → E2 (lo esencial, ~1,5 días) → resto.

## 10. Trabajo de implementación (antes de lanzar)

1. Integrar la 1b en `main` como sustrato 2.x, con la etiqueta `fase1b`.
2. **Programa temporal de toxicidad** por parches (aleatorio o periódico, con periodo T), con `CLOCK_PERIOD` configurable por mundo. Tests: conservación, determinismo, frecuencia empírica de cambios ≈ 1/T.
3. **Oscilaciones** de rebrote (día) y de capacidad (estaciones).
4. **Configuración de experimentos** declarativa (JSON por condición) y un **lanzador de barridos** que ejecute la cola de uno en uno y salte lo ya hecho.
5. **Sonda emparejada dentro del runner**, que sustituye a la métrica degenerada de cohortes.
6. Medidas nuevas: uso del reloj, anticipación y η efectiva.
7. Análisis: un script que lea todas las ejecuciones y produzca las tablas y figuras del plan de análisis.

## 11. Riesgos

- **Extinciones masivas**: el experimento 0 lo aborda; si aun así son frecuentes, se informan como resultado (H6).
- **VA ≈ 0 en todo**: también sería un resultado. Indicaría que, con vidas de ~140 pasos, no da tiempo a aprender (H4), y E5 lo comprobaría directamente.
- **Los periodos cortos no son detectables** por los agentes (la plasticidad actúa cada 4 pasos): T = 35 pasos es el límite inferior razonable.
- **Coste de cálculo**: si la ejecución se alarga, se reduce a 3 semillas en E3–E7, nunca en E1 y E2.

## Registro de cambios

- 0.1 (16-10-2026): primer borrador.
- 0.2 (16-10-2026, antes de tener datos): aprobación. En el programa aleatorio la probabilidad pasa de 1/T a 2/T para igualar la frecuencia de cambios con el periódico, de modo que la única diferencia entre ambos es la previsibilidad. Implementado en la rama `fase1d` (`58dfc48`): `panspermia.experiment`, colas en `experiments/fase1d/`.
- 0.3 (16-10-2026, tras E0): **N = 4.096** (N = 2.048 llena el cupo y dobla τ_vida). **τ_vida = 206 pasos** medido, así que los periodos de E1 pasan a 50 · 200 · 800 · 3.200 pasos (0,25 · 1 · 4 · 16 τ_vida). El control sin cambio cumple la viabilidad (5/5), pero el aleatorio con T = 560 se extingue en 3 de 5. Por decisión del responsable se calibra el veneno (`TOXIC_FACTOR` 0,5 → 0,3, en todas las condiciones por igual) con E0b antes de E1. El criterio de viabilidad se amplía a las condiciones centrales de E1, no solo al control. La batería se aplaza con menos de 32 adultos (ADR-013).
- 0.4 (16-10-2026, tras E0b y antes de E1): **corrección**: τ_vida se resume con la mediana entre semillas (~130 pasos; la media de 206 de la v0.3 estaba inflada por una semilla), así que **se mantienen los periodos 35 · 140 · 560 · 2.240**. Veneno calibrado: `TOXIC_FACTOR` = 0,3 en E1 y E2 (8 de 9 mundos viables en E0b; el responsable decide seguir e informar las extinciones). **Medida primaria**: VA_log = log((población_plástica + 1) / (población_congelada + 1)), con **mediana** entre semillas y *bootstrap*. La relativa explotaba con gemelos casi extintos (+32 en E0b). La relativa se conserva como secundaria.
- 0.5 (16-10-2026, 23:10, E1 parado a los 20 min y relanzado, sin datos analizados): a propuesta del responsable («¿descubren los bichos el patrón de la variabilidad?») se añade la **curva de recuperación** tras cada cambio de parche y su comparación temprana/tardía («aprender a aprender»). Se añade **E8, fiabilidad del aviso**, para después de E1/E2. Observación pura: la dinámica no cambia (`tox_since` y los contadores no entran en ninguna decisión). `tox_patch_flips` pasa a contar los cambios reales (antes restaba cambios opuestos simultáneos).
