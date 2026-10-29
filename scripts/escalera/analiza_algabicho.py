"""Alga por bicho (diseño v2.0–v2.2): primaria, comprobación de la manipulación y secundarias. Solo lee jsonl."""
import json
import statistics as st
from math import comb
from pathlib import Path

R = Path("/mnt/d/Development/panspermia/runs/fase1d")
RUN = "P4-alga-bicho-frena-rampa"


def rows(name):
    p = R / name
    return [json.loads(l) for l in p.open(encoding="utf-8")] if p.exists() else []


def sign_p(k, n):  # una cola, H0: p = 1/2
    return sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n


out = {"run": RUN, "mundos": []}
fav = 0
son = {r["seed"]: r for r in rows("_sonda_algabicho.jsonl") if r["run"] == RUN}
for s in sorted(son):
    r = son[s]
    p, f = r["plastico"], r["congelado"]
    dd = p["D"] - f["D"]
    A = p["ingesta_por_paso"] / f["ingesta_por_paso"] - 1
    sb = lambda g: g["pasos_buena"] / max(g["pasos_buena"] + g["pasos_vacia"], 1)
    ok = dd >= 0.10
    fav += ok
    m = {"seed": s, "D_plastico": p["D"], "D_congelado": f["D"], "dD": dd, "favorable": ok, "A": A,
         "p_buena": [p["p_comer_buena"], f["p_comer_buena"]], "p_vacia": [p["p_comer_vacia"], f["p_comer_vacia"]],
         "frac_buena": [sb(p), sb(f)], "manip_ok": abs(f["D"]) < 0.05}
    out["mundos"].append(m)
    print(f"s{s}: D {p['D']:+.3f} / {f['D']:+.3f}  ΔD {dd:+.3f} {'✓' if ok else '✗'}  A {A*100:+6.1f} %"
          f"  come buena {p['p_comer_buena']:.2f}/{f['p_comer_buena']:.2f}  vacía {p['p_comer_vacia']:.2f}/{f['p_comer_vacia']:.2f}"
          f"  sobre su buena {sb(p):.2f}/{sb(f):.2f}  manip {'ok' if m['manip_ok'] else 'NO'}")
n = len(son)
if n:
    out.update(favorables=fav, n=n, p=sign_p(fav, n), pasa=fav >= 9,
               mediana_dD=st.median(m["dD"] for m in out["mundos"]), mediana_A=st.median(m["A"] for m in out["mundos"]),
               manip=sum(m["manip_ok"] for m in out["mundos"]))
    print(f"Primaria: {fav}/{n} favorables (p = {out['p']:.3f}) → {'PASA' if out['pasa'] else 'NO PASA'};"
          f" mediana ΔD {out['mediana_dD']:+.3f}; mediana A {out['mediana_A']*100:+.1f} %; manipulación ok {out['manip']}/{n}")
nul = [r for r in rows("_sonda_algabicho_nulo.jsonl") if r["run"] == RUN]
out["nulo"] = [{"seed": r["seed"], "A": r["plastico"]["ingesta_por_paso"] / r["congelado"]["ingesta_por_paso"] - 1,
                "dD": r["plastico"]["D"] - r["congelado"]["D"]} for r in nul]
for x in out["nulo"]:
    print(f"nulo s{x['seed']}: A {x['A']*100:+.1f} %  ΔD {x['dD']:+.3f}")
Ms = []
for r in rows("_madura_algabicho.jsonl"):
    g = {k: r[k]["ingesta"] for k in "NEDA"}
    rel = (g["E"] - g["N"]) / g["N"] if g["N"] else float("inf")
    if rel > 0.10:
        Ms.append(r["M"])
    print(f"madura s{r['seed']}: N {g['N']:.4f} E {g['E']:.4f} D {g['D']:.4f}  E/N−1 {rel*100:+.0f} %  M {r['M']:.2f}{'' if rel > 0.10 else ' (sin ganancia)'}")
if Ms:
    out["M"] = {"n": len(Ms), "mediana": st.median(Ms), "min": min(Ms), "max": max(Ms), "ge07": sum(m >= 0.7 for m in Ms)}
    print(f"M en {len(Ms)} mundos con ganancia: mediana {out['M']['mediana']:.2f}; M ≥ 0,7 en {out['M']['ge07']}")
(R / "_analisis_algabicho.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
