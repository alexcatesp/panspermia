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

- Python ≥ 3.11, JAX con CUDA 12. En Windows: **WSL2** (JAX con GPU no corre nativo en Windows). GPU de referencia: RTX 5070 12 GB.
- Al arrancar cualquier simulación: `XLA_FLAGS=--xla_gpu_deterministic_ops=true` y `jax.config.update("jax_default_matmul_precision", "highest")`.
- Instalar: `pip install -e ".[dev]"`; tests: `pytest`.

## Estado actual y siguiente trabajo

Fase 0 (núcleo 2D) sin empezar. Los módulos en `src/panspermia/` son esqueletos con firmas; los tests en `tests/` codifican los criterios de aceptación de la fase 0 y están en `skip` hasta implementarse.

Orden sugerido para la fase 0:

1. `genome.py`: estructura, `random_minimal`, `mutate`, forma canónica, hash BLAKE3, serialización msgpack+zstd. Tests de ida y vuelta.
2. `develop.py`: CPPN vectorizada → fenotipo. Test de determinismo.
3. `brain.py`: paso neuronal + regla ABCD modulada.
4. `world.py`: mundo 2D (sin ataque en fase 0), sensores por rayos, recursos.
5. `island.py`: `world_step`, nacimientos/muertes por slots, `epoch` con `lax.scan`.
6. `metrics.py` + checkpoints Orbax + Parquet.
7. Benchmark de pasos-agente/s y documentarlo en `docs/decisiones.md`.

## Convenciones

- Código e identificadores en inglés; documentación y mensajes de commit en español.
- Tipos anotados; `chex`/`jaxtyping` para formas de arrays.
- Cada cambio de formato de genoma incrementa `SUBSTRATE_VERSION` (major si rompe compatibilidad) y añade función `upgrade` si es minor.
- Commits pequeños; un criterio de aceptación por PR cuando sea posible.
