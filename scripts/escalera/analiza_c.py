"""Análisis de C (ADR-033, diseno.md v2.5), adaptado del de P5-d (ADR-030, diseno.md v2.4): primaria, regla del indicio, secundarias y H-control. Solo lee jsonl."""
import json, statistics as st, sys
R = sys.argv[1]
out = {}
def rows(p):
    try:
        return [json.loads(l) for l in open(p, encoding="utf-8") if l.strip()]
    except FileNotFoundError:
        return []
SRC = {"C": "c_C", "Cbar": "c_Cbar", "padre": "veneno_inmediato"}
for n in ("C", "Cbar", "padre"):
    pr = sorted(rows(f"{R}/_madura_alga_{SRC[n]}.jsonl"), key=lambda r: r["seed"])
    ex = lambda r, m, a, b: r[a][m] - r[b][m]
    fb = [ex(r, "frac_buena", "E", "X") for r in pr]
    se = [ex(r, "sel_entrada", "E", "X") for r in pr]
    noise = [abs(ex(r, "frac_buena", "E", "E2")) for r in pr]
    o = {"n": len(pr), "fb": fb,
         "frac_buena_EX": [round(v, 3) for v in fb], "pasa_005": sum(v >= 0.05 for v in fb),
         "positivos": sum(v > 0 for v in fb), "mediana": round(st.median(fb), 4) if fb else None,
         "ruido_mediano": round(st.median(noise), 4) if noise else None,
         "sel_entrada_EX": [round(v, 3) for v in se],
         "A_menos_E": [round(ex(r, "frac_buena", "A", "E"), 3) for r in pr],
         "D_comer_EX": [round(ex(r, "D_comer", "E", "X"), 3) for r in pr],
         "primer_contacto_EX": [round(ex(r, "primer_contacto_buena", "E", "X"), 3) for r in pr],
         "ingesta_EX": [round(ex(r, "ingesta", "E", "X"), 4) for r in pr],
         "M": [round(r["M"], 2) for r in pr],
         "vivos_crianza": {k: [round(r["vivos_crianza"][k], 3) for r in pr] for k in ("E", "D", "X")},
         "frac_buena_medias": {k: round(st.mean(r[k]["frac_buena"] for r in pr), 3) for k in ("N", "D", "E", "X", "A", "E2")} if pr else {}}
    o["primaria_pasa"] = o["pasa_005"] >= 9
    o["indicio"] = bool(fb) and o["positivos"] >= 7 and o["mediana"] >= 0.03 and o["mediana"] > 2 * o["ruido_mediano"]
    sm = sorted(rows(f"{R}/_sonda_{SRC[n].replace('veneno_', 'veneno_')}.jsonl"), key=lambda r: r["seed"])
    nu = rows(f"{R}/_sonda_{SRC[n]}_nulo.jsonl")
    adv = lambda r: r["plastico"]["ingesta_por_paso"] / r["congelado"]["ingesta_por_paso"] - 1
    o["sonda_A"] = [round(adv(r), 3) for r in sm]
    o["sonda_dD"] = [round(r["plastico"]["D"] - r["congelado"]["D"], 3) for r in sm]
    o["p_comer_vacia_plast_menos_cong"] = [round(r["plastico"]["p_comer_vacia"] - r["congelado"]["p_comer_vacia"], 3) for r in sm]
    o["p_comer_buena_plast_menos_cong"] = [round(r["plastico"]["p_comer_buena"] - r["congelado"]["p_comer_buena"], 3) for r in sm]
    o["nulo_A"] = [round(adv(r), 3) for r in nu]
    out[n] = o
ct = rows(f"{R}/_control_c.jsonl")
if ct:
    g = lambda grp, m: [r["dif"][grp][m] for r in ct]
    out["hcontrol_C"] = {
        "positivo_fb": [round(v, 3) for v in g("positivo", "frac_buena")], "positivo_se": [round(v, 3) for v in g("positivo", "sel_entrada")],
        "positivo_pasa": sum(a >= 0.05 for a in g("positivo", "frac_buena")), "positivo_se_pasa": sum(a >= 0.05 for a in g("positivo", "sel_entrada")),
        "debil_fb": [round(v, 3) for v in g("debil", "frac_buena")],
        "negativo_ok": sum(abs(a) < 0.05 and abs(b) < 0.05 for a, b in zip(g("negativo", "frac_buena"), g("negativo", "sel_entrada")))}
print(json.dumps(out, ensure_ascii=False, indent=1))
if out["C"]["fb"] and out["Cbar"]["fb"]:
    out["C_menos_Cbar_mediana"] = round(st.median(out["C"]["fb"]) - st.median(out["Cbar"]["fb"]), 4)
    out["primaria_C"] = out["C"]["primaria_pasa"] and out["C_menos_Cbar_mediana"] > 0
for k in ("C", "Cbar", "padre"):
    out[k].pop("fb", None)
print(json.dumps({k: out.get(k) for k in ("C_menos_Cbar_mediana", "primaria_C")}))
json.dump(out, open(f"{R}/_analisis_c.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
