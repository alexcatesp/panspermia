import json
from pathlib import Path
R = Path("/mnt/d/Development/panspermia/runs/fase1d")
rows = {}
for l in (R / "_madura.jsonl").open(encoding="utf-8"):
    r = json.loads(l)
    rows[(r["run"], r["seed"])] = r
for run in ("P4-alga-tripa-frena-rampa", "P3-escaso-tripa-frena-rampa", "P4-alga-tripa", "P4-alga-sin-tripa-frena-rampa"):
    Ms = []
    print("==", run)
    for s in range(10):
        r = rows.get((run, s))
        if not r:
            continue
        g = {k: r[k]["ingesta"] for k in "NEDA"}
        rel = (g["E"] - g["N"]) / g["N"] if g["N"] else float("inf")
        ok = rel > 0.10  # solo se interpreta M si criar con comida mejora al recién nacido más de un 10 %
        if ok:
            Ms.append(r["M"])
        print(f"  s{s}: N {g['N']:.4f} E {g['E']:.4f} D {g['D']:.4f} A {g['A']:.4f}  E/N−1 {rel*100:+6.0f} %  M {r['M']:.2f}{'' if ok else ' (sin ganancia)'}"
              f"  vel N {r['N']['velocidad']:.1f} E {r['E']['velocidad']:.1f} D {r['D']['velocidad']:.1f}"
              f"  come N {r['N']['come']:.2f} E {r['E']['come']:.2f} D {r['D']['come']:.2f}")
    if Ms:
        Ms.sort()
        print(f"  M en {len(Ms)} mundos con ganancia: {Ms[0]:.2f}–{Ms[-1]:.2f}, mediana {Ms[len(Ms)//2] if len(Ms)%2 else (Ms[len(Ms)//2-1]+Ms[len(Ms)//2])/2:.2f}")
