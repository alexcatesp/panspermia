# CLAUDE.md — Panspermia

Ecosistema evolutivo distribuido: agentes encarnados que evolucionan por selección ecológica (sin fitness explícita), aprenden en vida con plasticidad hebbiana evolucionada y migran entre islas P2P.

## Fuente de verdad

- `docs/spec.md` es la especificación. Si el código y la spec discrepan, gana la spec; si la spec está mal, propón el cambio y regístralo en `docs/decisiones.md` antes de implementarlo.
- `docs/bibliografia.md`: referencias. Las marcadas con † no están verificadas.
- `docs/bibliografia/<fase>/`: bibliografía por fase para un posible artículo (README con síntesis, hueco y fichas; `refs.bib` con DOI comprobados; `pdf/` solo local y en `.gitignore`). Al citar en un ADR, usar estas claves.
- `docs/bitacora.md`: **cuaderno de laboratorio cronológico**. Añadir una entrada por cada experimento, prueba o diagnóstico (qué, commit, datos en `runs/`, resultado con números y conclusión: firme, indicio, descartado o aparcado), incluido lo que falla. Es la base de la publicación.
- `docs/caminos.md`: registro de caminos descartados, aparcados (con su condición de reapertura) y en estudio. Actualizarlo cada vez que una opción se pruebe y falle o funcione.
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
- Aceptación de la fase 1 hecha (ADR-010, tag `fase1-base`): el anillo de la batería v1 era un falso positivo (avanzar recto sin cerebro da 1,0). Con la batería v2 (ADR-011) y `CAPABILITY_REVIEW.json` firmados por el responsable, `runs/phase1/s1–s4` se reanudaron y las cinco islas terminan 500 épocas sin pausa. **No crear más `CAPABILITY_REVIEW.json` sin decisión del responsable.** `scripts/compare_runs.py` compara lotes en una ventana de épocas.
- Estructura del estado (`island.IslandState`): arrays con eje N delante; `Genome`, `Phenotype`, `Lineage`, `Behavior` son `flax.struct.dataclass`. Cada paso usa `fold_in(key, step)`. Nacimientos en lote fijo de `MAX_BIRTHS_PER_STEP` dentro de `lax.cond`. `world_step(..., plastic=, births=)` con flags estáticos.
- Las métricas en `metrics.py` y la batería en `capability.py` solo observan: nunca deben influir en la reproducción.
- Salvaguarda 5: los umbrales están en `config.CAPABILITY_PAUSE_THRESHOLDS`; solo una persona puede subirlos (vía `CAPABILITY_REVIEW.json` o un ADR). No cambiarlos para que una ejecución «pase».
- Visor: `python -m panspermia.viewer runs/<x>` (desde Windows basta `PYTHONPATH=src python -m panspermia.viewer ...`: solo usa la biblioteca estándar); la página está en `src/panspermia/viewer_static/index.html` (sin dependencias externas). Probarla con Playwright. En esta máquina el Escudo Web de Avast cortaba las descargas grandes de `127.0.0.1` (siempre a los 19 s); hay una excepción para `http://127.0.0.1:8765/*`. Si se usa otro puerto, puede volver a pasar. En Windows `allow_reuse_address` deja a dos servidores escuchar en el mismo puerto: matar el viejo antes de relanzar.
- Orden de fases (ADR-012): 1b (integrada en main, sustrato 2.0.0; 2 de 5 mundos sobreviven a 500 épocas) → **1d: condiciones del aprendizaje** (barridos de un factor cada vez con la sonda emparejada) → granja «fuga» (ADR-009) → red 4a. Batería v2 integrada en main (ADR-011). La 1d se implementa en la rama `fase1d` (worktree `panspermia-fase1d`): experimentos declarativos en `experiments/fase1d/*.json`, lanzados con `python -m panspermia.experiment sweep <cola> --out runs/fase1d` (con `PYTHONPATH=src` desde el worktree, o se importará el paquete de main) y resumidos con `scripts/analyze_1d.py`.
- Comunicación con el responsable: cada mensaje lleva un bloque «En palabras sencillas» (nivel abuela o niño), sin jerga.

## Convenciones

- Código e identificadores en inglés; documentación y mensajes de commit en español.
- Tipos anotados; `chex`/`jaxtyping` para formas de arrays.
- Cada cambio de formato de genoma incrementa `SUBSTRATE_VERSION` (major si rompe compatibilidad) y añade función `upgrade` si es minor.
- Commits pequeños; un criterio de aceptación por PR cuando sea posible.
