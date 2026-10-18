"""Análisis prerregistrado de la escalera de complejidad (docs/escalera/diseno.md, ADR-014/015).

Para cada condición y semilla: media de cada medida en la ventana tardía (épocas 151–300) y
pendiente (mínimos cuadrados) en esa ventana. Para cada comparación emparejada por semilla:
diferencia, cuántas semillas tienen el signo predicho y prueba de signos exacta unilateral.

Solo usa la biblioteca estándar: desde Windows basta `python scripts/analyze_ladder.py runs/fase1d`.

    python scripts/analyze_ladder.py runs/fase1d --compare P0-feliz-neutral:P0-feliz:hidden_mean:<
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

MEASURES = ("hidden_mean", "thrust_mean", "desc_speed", "mass_mean", "max_thrust_mean", "population",
            "lifespan_mean", "intake", "toxic_intake_frac", "cppn_nodes_mean", "cppn_edges_mean",
            "synapses_mean", "generation_mean", "va_log_population")
LATE = (151, 300)

# Comparaciones prerregistradas (diseño v0.1 y v0.3): (condición, referencia, medida, signo predicho)
PREREG = [
    ("P0-feliz-neutral", "P0-feliz", "hidden_mean", "<"),
    ("P0-feliz-terrestre", "P0-feliz-neutral", "hidden_mean", "<"),
    ("P1-peaje", "P0-feliz", "thrust_mean", "<"),
    ("P1-peaje-neutral", "P0-feliz-neutral", "thrust_mean", "<"),
    ("P1-peaje-terrestre", "P0-feliz-terrestre", "thrust_mean", "<"),
    ("P2-comida-quieta", "P1-peaje", "lifespan_mean", ">"),
    ("P3-hijos-pagados", "P2-comida-quieta", "population", "<"),
    ("P4-comida-movil", "P3-hijos-pagados", "thrust_mean", ">"),
]


def load(runs: Path, cond: str) -> dict[int, list[dict]]:
    out = {}
    for d in sorted((runs / cond).glob("s*")):
        p = d / "stats" / "summary.json"
        if p.exists() and (d / "result.json").exists():
            out[int(d.name[1:])] = json.loads(p.read_text(encoding="utf-8"))
    return out


def window(rows: list[dict], key: str, lo: int, hi: int) -> list[tuple[int, float]]:
    return [(r["epoch"], r[key]) for r in rows
            if lo <= r["epoch"] <= hi and isinstance(r.get(key), (int, float)) and not math.isnan(r[key])]


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def slope(pts):
    if len(pts) < 3:
        return None
    mx, my = mean([p[0] for p in pts]), mean([p[1] for p in pts])
    sxx = sum((p[0] - mx) ** 2 for p in pts)
    return sum((p[0] - mx) * (p[1] - my) for p in pts) / sxx if sxx else None


def summarize(seeds: dict[int, list[dict]]) -> dict[int, dict]:
    res = {}
    for s, rows in seeds.items():
        res[s] = {}
        for k in MEASURES:
            pts = window(rows, k, *LATE)
            first = window(rows, k, 1, 10)
            res[s][k] = {"late": mean([p[1] for p in pts]), "slope100": (slope(pts) or 0) * 100 if pts else None,
                         "start": mean([p[1] for p in first])}
    return res


def sign_test(n_ok: int, n: int) -> float:
    """p unilateral exacta de obtener ≥ n_ok aciertos de n con p = 1/2."""
    return sum(math.comb(n, k) for k in range(n_ok, n + 1)) / 2 ** n


def compare(a: dict, b: dict, key: str, sign: str) -> dict:
    seeds = sorted(set(a) & set(b))
    diffs = [(s, a[s][key]["late"] - b[s][key]["late"]) for s in seeds
             if a[s][key]["late"] is not None and b[s][key]["late"] is not None]
    ok = sum((d < 0) if sign == "<" else (d > 0) for _, d in diffs)
    return {"key": key, "sign": sign, "diffs": diffs, "n_ok": ok, "n": len(diffs),
            "p": sign_test(ok, len(diffs)) if diffs else None,
            "criterio_5de5": len(diffs) == 5 and ok == 5}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("runs", type=Path)
    ap.add_argument("--conds", nargs="*", default=None, help="condiciones a resumir (por defecto, todas las P*)")
    ap.add_argument("--json", type=Path, help="vuelca el resumen en JSON")
    a = ap.parse_args()
    conds = a.conds or sorted(d.name for d in a.runs.iterdir() if d.is_dir() and d.name[:2] in {f"P{i}" for i in range(10)})
    data = {c: summarize(load(a.runs, c)) for c in conds}
    print(f"Ventana tardía: épocas {LATE[0]}–{LATE[1]} · media por semilla (pendiente por 100 épocas)\n")
    for c, seeds in data.items():
        if not seeds:
            continue
        print(f"== {c} ({len(seeds)} semillas)")
        for k in MEASURES:
            vals = [seeds[s][k] for s in sorted(seeds)]
            if all(v["late"] is None for v in vals):
                continue
            cells = " ".join(f"{v['late']:8.3f}({v['slope100']:+.2f})" if v["late"] is not None else "       —" for v in vals)
            print(f"  {k:18s} inicio {mean([v['start'] for v in vals if v['start'] is not None]) or 0:7.2f} | {cells}")
    print("\nComparaciones prerregistradas (emparejadas por semilla):")
    out = []
    for c, ref, key, sign in PREREG:
        if data.get(c) and data.get(ref):
            r = compare(data[c], data[ref], key, sign)
            out.append({"cond": c, "ref": ref, **r})
            d = ", ".join(f"s{s} {x:+.3f}" for s, x in r["diffs"])
            print(f"  {c} vs {ref} · {key} {sign}: {r['n_ok']}/{r['n']} (p = {r['p']:.4f})"
                  f" → {'CUMPLE' if r['criterio_5de5'] else 'no cumple'} · {d}")
    if a.json:
        a.json.write_text(json.dumps({"summary": data, "comparisons": out}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
