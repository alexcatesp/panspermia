"""Controles de la batería de capacidad (ADR-010, ADR-011).

- Negativos: políticas fijas SIN cerebro de `config.PROBE_CONTROLS` (empuje y giro constantes,
  comer siempre) en la mancha lejana y el laberinto de la batería v2, y en el anillo de la v1 (que
  reproduce el falso positivo). Deben puntuar poco.
- Positivo: un «buscador» programado a mano (avanza recto K pasos, luego describe un arco amplio y,
  si ve comida en los rayos, gira hacia ella). Demuestra que la mancha se puede resolver: si ni él
  la encuentra, el umbral sería inalcanzable y la alarma no serviría.

Solo observa: no toca ninguna isla.

Uso: python scripts/capability_controls.py
"""
from __future__ import annotations

import math

import jax
import jax.numpy as jnp
import numpy as np

from panspermia import brain, capability, island, world
from panspermia import config as C
from panspermia import genome as G
from panspermia.develop import develop_batch


def ring_layout_v1() -> tuple[np.ndarray, np.ndarray]:
    """Anillo de la batería v1 (radio 120–136), solo para documentar el falso positivo."""
    x, y = capability._grid()
    r = np.hypot(x - capability.CENTER, y - capability.CENTER)
    food = np.where((r >= 120.0) & (r <= 136.0), C.PROBE_FOOD, 0.0).astype(np.float32)
    return food, np.zeros_like(food, bool)


def searcher(straight_steps: int, arc_turn: float):
    """Política «buscador» para sustituir a brain.step. Usa h[:, 0] como contador de pasos."""
    def step(w, h, obs, hid_mask):
        n = obs.shape[0]
        res = obs[:, :C.N_RAYS * C.RAY_CHANNELS].reshape(n, C.N_RAYS, C.RAY_CHANNELS)[..., 1]
        seen = jnp.max(res, axis=1) > 0
        offset = world._RAY_FRAC[jnp.argmax(res, axis=1)]
        count = h[:, 0]
        search_turn = jnp.where(count < straight_steps, 0.0, arc_turn)
        turn = jnp.where(seen, jnp.clip(4.0 * offset, -1.0, 1.0), search_turn)
        thrust = jnp.where(seen, 0.5, 1.0)
        a = jnp.zeros((n, C.ACT_DIM)).at[:, 0].set(thrust).at[:, 1].set(turn).at[:, 2].set(1.0)
        h_new = h.at[:, 0].add(1.0)
        return a, h_new, jnp.concatenate([obs, h], axis=-1), jnp.concatenate([h_new, a], axis=-1)
    return step


def positive_controls(g, ph, w, angles, steps_list=(C.PROBE_PATCH_STEPS, 3 * C.PROBE_PATCH_STEPS)):
    """Éxito del mejor buscador en la mancha lejana para cada duración."""
    food, walls = capability.patch_layout()
    env = capability._probe_env(walls)
    valid = jnp.ones((angles.shape[0],), bool)
    original, best = brain.step, {}
    try:
        for steps in steps_list:
            for k in (100, 175, 250):
                for arc in (0.05, 0.1, 0.2):
                    brain.step = searcher(k, arc)
                    jax.clear_caches()  # la traza de _run_probe queda ligada a la política anterior
                    s = capability._success(capability._run_probe(
                        env, g, ph, w, valid, angles, jnp.asarray(food), steps), valid)
                    if s > best.get(steps, (0, None))[0]:
                        best[steps] = (s, (k, arc))
    finally:
        brain.step = original
        jax.clear_caches()
    return best


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
    for steps, (s, (k, arc)) in positive_controls(g, ph, w, rand_angles).items():
        print(f"buscador (recto {k} pasos, arco {arc}) · mancha en {steps} pasos · {s:.3f}")


if __name__ == "__main__":
    main()
