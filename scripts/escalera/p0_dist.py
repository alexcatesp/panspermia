"""Distribución del número de neuronas en la época 300 (A1, A6)."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
from reward_probe import restore
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
out = {}
for cond in ("P0-feliz", "P0-feliz-neutral", "P0-feliz-terrestre"):
    for d in sorted((R / cond).glob("s*")):
        _, st = restore(d, 300)
        a = np.asarray(st.alive)
        hid = np.asarray(st.genome.hid_mask)[a].sum(1)
        q = np.percentile(hid, [5, 25, 50, 75, 95]).tolist()
        out[f"{cond}/{d.name}"] = {"media": float(hid.mean()), "sd": float(hid.std()), "frac_0": float(np.mean(hid == 0)),
                                    "frac_le2": float(np.mean(hid <= 2)), "p5_25_50_75_95": q, "max": int(hid.max())}
        print(cond, d.name, json.dumps(out[f"{cond}/{d.name}"]), flush=True)
(R / "_dist_neuronas.json").write_text(json.dumps(out, indent=1))
