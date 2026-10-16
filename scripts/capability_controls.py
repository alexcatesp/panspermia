"""Controles de la batería de capacidad (ADR-010, ADR-011): ¿qué puntúa una política SIN cerebro?

Ejecuta las políticas fijas de `config.PROBE_CONTROLS` (empuje y giro constantes, comer siempre)
con cuerpos de genomas mínimos aleatorios en la mancha lejana y el laberinto de la batería v2, y en
el anillo de la v1 (que reproduce el falso positivo). Solo observa: no toca ninguna isla.

Uso: python scripts/capability_controls.py
"""
from __future__ import annotations

import math

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import capability, island
from panspermia import config as C
from panspermia import genome as G
from panspermia.develop import develop_batch


def ring_layout_v1() -> tuple[np.ndarray, np.ndarray]:
    """Anillo de la batería v1 (radio 120–136), solo para documentar el falso positivo."""
    x, y = capability._grid()
    r = np.hypot(x - capability.CENTER, y - capability.CENTER)
    food = np.where((r >= 120.0) & (r <= 136.0), C.PROBE_FOOD, 0.0).astype(np.float32)
    return food, np.zeros_like(food, bool)


def main() -> None:
    island.setup_determinism()
    p = C.PROBE_AGENTS
    k_g, k_a = jax.random.split(jax.random.PRNGKey(1234))
    g = jax.vmap(G.random_minimal)(jax.random.split(k_g, p))
    ph = develop_batch(g)
    w = ph.w0.astype(jnp.float32)
    rand_angles = jax.random.uniform(k_a, (p,), maxval=2 * math.pi)
    tests = {
        "anillo v1": (ring_layout_v1(), 500, rand_angles),
        "mancha v2": (capability.patch_layout(), C.PROBE_PATCH_STEPS, rand_angles),
        "laberinto": (capability.maze_layout(), C.PROBE_MAZE_STEPS, jnp.zeros((p,))),
    }
    print("política (empuje, giro) · " + " · ".join(tests))
    rows = {}
    for name, ((food, walls), steps, angles) in tests.items():
        env = capability._probe_env(walls)
        rows[name] = capability.control_successes(env, g, ph, w, angles, jnp.asarray(food), steps)
    for i, (thrust, turn) in enumerate(C.PROBE_CONTROLS):
        print(f"({thrust:.2f}, {turn:+.2f}) · " + " · ".join(f"{rows[n][i]:.3f}" for n in tests))


if __name__ == "__main__":
    main()
