"""(b0) del panel 04 (ADR-029, prerregistro en decisiones.md, 26-10, 02:51): ¿la tasa de altas al archivo de novedad
sirve como medida de crecimiento abierto? Solo lee runs/fase1d/<ejecución>/s<k>/stats/summary.json. Exploratorio.
Ventana 151–300. Sin el nº de adultos en las estadísticas, se usa la población como aproximación (declarado).
"""
import json, statistics as st, sys
from pathlib import Path

R = Path(sys.argv[1] if len(sys.argv) > 1 else "runs/fase1d")
RUNS = {"P0": "P0-escalera", "P1": "P1-escalera", "P2": "P2-escalera", "P3e": "P3-escaso",
        "P4salto": "P4-salto64", "P4alga": "P4-alga", "P2-600": "P2-escalera-600", "P2sex-600": "P2-escalera-sexual-600"}


def load(run):
    out = []
    for sd in sorted((R / run).glob("s[0-9]*")):
        rows = {r["epoch"]: r for r in json.loads((sd / "stats" / "summary.json").read_text())}
        out.append((sd.name, rows))
    return out


def mean(rows, key, a, b, norm=False):
    v = [rows[e][key] / (rows[e]["population"] if norm else 1) for e in range(a, b + 1) if e in rows]
    return sum(v) / len(v) if v else float("nan")


def slope(rows, key, a, b):
    xs = [e for e in range(a, b + 1) if e in rows]
    ys = [rows[e][key] for e in xs]
    mx, my = st.mean(xs), st.mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def per_seed(rows, a=151, b=300):
    pop = mean(rows, "population", a, b)
    rate = mean(rows, "novelty_added", a, b)
    early, late = mean(rows, "novelty_added", a, (a + b) // 2), mean(rows, "novelty_added", (a + b) // 2 + 1, b)
    descs = [k for k in rows[b] if k.startswith("desc_")]
    varying = sum(1 for k in descs if st.pstdev([rows[e][k] for e in range(a, b + 1) if e in rows]) > 1e-6)
    return {"tasa": rate, "tasa_pob": rate / pop * 1000, "pob": pop, "satura": late / early if early > 0 else None,
            "bp_pob": mean(rows, "bp_new_activity", a, b) / pop * 1000,
            "cerebro_pendiente": slope({e: {"x": r["hidden_mean"] + r["synapses_mean"]} for e, r in rows.items()}, "x", a, b),
            "desc_varian": varying, "repro_age": mean(rows, "desc_repro_age", a, b), "archivo_final": rows[b]["archive_size"]}


res = {}
for tag, run in RUNS.items():
    res[tag] = [{"seed": s, **per_seed(rows)} for s, rows in load(run)]
    if tag.endswith("600"):
        for (s, rows), d in zip(load(run), res[tag]):
            d["tasa_300_600"] = mean(rows, "novelty_added", 301, 600)
med = lambda tag, k: st.median(x[k] for x in res[tag])
for tag in RUNS:
    print(f"{tag:10s} tasa {[round(x['tasa'], 2) for x in res[tag]]} med {med(tag, 'tasa'):.2f} · por mil bichos "
          f"{med(tag, 'tasa_pob'):.3f} · pob {med(tag, 'pob'):.0f} · satura {[None if x['satura'] is None else round(x['satura'], 2) for x in res[tag]]}"
          f" · bp/pob {med(tag, 'bp_pob'):.3f} · cerebro {med(tag, 'cerebro_pendiente'):+.4f} · desc {med(tag, 'desc_varian')}"
          f" · repro_age {med(tag, 'repro_age'):.3f} · archivo {med(tag, 'archivo_final'):.0f}"
          + (f" · 300–600 {[round(x['tasa_300_600'], 2) for x in res[tag]]}" if tag.endswith("600") else ""))


def verdict(k):
    stable = [x[k] for t in ("P2", "P3e") for x in res[t]]
    m_st = st.median(stable)
    i_counts = {t: sum(x[k] > m_st for x in res[t]) for t in ("P4salto", "P4alga")}
    i_ok = all(c >= 4 for c in i_counts.values())
    sel = [x[k] for t in ("P1", "P2", "P3e") for x in res[t]]
    ii_ok = st.median(sel) > med("P0", k)
    p2_desc = sum(x[k] > med("P0", k) for x in res["P2"])
    return i_ok, ii_ok, i_counts, m_st, st.median(sel), p2_desc


iok, iiok, ic, mst, msel, p2d = verdict("tasa")
iokn, _, icn, _, _, _ = verdict("tasa_pob")
print(f"\n(i) bruta {ic} sobre la mediana estable {mst:.2f} → {iok}; normalizada {icn} → {iokn}")
print(f"(ii) mediana con selección {msel:.2f} frente a P0 {med('P0', 'tasa'):.2f} → {iiok}; P2 sobre la mediana de P0: {p2d}/5")
floor = all(med(t, "tasa") < 1 for t in RUNS)
small = any(x["pob"] < 512 for t in RUNS for x in res[t])
repro_art = (not iiok) and all(med("P0", "repro_age") > med(t, "repro_age") for t in ("P1", "P2", "P3e"))
if floor or small or iok != iokn or repro_art:
    v = "no se puede saber"
elif iok and iiok:
    v = "vale"
else:
    v = "no vale"
print(f"suelo {floor} · <512 {small} · (i) cambia al normalizar {iok != iokn} · artefacto repro_age {repro_art}")
print("VEREDICTO:", v)
json.dump({"res": res, "veredicto": v, "i": [iok, ic], "i_norm": [iokn, icn], "ii": [iiok, msel, med("P0", "tasa"), p2d]},
          open(R / "_b0_novedad.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
