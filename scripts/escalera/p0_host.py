"""Análisis sin GPU de P0 (A4, A5, A7, C4) desde los checkpoints de la época 300."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, "/mnt/d/Development/panspermia-escalera/scripts")
from reward_probe import restore
from panspermia import config as C

cond = sys.argv[1] if len(sys.argv) > 1 else "P0-feliz"
R = Path("/mnt/d/Development/panspermia/runs/fase1d") / cond
out = {}
for d in sorted(R.glob("s*")):
    spec, st = restore(d, 300)
    a = np.asarray(st.alive)
    g = st.genome
    hid = np.asarray(g.hid_mask)[a].sum(1)
    nodes = np.asarray(g.node_mask)[a].sum(1) - (C.CPPN_IN + C.CPPN_OUT)
    cppn_hidden_max = C.CPPN_NODES - C.CPPN_IN - C.CPPN_OUT
    # A7: fracción de perturbaciones de pesos que el redondeo a f16 borra (|N(0,σ)| < media ulp)
    W = np.asarray(g.W)[a].astype(np.float32); Wm = np.asarray(g.W_mask)[a]
    sig = np.asarray(g.life)[a][:, 2].astype(np.float32)
    w = np.abs(W[Wm]); s = np.repeat(sig, Wm.reshape(len(sig), -1).sum(1))
    ulp = np.spacing(w.astype(np.float16)).astype(np.float32)
    from math import erf
    lost = np.mean([erf(u / 2 / (sd * np.sqrt(2))) for u, sd in zip(ulp[:200000], s[:200000])])
    # C4: nacimientos por paso entre los vivos (todos nacieron en las últimas 600 pasos)
    bs = np.asarray(st.lineage.birth_step)[a]
    _, per_step = np.unique(bs, return_counts=True)
    out[d.name] = {
        "A5_neuronas_media": float(hid.mean()), "A5_neuronas_max": int(hid.max()),
        "A5_frac_ge56_de_64": float(np.mean(hid >= 56)),
        "A5_cppn_ocultos_media": float(nodes.mean()), "A5_cppn_ocultos_techo": cppn_hidden_max,
        "A5_frac_cppn_en_techo": float(np.mean(nodes >= cppn_hidden_max)),
        "A7_frac_perturbacion_borrada_f16": float(lost),
        "A3_sigma_mediana": float(np.median(sig)), "A3_tasa_mediana": float(np.median(np.asarray(g.life)[a][:, 3].astype(np.float32))),
        "C4_nacimientos_por_paso_max": int(per_step.max()), "C4_pasos_en_tope_32": int(np.sum(per_step >= C.MAX_BIRTHS_PER_STEP)),
        "C4_pasos_con_nacimientos": int(len(per_step)),
    }
    print(d.name, json.dumps(out[d.name]), flush=True)
Path(f"/mnt/d/Development/panspermia/runs/fase1d/_host_{cond}.json").write_text(json.dumps(out, indent=1))
