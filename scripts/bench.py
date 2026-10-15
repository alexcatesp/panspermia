"""Benchmark de pasos-agente/s de la fase 0 (spec §Motor de isla).

Uso (WSL, venv activo): python scripts/bench.py [--epochs 3]
Mide épocas completas de EPOCH_STEPS pasos tras una época de calentamiento (compilación).
Informa de dos cifras: pasos-slot/s (N_max × pasos: el coste real, porque el cómputo es denso
sobre todos los slots) y pasos-agente/s de agentes vivos.
"""
from __future__ import annotations

import argparse
import time

from panspermia.island import setup_determinism

setup_determinism()

import jax
import numpy as np

from panspermia import config as C
from panspermia import island


def bench(n_max: int, n_init: int, epochs: int) -> dict:
    s = island.init_island(0, b"bench", n_max=n_max, n_init=n_init)
    s, _ = island.epoch(s, C.EPOCH_STEPS)  # calentamiento
    jax.block_until_ready(s.w)
    times, alive = [], []
    for _ in range(epochs):
        t0 = time.perf_counter()
        s, st = island.epoch(s, C.EPOCH_STEPS)
        jax.block_until_ready(s.w)
        times.append(time.perf_counter() - t0)
        alive.append(float(np.mean([int(st["population"]), int(st["population_min"])])))
    t = float(np.median(times))
    return {"n_max": n_max, "epoch_s": t, "slot_steps_per_s": n_max * C.EPOCH_STEPS / t,
            "alive_mean": float(np.mean(alive)),
            "alive_steps_per_s": float(np.mean(alive)) * C.EPOCH_STEPS / t}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--epochs", type=int, default=3)
    a = p.parse_args()
    print(f"jax {jax.__version__} · {jax.devices()[0].device_kind}")
    for n_max in (1024, 2048, C.N_MAX):
        r = bench(n_max, min(C.N_INIT, n_max // 2), a.epochs)
        print(f"N_max={r['n_max']:5d} · época {r['epoch_s']:.2f} s · "
              f"{r['slot_steps_per_s']:.3g} pasos-slot/s · vivos≈{r['alive_mean']:.0f} · "
              f"{r['alive_steps_per_s']:.3g} pasos-agente(vivo)/s", flush=True)


if __name__ == "__main__":
    main()
