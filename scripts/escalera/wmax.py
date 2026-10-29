"""Saturación de pesos (panel 10, ADR-035; solo observa): en los vivos del checkpoint, fracción de sinapsis plásticas
(mask y η·g ≠ 0) con |w| en W_MAX, |w| medio y |w − w0| medio. Regla: > 50 % (mediana de mundos) = no interpretable.
Uso: python wmax.py <run> --seeds 0 1 2 --epoch 300 --config K=V ... --jsonl salida.jsonl"""
import argparse, json
from pathlib import Path
import numpy as np
from panspermia import config as C, island
import madura_alga as M

if __name__ == "__main__":
    pa = argparse.ArgumentParser()
    pa.add_argument("run", type=Path)
    pa.add_argument("--seeds", type=int, nargs="+", default=list(range(10)))
    pa.add_argument("--epoch", type=int, default=300)
    pa.add_argument("--config", nargs="*", default=[])
    pa.add_argument("--jsonl", type=Path, required=True)
    a = pa.parse_args()
    island.setup_determinism()
    for kv in a.config:
        k, v = kv.split("=")
        cur = getattr(C, k)
        setattr(C, k, float(v) if cur is None else type(cur)(float(v)))
    for seed in a.seeds:
        s = M.load(a.run, seed, a.epoch)
        alive = np.asarray(s.alive)
        ph = s.pheno
        w = np.asarray(s.w)[alive]
        w0 = np.asarray(ph.w0, np.float32)[alive]
        plastic = (np.asarray(ph.mask)[alive] & (np.asarray(ph.eta, np.float32)[alive] * np.asarray(ph.g, np.float32)[alive] != 0))
        sat = np.abs(w) >= C.W_MAX - 1e-3
        row = {"run": a.run.name, "seed": seed, "epoch": a.epoch, "vivos": int(alive.sum()),
               "frac_wmax": round(float(sat[plastic].mean()) if plastic.any() else 0.0, 4),
               "frac_wmax_bicho_mediana": round(float(np.median([sat[i][plastic[i]].mean() if plastic[i].any() else 0.0
                                                                 for i in range(len(w))])), 4),
               "abs_w": round(float(np.abs(w[plastic]).mean()) if plastic.any() else 0.0, 4),
               "abs_w_menos_w0": round(float(np.abs(w - w0)[plastic].mean()) if plastic.any() else 0.0, 4),
               "sinapsis_plasticas_por_bicho": round(float(plastic.sum(axis=(1, 2)).mean()), 1)}
        print(json.dumps(row), flush=True)
        with a.jsonl.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
