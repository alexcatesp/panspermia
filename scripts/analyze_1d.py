"""Resumen por condición de los experimentos de la fase 1d (solo lectura).

Lee `<raíz>/<condición>/s<semilla>/{stats/summary.json,result.json,run.json}` y saca, por condición,
media ± desviación entre semillas de: supervivencia, población, duración de la vida, tiempo de
generación, valor del aprendizaje (VA, sonda emparejada), neuronas ocultas, fracción tóxica, uso del
reloj, anticipación y segundos por época. Las medidas «tardías» usan la última mitad de las épocas.

Uso: python scripts/analyze_1d.py runs/fase1d [--csv runs/fase1d/resumen.csv]
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return sum(xs) / len(xs) if xs else None


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


KEYS = ["population_late", "population_min", "lifespan", "tau_gen", "va_population", "va_intake",
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
            row[k] = _mean(vals)
            row[k + "_sd"] = _sd(vals)
        table.append(row)
    fmt = lambda v: "—" if v is None else (f"{v:.3g}" if isinstance(v, float) else str(v))
    print(f"{'condición':32s} {'sobrev.':>8s} " + " ".join(f"{k[:11]:>11s}" for k in KEYS))
    for r in table:
        print(f"{r['condition']:32s} {r['survived']}/{r['n_seeds']:<6d} "
              + " ".join(f"{fmt(r[k]):>11s}" for k in KEYS))
        if r["extinct_epochs"]:
            print(f"{'':32s} extinciones en las épocas {r['extinct_epochs']}")
    if a.csv:
        with a.csv.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(table[0]))
            w.writeheader()
            w.writerows(table)


if __name__ == "__main__":
    main()
