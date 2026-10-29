"""Distribución de nodos ocultos y aristas de la CPPN en la época 300 (A2, A5)."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
from reward_probe import restore
from panspermia import config as C
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
out = {}
for cond in ("P1-peaje", "P1-peaje-cppn-neutral"):
    for d in sorted((R / cond).glob("s*")):
        _, st = restore(d, 300)
        a = np.asarray(st.alive); g = st.genome
        nodes = np.asarray(g.node_mask)[a].sum(1) - (C.CPPN_IN + C.CPPN_OUT)
        edges = np.asarray(g.W_mask)[a].reshape(a.sum(), -1).sum(1)
        out[f"{cond}/{d.name}"] = {"nodos_media": float(nodes.mean()), "nodos_p5_50_95": np.percentile(nodes, [5, 50, 95]).tolist(),
                                    "aristas_media": float(edges.mean()), "aristas_p5_50_95": np.percentile(edges, [5, 50, 95]).tolist(),
                                    "aristas_min": int(edges.min()), "frac_aristas_le10": float(np.mean(edges <= 10))}
        print(cond, d.name, json.dumps(out[f"{cond}/{d.name}"]), flush=True)
(R / "_dist_cppn_P1.json").write_text(json.dumps(out, indent=1))
