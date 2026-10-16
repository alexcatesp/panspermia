"""Benchmark: B islas a la vez en la GPU (vmap) frente a una sola. ¿Coinciden bit a bit?

Uso: python scripts/bench_multi.py
"""
from __future__ import annotations

import functools
import time

import jax
import numpy as np

from panspermia import island


def _scan(state, k):
    step = functools.partial(island.world_step)
    return jax.lax.scan(step, state, None, length=k)[0]


def main() -> None:
    island.setup_determinism()
    k = 200
    single = jax.jit(_scan, static_argnums=1)
    batched = jax.jit(jax.vmap(_scan, in_axes=(0, None)), static_argnums=1)
    for b in (1, 2, 4, 8):
        states = [island.init_island(s, f"bench-{s}".encode()) for s in range(b)]
        # calentar con una época para tener poblaciones realistas
        states = [single(s, 1000) for s in states]
        jax.block_until_ready(states)
        stacked = jax.tree.map(lambda *x: jax.numpy.stack(x), *states)
        out_b = batched(stacked, k); jax.block_until_ready(out_b)  # compilar
        t = time.perf_counter(); out_b = batched(stacked, k); jax.block_until_ready(out_b)
        tb = time.perf_counter() - t
        t = time.perf_counter()
        outs = [single(s, k) for s in states]; jax.block_until_ready(outs)
        ts = time.perf_counter() - t
        same = all(np.array_equal(np.asarray(jax.tree.leaves(o)[i]), np.asarray(jax.tree.leaves(out_b)[i][j]))
                   for j, o in enumerate(outs) for i in range(len(jax.tree.leaves(o))))
        alive = sum(int(np.asarray(s.alive).sum()) for s in states)
        print(f"B={b} · vivos {alive} · secuencial {ts:.2f}s · vmap {tb:.2f}s · aceleración {ts / tb:.2f}× · "
              f"bit a bit {'sí' if same else 'NO'}", flush=True)


if __name__ == "__main__":
    main()
