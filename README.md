# Panspermia

Ecosistema de vida artificial distribuido: agentes que evolucionan por selección natural (sin función de fitness), aprenden durante su vida con plasticidad hebbiana evolucionada y migran entre "islas" que cada participante ejecuta en su PC.

**Estado**: fase 0 (núcleo 2D) implementada: genoma CPPN serializable y validado, desarrollo genotipo→fenotipo, cerebro recurrente con plasticidad ABCD modulada, mundo 2D toroidal con recursos y sensores por rayos, isla determinista bit a bit bajo `jit` + `lax.scan`, estadísticas Parquet y checkpoints Orbax.

## Documentos

- [Especificación](docs/spec.md) — arquitectura, genoma, cerebro, red P2P, métricas, fases, salvaguardas.
- [Bibliografía](docs/bibliografia.md) — trabajos en los que se basa.
- [Decisiones](docs/decisiones.md) — registro de decisiones de diseño.

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
python scripts/bench.py                                         # pasos-agente/s
duckdb -c "SELECT epoch, population, births, hidden_mean FROM 'runs/s0/stats/*.parquet' ORDER BY epoch"
```

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
| `metrics.py` | Estadísticas por época (solo observan) |
| `run.py` | Runner con Parquet y Orbax |

## Licencias

Código: [Apache-2.0](LICENSE) · Documentación: CC BY 4.0 · Genomas compartidos: CC0.
