"""Batería en checkpoints con la química del examen encendida (como hoy) o apagada. Solo observa."""
import json, shutil, sys, tempfile
from pathlib import Path
import jax, jax.numpy as jnp
import orbax.checkpoint as ocp
from panspermia import capability, island
from panspermia import config as C

island.setup_determinism()
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
orig = capability._probe_env
out = R / "_bateria_quimica.jsonl"
for cond, seeds, epochs in [("P1-escalera", range(5), (300,)), ("P0-escalera", range(5), (300,)),
                            ("P2-escalera-600", range(5), (100, 300, 600)), ("P2-escalera-sexual-600", range(5), (600,))]:
    for s in seeds:
        for ep in epochs:
            d = R / cond / f"s{s}"
            if not (d / "checkpoints" / str(ep)).exists():
                print("falta", cond, s, ep); continue
            template = island.init_island(s, b"fase1d-w0", n_max=C.N_MAX, n_init=C.N_INIT)
            with tempfile.TemporaryDirectory() as tmp:
                shutil.copytree(d / "checkpoints" / str(ep), Path(tmp) / str(ep))
                mngr = ocp.CheckpointManager(Path(tmp))
                st = mngr.restore(ep, args=ocp.args.StandardRestore(jax.tree.map(ocp.utils.to_shape_dtype_struct, template)))
            row = {"cond": cond, "seed": s, "epoch": ep}
            for chem in (1.0, 0.0):
                capability._probe_env = lambda walls, c=chem: orig(walls).replace(chem_on=jnp.float32(c))
                b = capability.run_battery(st, 0.0)
                for k in ("patch_success", "patch_baseline_random", "patch_baseline_controls", "patch_gain",
                          "maze_success", "maze_baseline_random", "maze_baseline_controls", "maze_gain"):
                    row[f"{k}@chem{int(chem)}"] = round(b[k], 3)
            capability._probe_env = orig
            print(json.dumps(row), flush=True)
            with out.open("a") as f: f.write(json.dumps(row) + "\n")
