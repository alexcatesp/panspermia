"""B1: ¿el cruce por índice deja nodos de la CPPN desconectados? (época 300)"""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
from reward_probe import restore
from panspermia import config as C
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
hid = np.zeros(C.CPPN_NODES, bool); hid[C.CPPN_IN:C.CPPN_NODES - C.CPPN_OUT] = True
out = {}
for cond in ("P0-feliz", "P0-feliz-sexual"):
    for s in (0, 1, 2, 3, 4):
        _, st = restore(R / cond / f"s{s}", 300)
        a = np.asarray(st.alive); nm = np.asarray(st.genome.node_mask)[a]; Wm = np.asarray(st.genome.W_mask)[a]
        hn = nm & hid
        no_in = hn & ~Wm.any(axis=1)   # sin aristas de entrada
        no_out = hn & ~Wm.any(axis=2)                                                                       # sin aristas de salida
        n = hn.sum(1)
        out[f"{cond}/s{s}"] = {"nodos": float(n.mean()), "frac_sin_entrada": float(no_in.sum() / max(hn.sum(), 1)),
                               "frac_sin_salida": float(no_out.sum() / max(hn.sum(), 1)),
                               "aristas_entrada_salida": float(Wm[:, :C.CPPN_IN, C.CPPN_NODES - C.CPPN_OUT:].sum((1, 2)).mean())}
        print(cond, s, json.dumps(out[f"{cond}/s{s}"]), flush=True)
(R / "_b1_cppn.json").write_text(json.dumps(out, indent=1))
