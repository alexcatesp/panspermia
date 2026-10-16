"""Compara dos lotes de aceptación (p. ej. fase 1 frente a fase 1b) en una ventana común de épocas.

Lee `stats/summary.json` de cada semilla y resume, por lote, la media entre semillas de varias
métricas en las épocas (desde, hasta]. Solo lectura.

Uso: python scripts/compare_runs.py runs/phase1 runs/phase1b --to 100
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

KEYS = ["population", "hidden_mean", "attack_gene_mean", "deaths_attack", "deaths_starvation",
        "deaths_poison", "groups_silhouette", "groups_k", "comm_mi_bits", "archive_size",
        "genome_distance", "clades_alive", "toxic_intake_frac", "emit_nutrient", "emit_toxin",
        "emit_pheromone", "desc_speed", "desc_turn", "desc_intake"]


def _load(d: Path, lo: int, hi: int) -> list[dict]:
    rows = json.loads((d / "stats" / "summary.json").read_text())
    return [r for r in rows if lo < r["epoch"] <= hi]


def _mean(xs):
    xs = [x for x in xs if x is not None and not (isinstance(x, float) and math.isnan(x))]
    return sum(xs) / len(xs) if xs else None


def summarize(root: Path, lo: int, hi: int) -> dict:
    per_seed = {}
    for d in sorted(root.glob("s*")):
        if not (d / "stats" / "summary.json").exists():
            continue
        rows = _load(d, lo, hi)
        if not rows:
            continue
        s = {k: _mean([r.get(k) for r in rows]) for k in KEYS}
        lv = [r["learning_value"] for r in rows if r.get("learning_value") is not None]
        s["learning_value"] = _mean(lv)
        s["learning_n"] = len(lv)
        last = rows[-1]
        s["hidden_last"] = last.get("hidden_mean")
        s["epochs"] = last["epoch"]
        s["paused"] = (d / "CAPABILITY_PAUSE.json").exists()
        per_seed[d.name] = s
    keys = [k for k in KEYS + ["learning_value", "hidden_last"]]
    agg = {k: _mean([s[k] for s in per_seed.values()]) for k in keys}
    return {"per_seed": per_seed, "mean": agg}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    p.add_argument("--from", dest="lo", type=int, default=0)
    p.add_argument("--to", dest="hi", type=int, default=100)
    a = p.parse_args()
    sa, sb = summarize(a.a, a.lo, a.hi), summarize(a.b, a.lo, a.hi)
    print(f"épocas ({a.lo}, {a.hi}] · {a.a} ({len(sa['per_seed'])} semillas) frente a "
          f"{a.b} ({len(sb['per_seed'])} semillas)")
    fmt = lambda v: "—" if v is None else f"{v:.4g}"
    for k in sa["mean"]:
        print(f"  {k:22s} {fmt(sa['mean'][k]):>10s} {fmt(sb['mean'][k]):>10s}")
    for name, s in (("A", sa), ("B", sb)):
        for seed, v in s["per_seed"].items():
            print(f"  {name} {seed}: aprendizaje {fmt(v['learning_value'])} (n={v['learning_n']}) · "
                  f"ocultas final {fmt(v['hidden_last'])} · silueta {fmt(v['groups_silhouette'])} · "
                  f"pausada {v['paused']} · época {v['epochs']}")


if __name__ == "__main__":
    main()
