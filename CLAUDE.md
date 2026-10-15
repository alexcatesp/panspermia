# CLAUDE.md — Panspermia

Ecosistema evolutivo distribuido: agentes encarnados que evolucionan por selección ecológica (sin fitness explícita), aprenden en vida con plasticidad hebbiana evolucionada y migran entre islas P2P.

## Fuente de verdad

- `docs/spec.md` es la especificación. Si el código y la spec discrepan, gana la spec; si la spec está mal, propón el cambio y regístralo en `docs/decisiones.md` antes de implementarlo.
- `docs/bibliografia.md`: referencias. Las marcadas con † no están verificadas.
- `src/panspermia/config.py` concentra todas las constantes numéricas de la spec. No hardcodees números en otros módulos.

## Principios innegociables (spec §Objetivo y principios)

1. Ninguna métrica externa decide la reproducción. Las métricas solo observan.
2. El genoma es datos, nunca código. Validar rangos en toda entrada externa.
3. Determinismo bit a bit: misma (versión de sustrato, semilla, estado) → mismo resultado. Toda aleatoriedad vía `jax.random` con claves derivadas; prohibido `numpy.random` o `random` en el núcleo.
4. Estado en arrays de tamaño fijo con máscaras; nada de bucles Python por agente. Todo el paso de simulación bajo `jit` y `lax.scan`.
5. Sin retropropagación dentro del agente.

## Entorno

- Python ≥ 3.11, JAX con CUDA 12. En Windows: **WSL2** (JAX con GPU no corre nativo en Windows). GPU de referencia: RTX 5070 12 GB; GPU de desarrollo: RTX 5070 Ti 16 GB.
- Al arrancar cualquier simulación llamar a `panspermia.island.setup_determinism()` antes de usar JAX: fija `XLA_FLAGS=--xla_gpu_deterministic_ops=true`, `jax_default_matmul_precision="highest"` y desactiva la preasignación de VRAM.
- Distro WSL: `Ubuntu-24.04` (en `D:\WSL\Ubuntu-24.04`, usuario `aleja`); venv en `~/.venvs/panspermia`. Instalar: `bash scripts/setup_wsl.sh` (usa pip; `uv pip install` falla con las ruedas NVIDIA, ver ADR-005).
- Ejecutar desde Windows: `wsl -d Ubuntu-24.04 --cd /mnt/d/Development/panspermia -- bash -lc 'source ~/.venvs/panspermia/bin/activate; python -m pytest -q'`.
- Tests: `pytest` (rápidos, ~5 min en GPU) y `pytest --runslow` (incluye 5 semillas × 100 épocas).
- Ejecutar una isla: `python -m panspermia.run --seed 0 --epochs 100 --out runs/s0`; benchmark: `python scripts/bench.py`.

## Estado actual y siguiente trabajo

Fase 0 (núcleo 2D) implementada: `genome`, `develop`, `brain`, `world`, `island`, `metrics`, runner con Parquet + Orbax y benchmark. Decisiones de implementación en `docs/decisiones.md` (ADR-005; benchmark y resultados de aceptación en ADR-006).

Estructura del estado (`island.IslandState`): arrays con eje N delante; `Genome` y `Phenotype` son `flax.struct.dataclass`. Cada paso usa `fold_in(key, step)`. Los nacimientos se procesan en un lote fijo de `MAX_BIRTHS_PER_STEP` dentro de `lax.cond`.

Siguiente: fase 1 (ataque, cadáveres, métricas de conducta/novedad/diversidad, prueba de plasticidad congelada) y, en paralelo tras cerrar la 1, la 4a.

## Convenciones

- Código e identificadores en inglés; documentación y mensajes de commit en español.
- Tipos anotados; `chex`/`jaxtyping` para formas de arrays.
- Cada cambio de formato de genoma incrementa `SUBSTRATE_VERSION` (major si rompe compatibilidad) y añade función `upgrade` si es minor.
- Commits pequeños; un criterio de aceptación por PR cuando sea posible.
