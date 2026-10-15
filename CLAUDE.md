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
- Tests: `pytest` (~20 min en GPU) y `pytest --runslow` (incluye 5 semillas × 100 épocas). `XLA_PYTHON_CLIENT_PREALLOCATE` y `XLA_FLAGS` se fijan en `panspermia/__init__.py` antes de importar JAX.
- Ejecutar una isla: `python -m panspermia.run --seed 0 --epochs 100 --out runs/s0`; benchmark: `python scripts/bench.py`.

## Estado actual y siguiente trabajo

- Fase 0 cerrada (ADR-005, ADR-006). Fase 1 implementada (ADR-007); la aceptación (5 semillas × 500 épocas, ~4 h) se lanza con `scripts/phase1_acceptance.py` y se evalúa con su subcomando `eval`.
- Estructura del estado (`island.IslandState`): arrays con eje N delante; `Genome`, `Phenotype`, `Lineage`, `Behavior` son `flax.struct.dataclass`. Cada paso usa `fold_in(key, step)`. Nacimientos en lote fijo de `MAX_BIRTHS_PER_STEP` dentro de `lax.cond`. `world_step(..., plastic=, births=)` con flags estáticos.
- Las métricas en `metrics.py` y la batería en `capability.py` solo observan: nunca deben influir en la reproducción.
- Salvaguarda 5: los umbrales están en `config.CAPABILITY_PAUSE_THRESHOLDS`; solo una persona puede subirlos (vía `CAPABILITY_REVIEW.json` o un ADR). No cambiarlos para que una ejecución «pase».
- Visor: `python -m panspermia.viewer runs/<x>`; la página está en `src/panspermia/viewer_static/index.html` (sin dependencias externas). Probarla con Playwright.
- Pendiente de decidir (propuesta tras la fase 1): islas con hipótesis distintas en la red, techo de tamaño del genoma, verificación de Network Tierra y MODES.

## Convenciones

- Código e identificadores en inglés; documentación y mensajes de commit en español.
- Tipos anotados; `chex`/`jaxtyping` para formas de arrays.
- Cada cambio de formato de genoma incrementa `SUBSTRATE_VERSION` (major si rompe compatibilidad) y añade función `upgrade` si es minor.
- Commits pequeños; un criterio de aceptación por PR cuando sea posible.
