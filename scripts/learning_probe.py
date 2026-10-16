"""Sonda del aprendizaje en vida (solo observa): ¿qué cambia la plasticidad, además de sobrevivir?

Restaura un checkpoint y corre una época dos veces desde el mismo estado y con la misma
aleatoriedad (clave por paso = fold_in(key, step)): con plasticidad y con plasticidad congelada.
Compara supervivencia, ingesta, fracción de ingesta tóxica, nacimientos y muertes por causa.

Uso: python scripts/learning_probe.py runs/phase1b/s0 --epoch 100 --seed 0 --node phase1-0
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

import jax
import jax.numpy as jnp
import numpy as np
import orbax.checkpoint as ocp

from panspermia import config as C
from panspermia import island, metrics

KEYS = ["population", "births", "intake", "toxic_intake_frac", "nutrient_intake", "deaths_starvation",
        "deaths_poison", "deaths_attack", "mean_energy", "emit_toxin", "emit_nutrient", "emit_pheromone"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("run", type=Path)
    p.add_argument("--epoch", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--node", required=True)
    p.add_argument("--jsonl", type=Path, help="añade una línea JSON con el resultado")
    a = p.parse_args()
    island.setup_determinism()
    template = island.init_island(a.seed, a.node.encode(), n_max=C.N_MAX, n_init=C.N_INIT)
    with tempfile.TemporaryDirectory() as tmp:  # copia: no tocar la carpeta de una ejecución viva
        shutil.copytree(a.run / "checkpoints" / str(a.epoch), Path(tmp) / str(a.epoch))
        mngr = ocp.CheckpointManager(Path(tmp))
        abstract = jax.tree.map(ocp.utils.to_shape_dtype_struct, template)
        state = mngr.restore(a.epoch, args=ocp.args.StandardRestore(abstract))
    uid0, alive0 = jax.device_get((state.lineage.uid, state.alive))
    out = {}
    for plastic in (True, False):
        copy = jax.tree.map(jnp.copy, state)  # epoch dona su entrada
        s, st = island.epoch(copy, C.EPOCH_STEPS, plastic=plastic)
        uid, alive = jax.device_get((s.lineage.uid, s.alive))
        row = {k: float(st[k]) for k in KEYS if k in st}
        row["survival"] = metrics.learning_survival(uid0, alive0, uid, alive)
        out["plástica" if plastic else "congelada"] = row
    if a.jsonl:
        with a.jsonl.open("a") as f:
            f.write(json.dumps({"run": str(a.run), "epoch": a.epoch, **out}) + "\n")
    print(f"{a.run} · época {a.epoch} · vivos al inicio {int(np.asarray(alive0).sum())}")
    print(f"  {'métrica':20s} {'plástica':>12s} {'congelada':>12s} {'diferencia':>12s}")
    for k in ["survival"] + KEYS:
        if k in out["plástica"]:
            x, y = out["plástica"][k], out["congelada"][k]
            print(f"  {k:20s} {x:12.4f} {y:12.4f} {x - y:+12.4f}")


if __name__ == "__main__":
    main()
