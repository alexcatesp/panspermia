"""Controles de la batería de capacidad (ADR-010): ¿qué puntúa un agente SIN cerebro?

Sustituye `brain.step` por una política fija («avanza con empuje constante y come siempre», sin
giro, sin plasticidad útil) y ejecuta las mismas sondas de anillo y laberinto de `capability.py`
con los cuerpos de genomas mínimos aleatorios. Si una política trivial supera el umbral, la prueba
no mide generalización sino locomoción. Solo observa: no toca ninguna isla.

Uso: python scripts/capability_controls.py
"""
from __future__ import annotations

import math

import jax
import jax.numpy as jnp

from panspermia import brain, capability, island
from panspermia import config as C
from panspermia import genome as G
from panspermia.develop import develop_batch


def fixed_policy(thrust: float, turn: float = 0.0):
    def step(w, h, obs, hid_mask):
        n = obs.shape[0]
        a = jnp.zeros((n, C.ACT_DIM)).at[:, 0].set(thrust).at[:, 1].set(turn).at[:, 2].set(1.0)
        pre = jnp.concatenate([obs, h], axis=-1)
        post = jnp.concatenate([h, a], axis=-1)
        return a, h, pre, post
    return step


def main() -> None:
    island.setup_determinism()
    p = C.PROBE_AGENTS
    key = jax.random.PRNGKey(1234)
    k_g, k_a = jax.random.split(key)
    g = jax.vmap(G.random_minimal)(jax.random.split(k_g, p))
    ph = develop_batch(g)
    w = ph.w0.astype(jnp.float32)
    valid = jnp.ones((p,), bool)
    ring_angles = jax.random.uniform(k_a, (p,), maxval=2 * math.pi)
    original = brain.step
    print(f"umbrales: {C.CAPABILITY_PAUSE_THRESHOLDS}")
    for thrust, turn in [(0.0, 0.0), (0.25, 0.0), (0.5, 0.0), (1.0, 0.0), (1.0, 0.3), (1.0, 1.0)]:
        brain.step = fixed_policy(thrust, turn)
        out = {}
        for name, (layout, steps, angles) in {
            "ring": (capability.ring_layout(), C.PROBE_RING_STEPS, ring_angles),
            "maze": (capability.maze_layout(), C.PROBE_MAZE_STEPS, jnp.zeros((p,))),
        }.items():
            food, walls = layout
            env = capability._probe_env(walls)
            jax.clear_caches()  # la traza de _run_probe queda ligada a la política anterior
            intake = capability._run_probe(env, g, ph, w, valid, angles, jnp.asarray(food), steps)
            out[name] = capability._success(intake, valid)
        print(f"empuje {thrust:.2f} giro {turn:+.2f} → anillo {out['ring']:.3f} · laberinto {out['maze']:.3f}")
    brain.step = original


if __name__ == "__main__":
    main()
