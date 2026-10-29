"""Comer frena con rampa (diseño v1.9): ventaja A de la sonda mixta, pares con el padre y secundarias."""
import json, sys
from math import comb
from pathlib import Path

R = Path(sys.argv[1] if len(sys.argv) > 1 else "/mnt/d/Development/panspermia/runs/fase1d")
rows = [json.loads(l) for l in (R / "_sonda_frena.jsonl").open(encoding="utf-8")]
by = {}
for r in rows:
    by[(r["run"], r["seed"])] = r  # la última fila de cada mundo


def A(r):
    return r["plastico"]["ingesta_por_paso"] / r["congelado"]["ingesta_por_paso"] - 1


def A_age(r, lo, hi):
    def g(grp):
        p = r[grp]
        n = p["pasos_por_edad"][lo:hi]
        it = p["por_edad"]["intake"][lo:hi]
        tot = sum(n)
        return sum(i * k for i, k in zip(it, n)) / tot if tot else float("nan")
    f = g("congelado")
    return g("plastico") / f - 1 if f else float("nan")


def births(r):
    return r["plastico"]["hijos_por_paso"] / r["congelado"]["hijos_por_paso"] - 1


EXT = {("P4-alga-tripa-frena-rampa", 4)}  # extinguido en la época 121: desfavorable por el criterio
runs = ["P4-alga-tripa-frena-rampa", "P4-alga-tripa", "P4-alga-sin-tripa-frena-rampa", "P3-escaso-tripa-frena-rampa"]
out = {}
for run in runs:
    out[run] = {}
    for s in range(10):
        r = by.get((run, s))
        if r is None:
            continue
        pw = r["pesos"].get("plastico", {})
        out[run][s] = {"A": A(r), "A_joven": A_age(r, 0, 1), "A_50": A_age(r, 3, 8), "hijos": births(r),
                       "cambia": pw.get("frac_cambia"),
                       "pcc": [r["plastico"]["p_comer_comida"], r["congelado"]["p_comer_comida"]],
                       "pcs": [r["plastico"]["p_comer_sin"], r["congelado"]["p_comer_sin"]]}

med = lambda xs: sorted(xs)[len(xs) // 2] if len(xs) % 2 else sum(sorted(xs)[len(xs) // 2 - 1:len(xs) // 2 + 1]) / 2
for run in runs:
    print(f"== {run}")
    for s, v in out[run].items():
        print(f"  s{s}: A {v['A']*100:+6.1f} %  joven {v['A_joven']*100:+6.1f}  ≥50 {v['A_50']*100:+6.1f}  hijos {v['hijos']*100:+6.1f}"
              f"  cambia {v['cambia'] if v['cambia'] is None else round(v['cambia'], 2)}")
    xs = [v["A"] for v in out[run].values()]
    if xs:
        print(f"  mediana A {med(xs)*100:+.1f} %; A > 5 %: {sum(x > 0.05 for x in xs)}/{len(xs)}")

fav = []
F, P = out["P4-alga-tripa-frena-rampa"], out["P4-alga-tripa"]
for s in range(10):
    if s in F and s in P:
        ok = (("P4-alga-tripa-frena-rampa", s) not in EXT) and F[s]["A"] > 0.05 and F[s]["A"] > P[s]["A"]
        fav.append(ok)
        print(f"par s{s}: freno {F[s]['A']*100:+6.1f}  padre {P[s]['A']*100:+6.1f}  {'favorable' if ok else 'desfavorable'}")
k = sum(fav)
p = sum(comb(10, i) for i in range(k, 11)) / 2 ** 10
print(f"pares favorables {k}/{len(fav)} (p unilateral = {p:.3f}); pasa con ≥ 9: {'sí' if k >= 9 else 'no'}")
json.dump(out, (R / "_analisis_frena.json").open("w", encoding="utf-8"), indent=1, ensure_ascii=False)
