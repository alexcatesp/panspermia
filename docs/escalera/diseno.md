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

## v0.2 · 18-10-2026, 19:05 · Ramas tras P5 (decisión del responsable)

Se añade antes de tener datos y no cambia ningún criterio de P0–P5.

- **P0–P3 son cimientos.** Si uno falla, se repara (calibración o motor) antes de subir.
- **P5 es la bifurcación.** Se mira la mediana de VA_log_population de las épocas 151–300 y su signo por semilla:
  - **sí** (VA > 0 en 5 de 5): **P6 · veneno que cambia en el tiempo**;
  - **no**: P5 + química → P5 + química + ataque → P5 + química + ataque + señal, parando en el primero que haga aparecer el aprendizaje (VA > 0 en 5 de 5).
