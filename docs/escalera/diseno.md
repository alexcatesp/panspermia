# Escalera de complejidad · protocolo prerregistrado

**v0.1 · 18-10-2026 · rama `escalera` (worktree `panspermia-escalera`, sustrato 2.1.0) · ADR-014**

Escrito antes de tener ningún dato de la escalera. Cualquier cambio posterior se añade como versión nueva, con fecha y motivo, sin borrar lo anterior.

## Por qué

En la retrospectiva del 18-10, el responsable señaló que el proyecto añadió muchas variables a la vez:

- la fase 0 encendió de golpe comida, gasto, hambre, reproducción pagada y plasticidad;
- la fase 1, ataque, carroña, señal, vejez y biogeografía;
- la fase 1b, química, feromona, dos algas y veneno.

Toda la fase 1d se ha medido en un mundo con más de diez interruptores encendidos. Además, nunca se probó un control sin selección. La escalera rehace el camino **de un interruptor en un interruptor**: cada peldaño es el anterior más una sola cosa, y responde a una pregunta de sí o no.

## Peldaños

Mismo mundo (`node` `fase1d-w0`), 5 semillas (0–4), 300 épocas, N_max = 4.096 y N_init = 512. Plasticidad evolucionable y sonda del gemelo congelado cada 20 épocas, como en la 1d. **Misma semilla = mismos fundadores y misma geografía en todos los peldaños**, así que las comparaciones van emparejadas por semilla.

En todos los peldaños, salvo que se diga otra cosa: sin ataque (`attack_on` 0), sin química (`chem_on` 0), sin señal (`signal_on` 0) y sin veneno (`seasonal` 0). Los rayos siguen viendo los dos tipos de alga con su signo, que es igual en todos los peldaños.

| Peldaño | Añade respecto al anterior | Interruptores (`env`) |
|---|---|---|
| **P0 · Mundo feliz** | punto de partida: vivir es gratis, no hay comida, todos mueren a los 600 pasos, se nace por edad con energía regalada (E_INIT) y el padre no paga | `metabolism` 0, `k_mean` 0, `repro_mode` "edad", `max_age` 600 |
| **P1 · Peaje** | vivir, moverse, cada neurona y el tamaño cuestan energía; sin edad máxima | `metabolism` 1, `k_mean` 0, `repro_mode` "edad" |
| **P2 · Comida quieta** | comida que crece y se agota, en manchas que no se mueven | `repro_mode` "edad", `drift` 0 |
| **P3 · Hijos pagados** | reproducirse exige superar el umbral de energía y ceder una parte al hijo: la comida pasa a ser la única fuente de energía | `drift` 0 |
| **P4 · Comida móvil** | las manchas se desplazan despacio, como en el mundo de siempre | (todo por defecto, salvo lo común) |
| **P5 · Veneno** | un tipo de alga es tóxico, el mismo en todo el mundo y siempre (factor 0,3, rampa de 40 épocas) | `seasonal` 1, `tox_mode` "uniforme" |

**Notas de diseño:**

- En la propuesta del responsable, la comida y la reproducción pagada llegaban en el mismo paso; aquí se separan (P2 y P3) para que cada peldaño cambie una sola cosa.
- **P0, vida fija:** sin ninguna muerte, el mundo se llenaría y se congelaría. Una muerte a edad fija da relevo sin selección (decisión del responsable, 18-10). Los 600 pasos son la vida de un bicho quieto que solo paga el gasto basal en P1 (E_INIT / C_BASAL / DT).
- **P1, dotación fija:** sin comida, si el padre pagara al hijo, la energía total solo bajaría y el mundo se apagaría (decisión del responsable, 18-10). Calibración de P1:
  - quieto, con 8 neuronas y masa 1, gasta 0,76 por unidad de tiempo y vive unos 395 pasos, así que puede tener hijos desde la edad 200 (`MIN_REPRO_AGE`);
  - con el empuje máximo (20), gasta más de 1,5 y muere antes de los 200 pasos sin dejar hijos.
- La vejez (senescencia desde 5.000 pasos) está en la fórmula del gasto, así que existe desde P1. En P1 nadie llega a esa edad.
- **P5 frente a E1b-uniforme:** tienen el mismo veneno, las mismas semillas y el mismo factor. E1b-uniforme tiene además química, feromona, ataque, carroña y señal. La comparación mide, de una vez, si todo eso cambia algo; es un salto y se declara como tal.

## Medidas

Todas solo observan. Se calcula la media por semilla en la ventana tardía, **épocas 151–300**:

- `thrust_mean`: empuje real medio por bicho y paso;
- `desc_speed`: velocidad del descriptor conductual;
- `hidden_mean`: neuronas ocultas expresadas;
- `mass_mean`: masa;
- `max_thrust_mean`: empuje máximo genético;
- `lifespan_mean`: edad media al morir;
- `population`;
- `intake`;
- `toxic_intake_frac`;
- VA_log de población e ingesta (gemelo congelado, 8 sondas por mundo).

## Predicciones y criterios

**Regla de decisión:** con 5 semillas emparejadas, un peldaño "funciona" si la diferencia predicha tiene el signo predicho en las **5 de 5** semillas (prueba de signos exacta unilateral, p = 0,031). Hay una medida primaria por peldaño y las secundarias son descriptivas.

| Peldaño | Pregunta | Primaria (frente al anterior) | Secundarias |
|---|---|---|---|
| P0 | ¿Qué hacen las medidas sin selección? | — (referencia): la población llega a ≥ 95 % de N_max | deriva de `hidden_mean`, `thrust_mean` y `mass_mean` (dirección libre: es el sesgo de la mutación); VA ≈ 0 |
| P1 | ¿Funciona la selección? | `thrust_mean` **menor** que en P0 | `hidden_mean` y `mass_mean` menores; VA ≤ 0 (no hay nada que aprender) |
| P2 | ¿Sirve la comida y se va a por ella? | `lifespan_mean` **mayor** que en P1 | `thrust_mean` mayor (moverse hacia la comida compensa); VA |
| P3 | ¿Limita la comida a la población? | `population` **menor** que en P2 | `hidden_mean`; VA |
| P4 | ¿Obliga la comida móvil a moverse más? | `thrust_mean` **mayor** que en P3 | VA |
| P5 | ¿Aprenden a evitar el veneno? | `toxic_intake_frac` de las épocas 151–300 **menor** que la de las épocas 41–50 (final de la rampa), dentro de P5 | VA_log_population > 0; comparación descriptiva con E1b-uniforme |

**Pregunta de fondo:** ¿en qué peldaño empieza a compensar aprender en vida, es decir, VA > 0? Predicción: no en P0–P1, porque no hay nada que aprender. Puede empezar en P5, o en P4 si la comida móvil cambia lo bastante deprisa para una vida. La deriva de las manchas es lenta (`K_DRIFT`), así que lo esperable es P5.

**Si un peldaño falla:** no se sube al siguiente sin entender por qué. Si P1 falla (la selección no reduce el movimiento), el motor o la calibración tienen un problema, y eso invalida lo que viene detrás.

## Análisis y orden

- Cola `experiments/fase1d/escalera.json`, con los datos en `runs/fase1d/P*/s*`.
- Orden en la GPU (decisión del responsable, 18-10): **E2 → escalera → E9 → E1b**. Son unos 30 mundos, unas 15 h.
- El análisis compara peldaños consecutivos por semilla (script `scripts/analyze_ladder.py`, por escribir antes de ver datos).

## v0.2 · 18-10-2026, 18:45 · Ramas tras P5 (decisión del responsable)

Se añade antes de tener datos y no cambia ningún criterio de P0–P5.

- **P0–P3 son cimientos.** Si uno falla, se repara (calibración o motor) antes de subir.
- **P5 es la bifurcación.** Se mira la mediana de VA_log_population de las épocas 151–300 y su signo por semilla:
  - **sí** (VA > 0 en 5 de 5): **P6 · veneno que cambia en el tiempo**;
  - **no**: P5 + química → P5 + química + ataque → P5 + química + ataque + señal, parando en el primero que haga aparecer el aprendizaje (VA > 0 en 5 de 5).

## v0.3 · 18-10-2026, 21:55 · Rama de la física de la mutación (ADR-015)

Antes de tener datos de la rama. En P0 ya se había visto el crecimiento de la semilla 0, que es lo que motiva la rama.

| Condición | Igual que | Cambia | Criterio (5 de 5 semillas emparejadas, épocas 151–300) |
|---|---|---|---|
| P0-feliz-neutral | P0 | mutación neutral | `hidden_mean` **menor** que en P0 (nest) |
| P0-feliz-terrestre | P0 | mutación terrestre | `hidden_mean` **menor** que en P0-neutral |
| P1-peaje-neutral | P1 | mutación neutral | `thrust_mean` **menor** que en P0-neutral (P1 replicado con otra física) |
| P1-peaje-terrestre | P1 | mutación terrestre | `thrust_mean` **menor** que en P0-terrestre |

**Secundaria:** ¿cambia la conclusión de P1 sobre el cerebro? Se compara `hidden_mean` de P1 con su P0 en las tres físicas.

**Lectura:**
- Si las tres físicas llevan a la misma conclusión en P1, la física de la mutación no cambia lo que aprendemos.
- Si no coinciden, hay que elegir física antes de seguir construyendo.
- En ambos casos, la elección se hace con el responsable.

## v0.4 · 18-10-2026, 22:10 · Parada tras cada peldaño (decisión del responsable)

- **Cambio de procedimiento:** los peldaños ya no se encadenan solos. Cada uno se completa, se analiza y se decide el siguiente con el responsable.
- **P0 se completa con las tres físicas de la mutación:** "nest" (P0-feliz), "neutral" (P0-feliz-neutral) y "terrestre" (P0-feliz-terrestre), 5 semillas cada una. Después se para.
- **Qué se decide antes de lanzar P1:**
  - con qué física de mutación se sigue: una, varias en paralelo o la que el análisis aconseje;
  - si P1 necesita algún ajuste a la vista de P0.
- **Los criterios prerregistrados no cambian.**
- **Análisis:** `scripts/analyze_ladder.py` (escrito antes de ver los datos de las variantes). Media por semilla en las épocas 151–300, pendiente en esa ventana y comparaciones emparejadas con prueba de signos.
- **Mientras se decide,** la GPU avanza el resto de E2, que se pausa en cuanto haya decisión (se pierden como mucho 10 épocas de un mundo).

## v0.5 · 20-10-2026, 13:38 · P1-escalera, con la física integrada (ADR-019)

Escrito antes de tener datos de P1-escalera. Lo que se sabe de P1 viene de las reglas viejas, cambiando un factor cada vez (`p0_factores.md`).

- **Decisión del responsable (20-10, tras cerrar P0):** antes de P2 se repite P1 con todas las reglas nuevas juntas, para que cada peldaño se apoye en el anterior con la misma física. Rama `escalera-int` (sustrato 2.6.0), cola `p1int.json`, 5 semillas (0–4).
- **Primaria (la de P1, sin cambios):** `thrust_mean` **menor** que en P0-escalera, en 5 de 5 semillas emparejadas (épocas 151–300).
- **Secundarias:** `hidden_mean` y `mass_mean` menores que en P0-escalera; VA ≤ 0.
- **Descriptivas:** frente a P1-peaje-tasas-fijas (la condición vieja más parecida), aristas − nodos de la CPPN (sin selección se quedaba en 44–49) y vida media.
- **Si falla la primaria:** no se sube a P2 sin entender por qué; la integración o la calibración tendrían un problema.

## v0.6 · 20-10-2026, 16:48 · P2 con la física integrada y dos gemelos (decisión del responsable)

Escrito antes de tener datos de P2. Rama `escalera-int` (sustrato 2.6.0), cola `p2int.json`, semillas 0–4. Padre: P1-escalera (pasa en 5/5).

| Mundo | Cambia respecto a P2-escalera | Pregunta (5 de 5 semillas emparejadas, épocas 151–300) |
|---|---|---|
| **P2-escalera** | — (P1-escalera + comida en manchas quietas) | **Primaria:** `lifespan_mean` **mayor** que en P1-escalera. Secundaria: `thrust_mean` mayor (ir a por comida compensa); VA |
| P2-escalera-tasas-gen | σ y tasa estructural como gen (`MUTATION_RATES` "evolutivas") | Descriptiva: ¿se alejan σ y la tasa de 0,05 y 1 (A4)? `lifespan_mean` e `intake` frente a la base |
| P2-escalera-sexual | reproducción sexual con el cruce corregido (ADR-018) y tasas fijas | `lifespan_mean` o `intake` **mayor** que en la base en 5/5: el sexo compensa al juntar mejoras (B1) |

- **Lectura de los gemelos:**
  - si las tasas como gen bajan mucho σ o la tasa y viven más, se revisa A4;
  - si el sexo gana en 5/5, se adopta desde P2 y se anota que P0 y P1 fueron asexuales;
  - si no, se sigue con la base.
- **Orden:** la base primero; después, los gemelos.

## v0.7 · 21-10-2026, 09:11 · P3 con la física integrada (decisión del responsable)

Escrito antes de tener datos de P3. Rama `escalera-int` (sustrato 2.6.0, con el examen sin química del ADR-021), cola `p3int.json`, semillas 0–4, 300 épocas. Padre: P2-escalera (pasa en 5/5). Sin gemelos (decisión del responsable).

| Mundo | Cambia respecto a P2-escalera | Pregunta (5 de 5 semillas emparejadas, épocas 151–300) |
|---|---|---|
| **P3-escalera** | `repro_mode` "energia": se reproduce quien supera su umbral de energía (gen, 10–100) y cede al hijo una fracción de la suya (gen); la energía ya no se regala | **Primaria:** `population` **menor** que en P2-escalera (siempre 4.096). Secundarias, descriptivas: `hidden_mean`, `thrust_mean`, `lifespan_mean` frente a P2; VA |

- **Extinción:** un mundo extinguido no cuenta como "población menor". Se informa aparte y, si ocurre, se investiga la calibración antes de subir (P0–P3 son cimientos).
- **Predicción:** la comida limita la población y comer bien da más hijos. Así, la selección por comer bien pasa de "vivir más" a "dejar más descendencia". Que eso haga útil al cerebro con comida quieta es dudoso (P2 a 600 épocas: un reflejo basta). Se mira en las secundarias.
- **Batería:** examen sin química y umbrales de mancha 0,2 y laberinto 0,25 (ADR-021). Una pausa ahora sí sería una señal que revisar.

## v0.8 · 21-10-2026, 09:46 · P2-buscar: comida dispersa (decisión del responsable, ADR-022)

Escrito antes de tener datos. Rama `escalera-buscar` (sustrato 2.7.0), cola `p2buscar.json`, semillas 0–4, 300 épocas. Hermano de P2-escalera: solo cambia la comida (`K_CUT` 1,5). Examen sin química (ADR-021).

| Mundo | Cambia respecto a P2-escalera | Pregunta (5 de 5 semillas emparejadas) |
|---|---|---|
| **P2-buscar** | comida solo en las crestas: 9 % del suelo, 60 % fuera de la vista | **Primaria:** `cap_patch_success` (examen limpio) en la época 300 **mayor** que la de P2-escalera en la época 300, medida con el examen limpio sobre su checkpoint: s0 0,000, s1 0,031, s2 0,109, s3 0,016, s4 0,109. Secundarias, descriptivas: `hidden_mean` y `lifespan_mean` (151–300) frente a P2; `thrust_mean`; VA |

- **Si un mundo se pausa** (ganancia ≥ 0,2) antes de la época 300, se usa su último examen: una ganancia ≥ 0,2 implica un éxito ≥ 0,2, por encima de cualquier valor de P2. La pausa se respeta y decide el responsable.
- **Predicción:** puede evolucionar una búsqueda innata (reflejo más un patrón de movimiento) sin que crezca el cerebro y sin aprendizaje (VA ≈ 0), porque las manchas no se mueven (viswanathan1999random). Si además se conserva más cerebro que en P2, sería la primera señal de que el cerebro compensa.

## v0.9 · 21-10-2026, 16:56 · P3-escaso: hijos pagados con la mitad de comida (decisión del responsable)

Escrito antes de tener datos. P3-escalera no pasó por techo: con la comida de P2, entre el 40 y el 94 % de los vivos esperan una plaza libre, y la población se queda en 4.096. P2-buscar mostró que, con energía regalada, la comida escasa no baja la población. El responsable decidió (13:26 y 16:47) repetir P3 con menos comida, desde cero y con la cantidad calibrada (`scratchpad/p3cal2.json`: con ½, 3/3 sobreviven y se estabilizan en 2.700–2.930; con ⅜, 2/3 se extinguen al arrancar).

Rama `escalera-int` (`f02e61f`, sustrato 2.6.0, examen sin química), cola `p3escaso.json`, semillas 0–4, 300 épocas. Padre: P3-escalera.

| Mundo | Cambia respecto a P3-escalera | Pregunta (5 de 5 semillas, épocas 151–300) |
|---|---|---|
| **P3-escaso** | `k_mean` 1,902 (la mitad de 3,805) | **Primaria:** `population` media **menor que 4.096** (P3-escalera). Secundarias, descriptivas, frente a P3-escalera: `lifespan_mean`, `thrust_mean`, `hidden_mean`, VA, genes de reproducción (umbral y fracción) y examen limpio |

- **Extinción:** un mundo extinguido no cuenta como "población menor": la primaria fallaría en ese mundo. Se informa aparte (la calibración da mínimos de 16–55 bichos al arrancar).
- **Predicción:** población de 2.700–3.000; si la comida frena, la selección premia comer mejor para tener hijos, y la vida será más corta que en P3-escalera (calibración: 660–1.001). Si el cerebro sirve para comer mejor con comida escasa y quieta, las neuronas no deberían vaciarse como en P2-buscar (calibración, época 100: 0,9–1,9; dudoso).
- **Batería:** examen sin química, umbrales 0,2 y 0,25 (ADR-021). Una pausa sería una señal real: decide el responsable.

## v1.0 · 21-10-2026, 22:05 · P3-disperso: la misma comida, en pocos sitios (decisión del responsable)

Escrito antes de tener datos de los 5 mundos. Decisión del responsable (21:10): antes de P4, comprobar si con hijos pagados compensa buscar comida dispersa. Calibración (`scratchpad/p3dcal.json`, semillas 0–2, 100 épocas): 3/3 sobreviven (mínimo al arrancar 90–106 bichos; población en la época 100: 2.099–2.495).

Rama `escalera-buscar` (`8faa492`, sustrato 2.7.0, examen sin química), cola `p3disperso.json`, semillas 0–4, 300 épocas. Padre: P3-escaso. Hermano: P3-coste (ADR-023).

| Mundo | Cambia respecto a P3-escaso | Pregunta (5 de 5 semillas emparejadas) |
|---|---|---|
| **P3-disperso** | `K_CUT` 1,5 y `k_mean` 8,686: la misma comida total (1,902 / 0,219), concentrada en el 9 % del suelo | **Primaria:** `cap_patch_success` (examen limpio) en la época 300 **mayor** que en P3-escaso (s0 0,000; s1 0,000; s2 0,047; s3 0,016; s4 0,047). Secundarias, descriptivas: población, vida, empuje, neuronas, VA y genes de reproducción |

- **Extinción o pausa:** un mundo extinguido cuenta como fallo. Si la batería pausa un mundo (ganancia ≥ 0,2), se usa su último examen, se respeta la pausa y decide el responsable.
- **Predicción:** en la calibración se mueven más (empuje 8,6–9,3 frente a 6,4–7,9) y conservan más neuronas (2,2–6,0 frente a 0,9–1,9) que P3-escaso, pero en la época 100 el examen sigue bajo (0,02–0,05) y peor que los controles fijos. Con hijos casi gratis, es dudoso que buscar compense (de ahí P3-coste).

## v1.1 · 21-10-2026, 22:38 · P3-coste: cada hijo cuesta (decisión del responsable, ADR-023)

Escrito antes de tener datos de los 5 mundos. Calibración (`scratchpad/p3ccal.json`, semilla 0, 100 épocas): con coste 5, 10 y 20 los tres sobreviven (mínimo al arrancar: 8–13 bichos); vida 1.588–2.525 frente a 789, neuronas 3,4–6,3 frente a 0,9, examen en la época 100: 0,11 / 0,16 / 0,03 frente a 0,00. El responsable decidió (22:38) correr los tres costes, 5 mundos cada uno, y compararlos.

Rama `escalera-coste` (`7104c15`, sustrato 2.8.0, examen sin química), cola `p3coste.json`, semillas 0–4, 300 épocas. Orden en la GPU: tras P3-disperso, suite completa de tests en GPU (si falla, no se lanza) → coste 10 → coste 20 → coste 5 (`scratchpad/p3coste.sh`; marcas `p3coste10_hecho`, `p3coste20_hecho`, `p3coste5_hecho` y `p3coste_hecho`). Padre: P3-escaso. Hermano: P3-disperso.

| Mundo | Cambia respecto a P3-escaso | Pregunta (5 de 5 semillas emparejadas) |
|---|---|---|
| **P3-coste10**, **P3-coste20**, **P3-coste5** | `REPRO_COST` 10, 20 o 5: energía que el padre pierde con cada hijo, aparte de la que cede | **Primaria (la misma que P3-disperso, para cada coste):** `cap_patch_success` (examen limpio) en la época 300 **mayor** que en P3-escaso (s0 0,000; s1 0,000; s2 0,047; s3 0,016; s4 0,047). Secundarias, descriptivas: vida, neuronas, empuje, VA, genes de reproducción y población, y su tendencia con el coste (5 → 10 → 20) |

- **Extinción o pausa:** un mundo extinguido cuenta como fallo de ese coste. Si la batería pausa un mundo (ganancia ≥ 0,2), se usa su último examen, se respeta la pausa y decide el responsable.
- **Tres pruebas:** cada coste se juzga por separado; no se elige "el mejor" a posteriori como si fuera el único. Si pasan varios, se informa de todos.
- **Predicción:** vidas más largas y más neuronas que P3-escaso en los tres. El examen, dudoso: una sola semilla de calibración.
- **Duración estimada** (por los tiempos de la calibración: ~0,65 h por mundo): P3-disperso hasta ~02:15; tests ~35 min; cada coste ~3,3 h. Coste 10 hacia las 06:00, coste 20 hacia las 09:20 y coste 5 hacia las 12:30 (estimaciones). No cabe ningún coste más antes de las 07:00.

## v1.2 · 22-10-2026, 09:20 · P4: el mundo cambia a un ritmo dado (decisiones del responsable, 09:06 y 09:11) — borrador

Escrito antes de tener datos. Los criterios se fijan tras la calibración y antes de lanzar los 5 mundos.

- **Decisión 1 (09:06):** P4 va antes que la comida efímera y el olfato. Cambia una sola cosa, el ritmo del cambio, y la comida efímera es su hermana rápida. El olfato queda aparcado (`caminos.md`).
- **Decisión 2 (09:11).** Al diseñarlo aparecieron dos problemas:
  - Si los bichos ven la comida, «ir hacia lo que ves» sirve esté donde esté. Por eso que la comida cambie de sitio quizá no obligue a aprender. Según stephens1991change y dunlap2009components, aprender compensa cuando cambia qué señal lleva al premio.
  - Con la comida de P3-escaso (87 % del suelo), moverla apenas cambia nada.

  El responsable decidió dos familias de hermanos: **P4-sitio**, sobre P3-disperso (comida en manchas), y **P4-alga**. El padre de P4-alga será el coste 5 si pasa; si no, P3-escaso.
- **Código:** rama `escalera-p4` (worktree `panspermia-p4`, `0ca3215`, sustrato 2.9.0, desde `escalera-coste`).
  - `config.FOOD_JUMP_PERIOD`: cada periodo, las manchas saltan a un sitio al azar (fases nuevas).
  - `config.ALGA_SWAP_PERIOD`: cada periodo se sortea qué alga alimenta (A o B, que el bicho ya distingue por el signo del canal de recurso). La otra se come, pero no da energía ni cuenta como ingesta; no es veneno.
  - El sorteo usa una clave propia de cada mundo y es al azar, no periódico, para que no baste anticiparlo de forma innata (mitchell2009adaptive).
  - Apagados, el mundo es idéntico bit a bit a `escalera-coste`. Hay dos tests nuevos.

| Mundo | Padre | Cambia | Ritmo (calibración) |
|---|---|---|---|
| P4-generación | P3-disperso | la comida salta a un sitio al azar | cada 1.000 pasos (unas 2–3 generaciones de P3-disperso, que se renuevan cada 340–480 pasos) |
| P4-efímera | P3-disperso | ídem | cada 150 pasos (varias veces por vida) |
| P4-lento | P3-disperso | la deriva lenta de siempre (`K_DRIFT`) | — |
| P4-alga | coste 5 o P3-escaso | se sortea qué alga alimenta | cada 2.000 pasos (unas 2–3 generaciones de P3-escaso) |

- **Primaria propuesta (para cada mundo, 5/5 semillas emparejadas):** VA de la ingesta (gemelo congelado, media de las épocas 151–300) mayor que 0 y mayor que en el padre. Un mundo extinguido cuenta como fallo.
- **Secundarias:** neuronas, examen limpio, sonda de hambre, vida, genes de reproducción.
- **Predicción:**
  - P4-sitio: VA ≈ 0, porque la comida se ve y la regla innata basta. Puede aparecer búsqueda tras el salto (empuje, examen).
  - P4-efímera: o búsqueda localizada (hills2004dopamine) o un mundo demasiado pobre.
  - P4-alga: es donde más se espera VA > 0.
- **Calibración** (`scratchpad/p4cal.json`, `p4cal.sh`; semilla 0, 100 épocas; salida `runs/fase1d/_calP4`): arranca sola al terminar P3-coste (marca `p3coste_hecho`) y deja la marca `p4cal_hecho`.
- **Padre de P4-alga (10:51):** el coste 5 no pasó (2/5), así que P4-alga cuelga de P3-escaso.
- **Primera calibración (10:52–11:29, `runs/fase1d/_calP4`; detalle en la bitácora):** solo sobrevive P4-lento (2.108 bichos, VA −0,18 en la época 100). P4-generación se extingue una y otra vez desde la época 11; P4-efímera, en la época 1; P4-alga, en la época 5. Saltar a cualquier sitio deja las manchas a cientos de unidades (los bichos ven a 64), y con el alga sorteada la comida útil cae a la mitad de la de P3-escaso.
- **Decisión 3 del responsable (12:08):**
  - **P4-alga con el doble de algas** (`k_mean` 3,804): la comida útil media es la de P3-escaso, así que lo único que cambia respecto al padre es qué alga alimenta.
  - **P4-sitio con salto corto:** en cada periodo, todo el campo de comida se traslada `FOOD_JUMP_DIST` en una dirección al azar respecto a su sitio de siempre (traslación rígida: misma forma y misma comida). Rama `escalera-p4`, `5590724`, sustrato 2.10.0; con el salto corto apagado, idéntica bit a bit a `escalera-coste` (test nuevo: el campo es el de siempre desplazado 128 u).
- **Segunda calibración** (`scratchpad/p4cal2.json`, `p4cal2.sh`; semilla 0, 100 épocas; salida `runs/fase1d/_calP4b`, marca `p4cal2_hecho`), desde las 12:16: P4-alga con doble de algas; P4-sitio con saltos de 64 y 128 u cada 1.000 y cada 150 pasos.

## v1.3 · 22-10-2026, 15:13 · P4-alga: criterio fijado (decisión del responsable)

Escrito antes de lanzar los 5 mundos, con la calibración ya hecha.

- **Segunda calibración (12:16–13:13, `runs/fase1d/_calP4b`, semilla 0, 100 épocas):**

| Variante | ¿Viable? | VA (épocas 20 → 100) | Neuronas (época 100) |
|---|---|---|---|
| P4-alga, doble de algas | sí | 0,16 / −0,01 / −0,03 / −0,01 / 0,03 | 2,45 |
| Salto 64 u cada 1.000 pasos | sí | 0,12 / 0,14 / 0,86 / 0,77 / 0,30 | 7,0 |
| Salto 128 u cada 1.000 pasos | sí | 0,49 / 0,42 / 0,41 / 0,28 / 0,04 | 0,65 |
| Salto 64 u cada 150 pasos | extinto en la época 3 (después se recupera) | −0,12 a 0,10 | 2,3 |
| Salto 128 u cada 150 pasos | extinto | — | — |

- **Decisión del responsable (15:13):**
  - Se lanza solo **P4-alga** con el doble de algas.
  - La **comida efímera** (cambios dentro de una vida) queda **aparcada** (`caminos.md`): con 64 y 128 u cada 150 pasos se extingue.
  - Los saltos cortos cada 1.000 pasos (64 u, con el indicio de VA alto, y 128 u) quedan en espera hasta ver P4-alga.
- **Mundo:** rama `escalera-p4` (`2e41573`, sustrato 2.10.0), cola `p4.json`. Es P3-escaso con `k_mean` 3,804 (el doble de algas, para que la comida útil media sea la de P3-escaso) y `ALGA_SWAP_PERIOD` 2.000. Semillas 0–4, 300 épocas, desde cero. Antes, la suite completa en GPU; si falla, no se lanza (`scratchpad/p4alga.sh`, marca `p4alga_hecho`).
- **Primaria (5/5 semillas emparejadas):** VA de la ingesta (gemelo congelado), media de las épocas 151–300, **mayor que 0 y mayor que en P3-escaso** con la misma semilla. Valores de P3-escaso: s0 −0,000; s1 +0,001; s2 +0,009; s3 −0,021; s4 −0,003. Un mundo extinguido o pausado sin revisión cuenta como fallo.
- **Secundarias, descriptivas:** VA_log, neuronas, empuje, ingesta, vida, población, genes de reproducción, examen limpio (época 300) y sonda de hambre. Además, una medida propia de P4-alga: la fracción de la ingesta que viene del alga que alimenta en cada momento, si se puede calcular sin tocar la simulación.
- **Predicción:** P4-alga es donde más se espera VA > 0 (stephens1991change, dunlap2009components). Pero la calibración da VA ≈ 0 a partir de la época 40 y el cerebro se vacía (2,45 neuronas). Lo más probable es que salga negativo: con el signo del canal de recurso visible, puede bastar una regla innata del tipo «come las dos y quédate donde ganes energía».
- **Duración estimada** (por la calibración, ~0,23 h por 100 épocas): suite ~40 min y unas 3,5 h para los 5 mundos.

## v1.4 · 22-10-2026, 19:55 · P4-salto64: criterio fijado (decisión del responsable)

Escrito antes de lanzar, con P4-alga ya cerrado (no pasa, 3/5; `p0_factores.md`).

- **Decisión del responsable (19:55):** tras P4-alga se lanza el hermano de P4-sitio con salto corto de 64 u cada 1.000 pasos. El de 128 u y las semillas extra de P4-alga quedan en espera.
- **Mundo:** rama `escalera-p4` (`ba5e16e`, sustrato 2.10.0), cola `p4sitio.json`. Es P3-disperso (`K_CUT` 1,5, `k_mean` 8,686) con `FOOD_JUMP_PERIOD` 1.000 y `FOOD_JUMP_DIST` 64: cada 1.000 pasos (unas 2–3 generaciones) todo el campo de comida se desplaza 64 u en dirección al azar respecto a su sitio de siempre. Semillas 0–4, 300 épocas, desde cero. El código es el mismo con el que la suite pasó a las 15:43 (84 correctos y 1 omitido): solo se añade la cola, así que no se repite la suite.
- **Primaria (5/5 semillas emparejadas):** VA de la ingesta (gemelo congelado), media de las épocas 151–300, **mayor que 0 y mayor que en P3-disperso** con la misma semilla. Valores de P3-disperso: s0 −0,020; s1 +0,026; s2 +0,070; s3 −0,118; s4 +0,012. Un mundo extinguido o pausado sin revisión cuenta como fallo.
- **Secundarias, descriptivas:** VA_log, pruebas de VA positivas, neuronas, empuje, masa, ingesta, vida, nacimientos, población, genes de reproducción, examen limpio (época 300) y sonda de hambre (con `K_CUT` y el salto activados).
- **Predicción:** es el único hermano con VA alto sostenido en la calibración (0,86 y 0,77 en las épocas 60 y 80, una semilla). Pero el VA alto de las primeras épocas ya se apagó antes en los mundos de comida dispersa (P2-buscar, P3-disperso) y en P4-alga solo se sostuvo en un mundo de cinco. Lo más probable: VA > 0 en varios mundos, pero no en 5/5.
- **Duración estimada:** unas 3–3,5 h (P4-alga tardó 37 min por mundo).

## v1.5 · 22-10-2026, 22:45 · La tripa (ADR-024): criterio fijado (decisión del responsable, 22:22)

Escrito antes de lanzar.

- **Mundos** (rama `escalera-tripa`, sustrato 3.0.0, cola `tripa.json`; semillas 0–4, 300 épocas, desde cero):
  - **P4-alga-tripa:** P4-alga (doble de algas, `ALGA_SWAP_PERIOD` 2.000) con la tripa.
  - **P4-alga-sin-tripa:** el mismo mundo en el mismo sustrato, con la entrada a 0 (control).
  - **P3-escaso-tripa:** P3-escaso con la tripa (contraste: la comida que alimenta no cambia nunca).
- Antes, la suite completa en GPU; si falla, no se lanza (`scratchpad/tripa_noche.sh`, que espera a `p4sitio_hecho`; log `runs/fase1d/tripa.log`, marca `tripa_hecho`).
- **Primaria (5/5 semillas emparejadas):** VA de la ingesta (gemelo congelado), media de las épocas 151–300, de P4-alga-tripa **mayor que 0 y mayor que en P4-alga-sin-tripa** con la misma semilla. Un mundo extinguido o pausado sin revisión cuenta como fallo.
- **Contraste de la teoría (secundaria prerregistrada):** en P3-escaso-tripa se predice VA ≈ 0. Si P4-alga-tripa pasa y P3-escaso-tripa no muestra VA > 0, es lo que predicen stephens1991change y dunlap2009components: aprender compensa cuando cambia qué pista lleva al premio.
- **Secundarias, descriptivas:**
  - las de v1.3 (VA_log, pruebas de VA positivas, neuronas, empuje, ingesta, vida, población, genes, examen, sonda de hambre);
  - el diagnóstico de `diag_aprender.py`: correlación entre la modulación y lo comido, peso de la tripa en las moduladoras y suelo de ruido del VA;
  - P4-alga-sin-tripa frente a P4-alga (2.10), para ver cuánto cambia el sustrato nuevo por sí solo.
  - **Añadida a las 23:15, antes de lanzar** (artículo traído por el responsable: xu2026sparse; schultz1997neural): ¿la modulación `m` sigue a la tripa en bruto o a su sorpresa? Se medirá por mundo la correlación de `m` con la tripa y con la tripa menos su media reciente del propio bicho (huella exponencial; detalle en el análisis). También, si anular las moduladoras que más pesan de la tripa reduce la ingesta más que anular otras al azar. Solo se describe; no forma parte del criterio.
- **Predicción:** abierta. Es la primera vez que la consecuencia de comer es visible. Si la evolución engancha la tripa a la modulación, debería aparecer VA > 0 en P4-alga-tripa. Lo más probable, de todos modos, es que pase en algunos mundos y no en 5/5.
- **Duración estimada:** suite ~30 min y unas 9 h para los 15 mundos (unos 37 min cada uno).

## v1.6 · 22-10-2026, 23:50 · Pruebas de la masa (decisión del responsable, 23:45)

Escrito antes de lanzar. En P4-salto64, aprender compensó solo en los mundos que conservaron cuerpos grandes (s0, s2). La dispersión de los hijos no lo explica (bitácora, 23:28–23:40). El responsable pidió tres pruebas causales.

- **Rama** `escalera-masa` (worktree `panspermia-masa`, `62fcb9b`, sustrato 2.11.0), desde `escalera-p4`. `config.BODY_RADIUS_FIXED` y `config.BIRTH_OFFSET_FIXED`; con los dos a 0, idéntica bit a bit a 2.10. Script `scripts/branch_run.py`.
- **Mundos** (todos P4-salto64; 300 épocas):
  1. **P4-salto64-grande:** radio fijo 6,6 (masa 2,72), semillas 0–4.
  2. **P4-salto64-chico:** radio fijo 2,25 (masa 0,32), semillas 0–4.
  3. **P4-salto64-rama1–3:** s1 (que encogió) y s2 (que siguió grande), retomados en la época 50 con otro azar. Antes, `masa_e50.json` repite s1 y s2 hasta la época 50, que debe coincidir con P4-salto64.
  4. **P4-salto64-hijo8:** el hijo nace siempre a 8 u del padre (2·`RADIUS_REF`), semillas 0–4.
- **Preguntas y lectura:**
  - (1) y (2): ¿el cuerpo grande hace que aprender compense? Sí si el VA de las épocas 151–300 es mayor en «grande» que en «chico» en 5/5 semillas emparejadas, y mayor que 0 en «grande» en 5/5.
  - (3): ¿es contingente el camino de cada mundo? Sí si alguna rama de s1 acaba grande (masa > 1,5 en las épocas 151–300) o alguna de s2 acaba pequeña.
  - (4): ¿influye la distancia del hijo? Se compara con P4-salto64: el número de mundos grandes y su VA. Es descriptiva: con 5 mundos, solo un cambio claro (0 o 5 mundos grandes) contaría.
- **Orden y duración:** `scratchpad/masa_dia.sh` espera a `tripa_hecho`. Después pasa la suite en GPU y hace e50 → ramas → `masa.json` (log `runs/fase1d/masa.log`, marca `masa_hecho`). Unas 12–13 h, desde las ~9:15 del 23-10.

## v1.7 · 23-10-2026, 13:30 · Comer frena (ADR-025): criterio fijado (decisión del responsable, 13:15)

Escrito antes de lanzar.

- **Mundos** (rama `escalera-frena`, `b7dc22e`, sustrato 3.1.0; semillas 0–4, 300 épocas, desde cero):
  - **P4-alga-tripa-frena:** P4-alga-tripa con comer frena. Su padre es P4-alga-tripa.
  - **P4-alga-sin-tripa-frena:** lo mismo con la tripa apagada. ¿Hace falta la tripa cuando comer es una decisión?
  - **P3-escaso-tripa-frena:** contraste; la comida que alimenta no cambia nunca.
- **Orden:** `scratchpad/frena_noche.sh` espera a `masa_hecho`. Después:
  1. pasa la suite completa en GPU; si falla, no se lanza;
  2. calibra con la cola `frenacal.json`, factor 0 y 0,25, semilla 0, 30 épocas;
  3. lanza `frena.json` (factor 0) si ese factor es viable (sin extinción y con 500 bichos o más al final); si no, `frena025.json` (0,25); si ninguno es viable, se para.
  - Log en `runs/fase1d/frena.log`; marca `frena_hecho`.
- **Primaria (5/5 semillas emparejadas):** VA de la ingesta (gemelo congelado), media de las épocas 151–300, de P4-alga-tripa-frena **mayor que 0 y mayor que en P4-alga-tripa** con la misma semilla. Un mundo extinguido o pausado sin revisión cuenta como fallo.
- **Comprobación de la manipulación (secundaria prerregistrada):** con `diag_comer.py`, comer debe pasar a ser una decisión. Se mira si la probabilidad de comer donde no hay nada baja claramente respecto a sobre comida buena; en P4-alga-tripa era igual o mayor (85–98 % frente a 63–95 %). Si no cambia, la manipulación ha fallado y el VA no se interpreta.
- **Secundarias, descriptivas:**
  - frena con tripa frente a frena sin ella (VA emparejado);
  - P3-escaso-tripa-frena (se predice VA ≈ 0);
  - las de v1.3 y v1.5 (VA_log, pruebas positivas, neuronas, empuje, ingesta, vida, población, genes, examen, sonda de hambre, modulación frente a tripa y sorpresa, peso de la tripa en las moduladoras);
  - el suelo de ruido del VA, en GPU cuando quede libre.
- **Predicción:** abierta. Es la primera vez que equivocarse al comer cuesta algo. La bibliografía (§18) predice que la decisión de comer debería volverse sensible al contexto y que el aprendizaje tiene más donde apoyarse. Aun así, 5/5 es exigente.
- **Duración estimada:** suite de ~1 h, calibración de ~25 min y unos 10 h para los 15 mundos. Empezaría hacia la 1:00 del 24-10 y acabaría hacia las 12:00.

## v1.8 · 23-10-2026, 13:58 · Comer frena con 10 mundos por condición (decisión del responsable, 13:55)

Escrito antes de lanzar; sustituye la primaria de v1.7. Motivo: la revisión `docs/escalera/condiciones_aprendizaje.md` (C8). El aprendizaje evoluciona solo en una fracción de los linajes (7 % en pontes2020evolutionary; la mitad de las ejecuciones en niv2002evolution), así que 5/5 con 5 mundos puede no detectar un efecto real.

- **Mundos:** las mismas tres familias de v1.7, con las **semillas 0–9** (30 mundos; colas `frena.json` y `frena025.json` de `escalera-frena`, `cba2bf0`). El padre, P4-alga-tripa, se amplía con las semillas 5–9 (cola `tripa10.json` de `escalera-tripa`, `0c96723`; mismo código que las semillas 0–4).
- **Primaria (prueba de signos emparejada, unilateral):** pares por semilla. Un par es favorable si el VA de las épocas 151–300 de P4-alga-tripa-frena es mayor que 0 y mayor que el del padre con la misma semilla. **Pasa con al menos 9 pares favorables de 10** (p = 0,011 si no hubiera efecto). Un mundo extinguido o pausado sin revisión cuenta como desfavorable.
- **Lo demás no cambia:** la comprobación de la manipulación (`diag_comer.py`) y las secundarias de v1.7, ahora con 10 semillas.
- **Orden:** `scratchpad/frena_noche3.sh` espera a `masa_hecho` y `frena_ok` (visto bueno dado a las 13:57). Después: suite completa en GPU, calibración, los 30 mundos y el padre (semillas 5–9). Marca `frena_hecho`.
- **Duración estimada:** unas 23 h (35 mundos de ~0,6 h, más la suite y la calibración). Empezaría hacia las 3:15 del 24-10 y acabaría hacia las 2:00 del 25-10.
- **Decisión del responsable sobre C1 (13:55):** solo el freno en este peldaño, un cambio cada vez. Que el alga buena se sortee para cada bicho al nacer queda para el peldaño siguiente.
