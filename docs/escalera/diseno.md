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
