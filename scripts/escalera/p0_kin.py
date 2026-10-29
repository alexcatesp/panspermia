"""D1 (ADR-017): parentesco local a posteriori desde los checkpoints (solo observa)."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
from reward_probe import restore
from panspermia import metrics

R = Path("/mnt/d/Development/panspermia/runs/fase1d")
out = {}
for cond in ("P0-feliz", "P0-feliz-nacer-azar", "P0-feliz-control-kin"):
    for d in sorted((R / cond).glob("s*")):
        for ep in (100, 200, 300):
            spec, st = restore(d, ep)
            a = np.asarray(st.alive)
            kl = float(metrics.kin_local(st)); kg = metrics.simpson(np.asarray(st.lineage.clade), a)
            out[f"{cond}/{d.name}/{ep}"] = {"kin_local": kl, "kin_global": kg, "vivos": int(a.sum())}
            print(cond, d.name, ep, f"{kl:.4f} {kg:.4f}", flush=True)
(R / "_analisis_D1_kin.json").write_text(json.dumps(out, indent=1))
