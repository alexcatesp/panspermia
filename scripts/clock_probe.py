"""Sonda del reloj (solo observa; diseño 1d v0.9): ¿usan los agentes la información del reloj?

Restaura un checkpoint y corre una época dos veces desde el mismo estado y con la misma
aleatoriedad: con el reloj normal y con el reloj **desincronizado** (`clock_period` × φ). Desincronizado,
el reloj oscila con la misma estadística, pero su fase deja de coincidir con la del mundo: lo que se
pierde es solo la información. En el programa aleatorio el reloj no lleva información del veneno, así
que hace de control.

Efecto: CU = log((población_normal + 1) / (población_desincronizada + 1)), y también log de la ingesta y
diferencia de fracción tóxica (normal − desincronizada). H2 predice CU mayor en el periódico.

Uso: python scripts/clock_probe.py runs/fase1d/E1-periodico-T560/s0 --epoch 300
     [--jsonl runs/fase1d/clock_probe.jsonl]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from reward_probe import restore

from panspermia import config as C
from panspermia import island

PHI = (1 + math.sqrt(5)) / 2  # periodo incommensurable con el del mundo


def run_epoch(state, clock_period: float) -> dict:
    s = jax.tree.map(jnp.copy, state)  # epoch dona su entrada
    s = s.replace(env=s.env.replace(clock_period=jnp.float32(clock_period)))
    s, st = island.epoch(s, C.EPOCH_STEPS, plastic=True)
    return {k: float(st[k]) for k in ("population", "intake", "toxic_intake_frac", "births")}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--epoch", type=int, required=True)
    p.add_argument("--jsonl", type=Path, help="añade una línea JSON con el resultado")
    a = p.parse_args()
    island.setup_determinism()
    _, state = restore(a.run, a.epoch)
    period = float(np.asarray(state.env.clock_period))
    t0 = time.time()
    normal = run_epoch(state, period)
    desync = run_epoch(state, period * PHI)
    res = {
        "run": str(a.run), "epoch": a.epoch, "clock_period": period, "normal": normal, "desync": desync,
        "cu_log_population": math.log((normal["population"] + 1) / (desync["population"] + 1)),
        "cu_log_intake": math.log((normal["intake"] + 1) / (desync["intake"] + 1)),
        "cu_toxic_frac": normal["toxic_intake_frac"] - desync["toxic_intake_frac"],
        "population_start": int(np.asarray(jax.device_get(state.alive)).sum()),
        "seconds": round(time.time() - t0, 1), "backend": jax.default_backend(),
    }
    if a.jsonl:
        with a.jsonl.open("a") as f:
            f.write(json.dumps(res) + "\n")
    print(json.dumps(res, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
