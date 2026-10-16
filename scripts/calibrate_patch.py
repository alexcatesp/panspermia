"""Calibración de la mancha lejana (ADR-011): controles negativos frente al buscador positivo.

Para cada (distancia, pasos) mide el mejor control sin cerebro (debe quedar < 0,1) y el mejor
buscador programado (debe superar holgadamente 0,5 + referencia). Solo observa.

Con --run se usan cuerpos evolucionados (64 adultos de un checkpoint) en lugar de aleatorios.

Uso: python scripts/calibrate_patch.py [--run runs/phase1/s0 --epoch 500 --seed 0 --node phase1-0]
"""
from __future__ import annotations

import argparse
import itertools
import math
import shutil
import tempfile
from pathlib import Path

import jax
import jax.numpy as jnp
import orbax.checkpoint as ocp
from capability_controls import searcher

from panspermia import brain, capability, island
from panspermia import config as C
from panspermia import genome as G
from panspermia.develop import develop_batch


def main() -> None:
    island.setup_determinism()
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", type=Path)
    ap.add_argument("--epoch", type=int)
    ap.add_argument("--seed", type=int)
    ap.add_argument("--node")
    a = ap.parse_args()
    p = C.PROBE_AGENTS
    k_g, k_a = jax.random.split(jax.random.PRNGKey(1234))
    angles = jax.random.uniform(k_a, (p,), maxval=2 * math.pi)
    if a.run:
        template = island.init_island(a.seed, a.node.encode())
        with tempfile.TemporaryDirectory() as tmp:
            shutil.copytree(a.run / "checkpoints" / str(a.epoch), Path(tmp) / str(a.epoch))
            abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, template)
            state = ocp.CheckpointManager(Path(tmp)).restore(a.epoch, args=ocp.args.StandardRestore(abstract))
        g, ph, w, valid = capability.sample_adults(state, k_g)
        print(f"cuerpos evolucionados de {a.run} (época {a.epoch}) · alcance medio "
              f"{float(jnp.mean(ph.sensor_range)):.1f}", flush=True)
    else:
        g = jax.vmap(G.random_minimal)(jax.random.split(k_g, p))
        ph = develop_batch(g)
        w = ph.w0.astype(jnp.float32)
        valid = jnp.ones((p,), bool)
        print(f"cuerpos aleatorios · alcance medio {float(jnp.mean(ph.sensor_range)):.1f}", flush=True)
    for dist, steps in itertools.product((90.0, 120.0), (500, 1000)):
        C.PROBE_PATCH_DIST = dist
        food, walls = capability.patch_layout()
        env = capability._probe_env(walls)
        res = jnp.asarray(food)
        neg = max(capability.control_successes(env, g, ph, w, angles, res, steps, valid))
        original, pos, best = brain.step, 0.0, None
        try:
            for k, arc in itertools.product((int(dist / 2), int(dist)), (0.02, 0.05, 0.1)):
                brain.step = searcher(k, arc)
                jax.clear_caches()
                s = capability._success(capability._run_probe(env, g, ph, w, valid, angles, res, steps), valid)
                if s > pos:
                    pos, best = s, (k, arc)
        finally:
            brain.step = original
            jax.clear_caches()
        print(f"distancia {dist:.0f} · pasos {steps} · mejor control sin cerebro {neg:.3f} · "
              f"mejor buscador {pos:.3f} {best}", flush=True)


if __name__ == "__main__":
    main()
