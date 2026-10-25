# Panspermia

Ecosistema de vida artificial distribuido: agentes que evolucionan por selección natural (sin función de fitness), aprenden durante su vida con plasticidad hebbiana evolucionada y migran entre "islas" que cada participante ejecuta en su PC.

**Estado**: fase 0 cerrada (núcleo 2D determinista bit a bit). Fase 1 implementada: ataque con carroña (energía conservada), señal, senescencia, biogeografía, métricas de conducta, novedad, diversidad y comunicación, prueba de plasticidad congelada, batería de capacidad con pausa (salvaguarda 5) y visor web del «mundo».

**Resultado de la fase 1** (ADR-010, etiqueta `fase1-base`): ecología estable y sin extinciones, pero aprender en vida no compensa (valor del aprendizaje negativo en las 5 semillas), los cerebros encogen y los grupos de conducta se diluyen. La batería de capacidad pausó 4 de las 5 islas por la prueba del anillo, que resultó ser un falso positivo: un agente sin cerebro que solo avanza recto la supera (`scripts/capability_controls.py`). Con la batería v2 (ADR-011: referencia = mejor política trivial con los mismos cuerpos, mancha de comida a 90 u) las cinco islas completan 500 épocas sin pausa (3.100–3.800 bichos; mejor ganancia 0,156 < 0,2).

**Fase 1b** (ADR-008, sustrato 2.0.0, integrada en main): química artificial (nutriente, toxina y feromona) y dos tipos de alga, uno tóxico, que se alternan por regiones móviles con una rampa de toxicidad de 40 épocas. En la aceptación (5 semillas × 500 épocas) sobreviven 2 de 5 mundos. En ellos los cerebros crecen (s0: de 8 a 21 neuronas ocultas) y uno se vuelve pacífico (s2: ataque 0,45). La sonda emparejada indica que aprender aumenta la población y la ingesta. El código de la fase 1 original (sustrato 1.x) queda en la etiqueta `fase1-base`.

**Fase 1d** (en curso, rama `fase1d`): barridos controlados de las condiciones en que aprender compensa (ADR-012, protocolo en `docs/fase1d/diseno.md`). El registro cronológico de todo lo probado está en `docs/bitacora.md`. La sonda de recompensa (`scripts/reward_probe.py`) no encuentra una señal de castigo consistente en las neuronas moduladoras. Por eso E9 (rama `fase1d-e9`, sustrato 3.0.0) añade un sentido de malestar tras comer veneno y lo compara con mundos sin él. **Resultado de E1** (50 mundos, 49 sobreviven): aprender en vida compensa casi siempre que hay veneno (VA_log > 0 en 40 de 44 mundos), pero no aparece la campana que predice la teoría (H1), y la comparación entre ciclos regulares y cambios al azar (H2) no es concluyente. El análisis destapó cuatro fallos del diseño (diseño v0.8). Los corrige **E1b** (rama `fase1d-e1b`): un control uniforme, 5 semillas más y una sonda del reloj desincronizado.

**Escalera de complejidad** (ADR-014, rama `escalera`): rehace el camino **un interruptor cada vez**, desde un mundo feliz sin selección (P0), pasando por el peaje a vivir (P1), la comida (P2–P4) y los hijos pagados (P3), hasta la comida venenosa (P5). Cada peldaño responde a una pregunta de sí o no prerregistrada (`docs/escalera/diseno.md`). El primer peldaño ya mostró que los cerebros crecen solos sin selección, por cómo está programada la mutación. Una rama (ADR-015) repite P0 y P1 con una mutación neutral y otra terrestre (que pierde más de lo que gana) antes de seguir. Estado a 22-10: P0, P1 y P2 cerrados; P3 (hijos pagados) pasa con la mitad de comida; con esa comida concentrada en pocos sitios (P3-disperso) no aprenden a buscar mejor (3/5), y con un coste por hijo (P3-coste, ADR-023) tampoco, con ningún coste (5: 2/5; 10 y 20: 3/5): viven más y tienen hijos caros, pero no aprenden. El siguiente peldaño, P4, varía cada cuánto cambia de sitio la comida (P4-sitio) o qué alga alimenta (P4-alga). P4-alga (cada 2.000 pasos se sortea qué alga alimenta) no pasa (3/5): aprender compensa en algunos mundos y perjudica en otros, y solo uno lo mantiene; con saltos cortos de la comida (P4-salto64) tampoco pasa (2/5), aunque en dos mundos aparecen cuerpos grandes de vida corta, cerebros más grandes y aprender compensa: es el mejor indicio hasta ahora. Un diagnóstico mostró que el cerebro casi no nota cuándo ha comido. Por eso, con la decisión ADR-024, se le ha dado un sentido nuevo, la «tripa», que le dice cuánta energía le ha dado lo que acaba de comer (sustrato 3.0.0, rama `escalera-tripa`). La tripa no pasa (4/5, 23-10): comer resultó ser un reflejo siempre encendido y gratis, sin nada que aprender. Por eso, con ADR-025, comer frena: mientras come, el bicho no puede moverse (sustrato 3.1.0, rama `escalera-frena`), como en la naturaleza. Con el freno total desde el principio se extinguen, así que el freno se endurece poco a poco (sustrato 3.2.0). Con el freno no pasa (6 de 10 mundos mejoran al padre, 25-10): aprender en vida compensa más (mediana +68 % frente a +11 %), pero lo que aprenden es a comer menos y moverse más, no a distinguir dónde hay comida. Y es sobre todo maduración: criados sin comida, los bichos aprenden casi lo mismo; la plasticidad termina de construir un cerebro que nace incompleto. El siguiente peldaño (ADR-026, sustrato 3.3.0, rama `escalera-algabicho`) sortea para cada bicho, al nacer, qué alga le alimenta, para que solo la experiencia pueda decírselo. Tampoco pasa (0 de 10 mundos, 25-10): no aprenden a comer su alga y dejar la otra, aunque pasan más tiempo sobre la suya que sus vecinos congelados. Aprender en vida compensa más que nunca (+136 %), pero sigue siendo sobre todo maduración. Una prueba con el alga cambiada durante la crianza mostró que no aprenden cuál es la suya: les basta un reflejo de la tripa, porque probar un alga es casi gratis. El peldaño siguiente (ADR-027, sustrato 3.5.0, rama `escalera-manchas`) reparte la comida en manchas lejanas, cada una de un solo tipo de alga, para que equivocarse cueste un viaje. Una sonda nueva, con media población congelada en el mismo mundo, mostró en octubre que **cada bicho sí aprende en vida** en los mundos de P3 y P4 que conservan la plasticidad: aprende a no cerrar la boca sobre la comida y gana entre un 15 % y un 166 % de ingesta. La medida anterior, el VA de población, no lo veía porque mide el efecto del aprendizaje en el tamaño de la población. Desde entonces la sonda mixta es la medida principal. Buscar comida sigue siendo innato. La sonda de hambre (`scripts/hunger_probe.py`, rama `escalera-int`) engaña al cerebro sobre su energía; todavía no encuentra una respuesta común que parezca hambre.

## Documentos

- [Especificación](docs/spec.md) — arquitectura, genoma, cerebro, red P2P, métricas, fases, salvaguardas.
- [Bibliografía](docs/bibliografia.md) — trabajos en los que se basa.
- [Decisiones](docs/decisiones.md) — registro de decisiones de diseño.
- [Bitácora](docs/bitacora.md) — cuaderno de laboratorio: cada experimento con su código, datos y resultado.
- [Caminos](docs/caminos.md) — opciones probadas: descartadas, aparcadas (con su condición de reapertura) y en estudio.

## Requisitos

- Python ≥ 3.11
- GPU NVIDIA con CUDA 12 (Linux o Windows con WSL2)

```bash
# En WSL2 (Ubuntu 24.04), desde la raíz del repo
bash scripts/setup_wsl.sh            # venv en ~/.venvs/panspermia con JAX CUDA 12
source ~/.venvs/panspermia/bin/activate
pytest                               # tests rápidos
pytest --runslow                     # + criterio de no extinción (5 semillas × 100 épocas)
```

## Uso

```bash
python -m panspermia.run --seed 0 --epochs 100 --out runs/s0   # isla aislada
python -m panspermia.viewer runs/s0                             # visor: http://127.0.0.1:8765
python scripts/bench.py                                         # pasos-agente/s
python scripts/phase1_acceptance.py run --out runs/phase1       # 5 semillas × 500 épocas
python scripts/compare_runs.py runs/phase1 runs/phase1b --to 100 # compara dos lotes
PYTHONPATH=src python -m panspermia.panel runs/fase1d          # panel en vivo: escalera (planteamiento, vídeo y resultados por peldaño), árbol y avance (127.0.0.1:8766)
python scripts/capability_controls.py                           # controles triviales de la batería
duckdb -c "SELECT epoch, population, births, hidden_mean FROM read_parquet('runs/s0/stats/*.parquet', union_by_name=true) ORDER BY epoch"
```

Cada 50 épocas el runner graba una época completa para el visor; cada 20 mide el valor del aprendizaje (clon con plasticidad congelada) y cada 100 ejecuta la batería de capacidad. Si una prueba supera su umbral, la isla se **pausa** (`CAPABILITY_PAUSE.json`, código de salida 3) hasta que una persona la revise y cree `CAPABILITY_REVIEW.json` (ver ADR-007).

El runner guarda una fila de estadísticas por época (demografía y complejidad) en `stats/*.parquet`, checkpoints Orbax cada 10 épocas en `checkpoints/` (últimos 5 + uno de cada 100) y reanuda desde el último si existe.

## Estructura

| Módulo | Contenido |
| --- | --- |
| `config.py` | Todas las constantes numéricas |
| `genome.py` | Genoma, mutación, forma canónica, BLAKE3, msgpack+zstd, validación |
| `develop.py` | CPPN vectorizada → fenotipo (pesos y reglas por sinapsis) |
| `brain.py` | Paso recurrente y plasticidad hebbiana ABCD modulada |
| `world.py` | Mundo 2D: biogeografía, recursos, vecindad, rayos, física, energía |
| `island.py` | `IslandState`, `world_step`, `epoch`, nacimientos y reinyección |
| `metrics.py` | Estadísticas por época, descriptor conductual, novedad, grupos, Bedau-Packard (solo observan) |
| `capability.py` | Batería de capacidad (salvaguarda 5): comunicación, mancha lejana y laberinto, con el examen sin química (ADR-021, rama `escalera-int`) |
| `record.py` | Grabación de épocas para el visor |
| `run.py` | Runner: Parquet, Orbax, pruebas periódicas y pausa por capacidad |
| `viewer.py` + `viewer_static/` | Visor web local del mundo |

## Licencias

Código: [Apache-2.0](LICENSE) · Documentación: CC BY 4.0 · Genomas compartidos: CC0.
