"""¿De dónde sale la ventaja con freno? Por grupo: tiempo sobre comida, P(comer), velocidad, giro."""
import json
from pathlib import Path

R = Path("/mnt/d/Development/panspermia/runs/fase1d")
rows = {}
for l in (R / "_sonda_frena.jsonl").open(encoding="utf-8"):
    r = json.loads(l)
    rows[(r["run"], r["seed"])] = r
for (run, s), r in sorted(rows.items()):
    p, f = r["plastico"], r["congelado"]
    A = p["ingesta_por_paso"] / f["ingesta_por_paso"] - 1
    if abs(A) < 0.05:
        continue
    print(f"{run[:22]:22s} s{s} A {A*100:+5.0f}% | sobre comida {p['frac_sobre_comida']:.2f}/{f['frac_sobre_comida']:.2f}"
          f" | comer|comida {p['p_comer_comida']:.2f}/{f['p_comer_comida']:.2f} | comer|nada {p['p_comer_sin']:.2f}/{f['p_comer_sin']:.2f}"
          f" | vel {p['velocidad']:.2f}/{f['velocidad']:.2f} | giro {p['giro']:.3f}/{f['giro']:.3f}")
    # el bloque de pesos que más cambia en los que aprenden
    b = r["pesos"].get("plastico", {}).get("bloques", {})
    top = sorted(b.items(), key=lambda kv: -kv[1][0])[:3]
    print("    " + "; ".join(f"{k} Δ{v[0]:.2f} (w0 {v[1]:.2f})" for k, v in top))
