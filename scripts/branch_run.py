"""Ramifica un mundo desde un checkpoint con otro azar (pruebas de la masa, decisión del responsable, 22-10).

Copia el checkpoint de la época E de <origen> a <destino>, cambia la clave del mundo por
fold_in(clave, salt) y copia las estadísticas y archivos de métricas hasta E. Después, el runner
(o el barrido) reanuda <destino> desde E con la misma configuración. Todo lo anterior a E es idéntico al origen.

Uso: python scripts/branch_run.py runs/fase1d/P4-salto64-e50/s1 --epoch 50 --salt 1 --out runs/fase1d/P4-salto64-rama1/s1
"""
import argparse, json, shutil
from pathlib import Path

import jax
import orbax.checkpoint as ocp

from panspermia import config as C, island, run

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("src", type=Path)
    p.add_argument("--epoch", type=int, required=True)
    p.add_argument("--salt", type=int, required=True)
    p.add_argument("--out", type=Path, required=True)
    p.add_argument("--node", default="fase1d-w0")
    a = p.parse_args()
    island.setup_determinism()
    seed = int(a.src.name.lstrip("s"))
    if (a.out / "checkpoints").exists():
        raise SystemExit(f"{a.out} ya tiene checkpoints: no se sobrescribe")
    template = island.init_island(seed, a.node.encode(), n_max=C.N_MAX, n_init=C.N_INIT)
    src = run._checkpoint_manager(a.src / "checkpoints")
    state = src.restore(a.epoch, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))
    src.close()
    state = state.replace(key=jax.random.fold_in(state.key, a.salt))
    (a.out / "stats").mkdir(parents=True, exist_ok=True)
    dst = run._checkpoint_manager(a.out / "checkpoints")
    dst.save(a.epoch, args=ocp.args.StandardSave(jax.device_get(state)), force=True)
    dst.wait_until_finished(); dst.close()
    rows = [r for r in json.loads((a.src / "stats" / "summary.json").read_text()) if r["epoch"] <= a.epoch]
    (a.out / "stats" / "summary.json").write_text(json.dumps(rows))
    for f in (a.src / "stats").glob("part_*.parquet"):
        if int(f.stem.split("_")[1]) <= a.epoch:
            shutil.copy(f, a.out / "stats" / f.name)
    for name in ("novelty_archive.npy", "activity.json"):
        if (a.src / name).exists():
            shutil.copy(a.src / name, a.out / name)
    (a.out / "branch.json").write_text(json.dumps({"src": str(a.src), "epoch": a.epoch, "salt": a.salt}))
    print(f"rama {a.out} desde {a.src} época {a.epoch}, salt {a.salt}")
