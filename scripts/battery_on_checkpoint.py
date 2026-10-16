"""Pasa la batería de capacidad vigente por un checkpoint guardado (solo observa).

Sirve para revisar una pausa o para calibrar una versión nueva de la batería sobre poblaciones
reales sin reanudar la isla. La información mutua de comunicación se toma de `stats/summary.json`.

Uso: python scripts/battery_on_checkpoint.py runs/phase1/s1 --epoch 100 --seed 1 --node phase1-1
"""
from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

import jax
import orbax.checkpoint as ocp

from panspermia import capability, island
from panspermia import config as C


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
    rows = json.loads((a.run / "stats" / "summary.json").read_text())
    mi = next((r["comm_mi_bits"] for r in rows if r["epoch"] == a.epoch), 0.0)
    out = capability.run_battery(state, mi)
    hit = capability.exceeded(out, C.CAPABILITY_PAUSE_THRESHOLDS)
    print(f"{a.run} · época {a.epoch} · umbrales {C.CAPABILITY_PAUSE_THRESHOLDS}")
    for k, v in out.items():
        print(f"  {k:26s} {v:.4f}")
    print(f"  PAUSARÍA: {hit}" if hit else "  no pausaría")
    if a.jsonl:
        with a.jsonl.open("a") as f:
            f.write(json.dumps({"run": str(a.run), "epoch": a.epoch, **out, "exceeded": hit}) + "\n")


if __name__ == "__main__":
    main()
