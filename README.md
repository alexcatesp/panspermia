# Panspermia

Ecosistema de vida artificial distribuido: agentes que evolucionan por selección natural (sin función de fitness), aprenden durante su vida con plasticidad hebbiana evolucionada y migran entre "islas" que cada participante ejecuta en su PC.

**Estado**: fase 0 cerrada (núcleo 2D determinista bit a bit). Fase 1 implementada: ataque con carroña (energía conservada), señal, senescencia, biogeografía, métricas de conducta, novedad, diversidad y comunicación, prueba de plasticidad congelada, batería de capacidad con pausa (salvaguarda 5) y visor web del «mundo».

**Resultado de la fase 1** (ADR-010, etiqueta `fase1-base`): ecología estable y sin extinciones, pero aprender en vida no compensa (valor del aprendizaje negativo en las 5 semillas), los cerebros encogen y los grupos de conducta se diluyen. La batería de capacidad pausó 4 de las 5 islas por la prueba del anillo, que resultó ser un falso positivo: un agente sin cerebro que solo avanza recto la supera (`scripts/capability_controls.py`). Las islas siguen pausadas a la espera de que el responsable decida sobre la batería v2 propuesta. La fase 1b (química y algas estacionales, ADR-008) está en la rama `fase1b`.

## Documentos

- [Especificación](docs/spec.md) — arquitectura, genoma, cerebro, red P2P, métricas, fases, salvaguardas.
- [Bibliografía](docs/bibliografia.md) — trabajos en los que se basa.
- [Decisiones](docs/decisiones.md) — registro de decisiones de diseño.
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
| `capability.py` | Batería de capacidad (salvaguarda 5): comunicación, anillo, laberinto |
| `record.py` | Grabación de épocas para el visor |
| `run.py` | Runner: Parquet, Orbax, pruebas periódicas y pausa por capacidad |
| `viewer.py` + `viewer_static/` | Visor web local del mundo |

## Licencias

Código: [Apache-2.0](LICENSE) · Documentación: CC BY 4.0 · Genomas compartidos: CC0.
