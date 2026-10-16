"""Resumen por condición de los experimentos de la fase 1d (solo lectura).

Lee `<raíz>/<condición>/s<semilla>/{stats/summary.json,result.json,run.json}` y saca, por condición,
la **mediana** entre semillas (en el CSV, también la media y la desviación) de: supervivencia,
población, duración de la vida, tiempo de generación, valor del aprendizaje (VA, sonda emparejada;
primaria `va_log_population`, diseño v0.4), neuronas ocultas, fracción tóxica, uso del reloj,
anticipación y segundos por época. Las medidas «tardías» usan la última mitad de las épocas.

Uso: python scripts/analyze_1d.py runs/fase1d [--csv runs/fase1d/resumen.csv]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from itertools import pairwise
from pathlib import Path


def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return sum(xs) / len(xs) if xs else None


def _median(xs):
    xs = sorted(x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x)))
    n = len(xs)
    if not n:
        return None
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2


def _sd(xs):
    xs = [x for x in xs if x is not None]
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def seed_summary(d: Path) -> dict | None:
    f = d / "stats" / "summary.json"
    if not f.exists():
        return None
    rows = json.loads(f.read_text())
    if not rows:
        return None
    result = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
    last = rows[-1]["epoch"]
    late = [r for r in rows if r["epoch"] > last / 2]
    gens = [r.get("generation_mean") for r in rows]
    tau_gen = None
    if len(rows) > 10 and gens[-1] and gens[len(gens) // 2]:
        de = rows[-1]["epoch"] - rows[len(rows) // 2]["epoch"]
        dg = gens[-1] - gens[len(gens) // 2]
        tau_gen = 1000 * de / dg if dg > 0 else None
    return {
        "epochs": last,
        "finished": result.get("final_population") is not None,
        "extinct": bool(result.get("stopped_extinct")) or any(r["population"] == 0 for r in rows[-5:]),
        "extinct_at": result.get("extinct_at"),
        "paused": bool(result.get("paused")),
        "population_late": _mean([r["population"] for r in late]),
        "population_min": min(r["population_min"] for r in rows),
        "lifespan": _mean([r.get("lifespan_mean") for r in late]),
        "tau_gen": tau_gen,
        "va_log_population": _mean([r.get("va_log_population") for r in late]),
        "va_log_intake": _mean([r.get("va_log_intake") for r in late]),
        "va_population": _mean([r.get("va_population") for r in late]),
        "va_intake": _mean([r.get("va_intake") for r in late]),
        "va_toxic_frac": _mean([r.get("va_toxic_frac") for r in late]),
        "hidden": _mean([r.get("hidden_mean") for r in late]),
        "toxic_frac": _mean([r.get("toxic_intake_frac") for r in late]),
        "clock_rhythm": _mean([r.get("clock_rhythm") for r in late]),
        "anticipation": _mean([r.get("anticipation") for r in late]),
        "attack_gene": _mean([r.get("attack_gene_mean") for r in late]),
        "sec_per_epoch": _mean([r.get("seconds") for r in rows[1:]]),
    }


def recovery_curve(rows: list[dict]) -> list[float | None]:
    """Fracción tóxica agregada por intervalo de tiempo desde el último cambio del parche."""
    out = []
    b = 0
    while f"recov_intake_b{b}" in rows[-1]:
        food = sum(r.get(f"recov_intake_b{b}") or 0.0 for r in rows)
        tox = sum((r.get(f"recov_toxic_frac_b{b}") or 0.0) * (r.get(f"recov_intake_b{b}") or 0.0)
                  for r in rows)
        out.append(tox / food if food > 0 else None)
        b += 1
    return out


def recovery_summary(d: Path) -> dict | None:
    """Curva de recuperación tardía y «aprender a aprender»: fracción tóxica en los primeros 64
    pasos tras un cambio, en las épocas 41–100 (veneno pleno) frente a las últimas 100."""
    f = d / "stats" / "summary.json"
    if not f.exists():
        return None
    rows = [r for r in json.loads(f.read_text()) if "recov_intake_b0" in r and r["population"] >= 64]
    if len(rows) < 20:
        return None
    last = rows[-1]["epoch"]
    early_rows = [r for r in rows if 40 < r["epoch"] <= 100]
    late_rows = [r for r in rows if r["epoch"] > last - 100]
    fast = lambda c: _mean([x for x in c[:4] if x is not None])  # intervalos < 64 pasos
    curve_late = recovery_curve(late_rows)
    fast_early = fast(recovery_curve(early_rows)) if early_rows else None
    return {"curve_late": curve_late, "fast_early": fast_early, "fast_late": fast(curve_late)}


KEYS = ["population_late", "population_min", "lifespan", "tau_gen", "va_log_population",
        "va_log_intake", "va_population", "va_intake",
        "va_toxic_frac", "hidden", "toxic_frac", "clock_rhythm", "anticipation", "attack_gene",
        "sec_per_epoch"]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--csv", type=Path)
    a = p.parse_args()
    table = []
    for cond in sorted(d for d in a.root.iterdir() if d.is_dir()):
        seeds = {s.name: seed_summary(s) for s in sorted(cond.glob("s*"))}
        seeds = {k: v for k, v in seeds.items() if v}
        if not seeds:
            continue
        alive = [v for v in seeds.values() if not v["extinct"]]
        row = {"condition": cond.name, "n_seeds": len(seeds), "survived": len(alive),
               "extinct_epochs": [v["extinct_at"] for v in seeds.values() if v["extinct"]]}
        for k in KEYS:
            vals = [v[k] for v in alive] or [v[k] for v in seeds.values()]
            row[k] = _median(vals)
            row[k + "_mean"] = _mean(vals)
            row[k + "_sd"] = _sd(vals)
        table.append(row)
    fmt = lambda v: "—" if v is None else (f"{v:.3g}" if isinstance(v, float) else str(v))
    print(f"{'condición':32s} {'sobrev.':>8s} " + " ".join(f"{k[:11]:>11s}" for k in KEYS))
    for r in table:
        print(f"{r['condition']:32s} {r['survived']}/{r['n_seeds']:<6d} "
              + " ".join(f"{fmt(r[k]):>11s}" for k in KEYS))
        if r["extinct_epochs"]:
            print(f"{'':32s} extinciones en las épocas {r['extinct_epochs']}")
    edges = (8, 16, 32, 64, 128, 256, 512, 1024, 2048)  # = config.RECOVERY_EDGES
    labels = ([f"<{edges[0]}"] + [f"{lo}-{hi}" for lo, hi in pairwise(edges)]
              + [f">={edges[-1]}"])
    print()
    print("Curva de recuperación: fracción tóxica según los pasos desde el cambio del parche "
          "(últimas 100 épocas; mediana entre semillas). «Aprender a aprender»: fracción tóxica en "
          "los primeros 64 pasos, épocas 41–100 frente a las últimas 100.")
    print(f"{'condición':32s} " + " ".join(f"{x:>9s}" for x in labels)
          + f" {'rápida 41-100':>14s} {'rápida final':>13s}")
    for cond in sorted(d for d in a.root.iterdir() if d.is_dir()):
        recs = [recovery_summary(s) for s in sorted(cond.glob("s*"))]
        recs = [r for r in recs if r]
        if not recs:
            continue
        curve = [_median([r["curve_late"][b] for r in recs if b < len(r["curve_late"])])
                 for b in range(len(labels))]
        fe, fl = _median([r["fast_early"] for r in recs]), _median([r["fast_late"] for r in recs])
        print(f"{cond.name:32s} " + " ".join(f"{fmt(x):>9s}" for x in curve)
              + f" {fmt(fe):>14s} {fmt(fl):>13s}")
    if a.csv:
        with a.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)


if __name__ == "__main__":
    main()
