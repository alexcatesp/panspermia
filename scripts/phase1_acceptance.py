"""Criterios de aceptación de la fase 1 (spec §Fases).

    python scripts/phase1_acceptance.py run --seeds 0 1 2 3 4 --epochs 500 --out runs/phase1
    python scripts/phase1_acceptance.py eval --out runs/phase1

Criterios:
1. ≥ 2 grupos conductuales estables (silueta ≥ 0,3) durante ≥ 50 épocas consecutivas.
2. Valor del aprendizaje positivo con p < 0,05 en 5 semillas (test exacto de signos por
   permutación sobre las medias por semilla; se informa también un t pooled de referencia).
3. El archivo de novedad sigue creciendo a las 500 épocas (altas en las últimas 50 épocas).
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


def run(seeds: list[int], epochs: int, out: Path) -> None:
    from panspermia import run as runner
    for s in seeds:
        d = out / f"s{s}"
        print(f"=== semilla {s} → {d}", flush=True)
        try:
            r = runner.run(s, epochs, d, f"phase1-{s}".encode(), runner.C.N_MAX, runner.C.N_INIT)
        except runner.CapabilityPause as exc:
            r = {"paused": True, "error": str(exc)}
        print(json.dumps(r), flush=True)


def _longest_run(flags: list[bool]) -> int:
    best = cur = 0
    for f in flags:
        cur = cur + 1 if f else 0
        best = max(best, cur)
    return best


def _sign_flip_p(xs: list[float]) -> float:
    """p exacto unilateral (media > 0) por permutación de signos."""
    obs = sum(xs)
    combos = list(itertools.product((1, -1), repeat=len(xs)))
    return sum(sum(s * x for s, x in zip(c, xs)) >= obs - 1e-12 for c in combos) / len(combos)


def evaluate(out: Path, epochs: int) -> dict:
    seeds = {}
    for d in sorted(out.glob("s*")):
        f = d / "stats" / "summary.json"
        if not f.exists():
            continue
        rows = json.loads(f.read_text())
        groups = [r.get("groups_k", 0) >= 2 and r.get("groups_silhouette", 0) >= 0.3 for r in rows]
        lv = [r["learning_value"] for r in rows if r.get("learning_value") is not None]
        arch = {r["epoch"]: r["archive_size"] for r in rows}
        last = max(arch) if arch else 0
        growth = arch.get(last, 0) - arch.get(max(0, last - 50), 0) if last > 50 else None
        seeds[d.name] = {
            "epochs": last,
            "paused": (d / "CAPABILITY_PAUSE.json").exists(),
            "groups_longest_stable": _longest_run(groups),
            # más exigente que la spec: la diversidad aleatoria inicial ya forma grupos (ADR-007)
            "groups_longest_stable_late": _longest_run(
                [g for g, r in zip(groups, rows) if r["epoch"] > epochs // 2]),
            "learning_tests": len(lv),
            "learning_mean": sum(lv) / len(lv) if lv else None,
            "archive_final": arch.get(last),
            "archive_growth_last_50": growth,
        }
    means = [s["learning_mean"] for s in seeds.values() if s["learning_mean"] is not None]
    pooled = [r for d in sorted(out.glob("s*")) if (d / "stats" / "summary.json").exists()
              for r in (x["learning_value"] for x in json.loads((d / "stats" / "summary.json").read_text())
                        if x.get("learning_value") is not None)]
    t_p = None
    if len(pooled) > 2:
        m = sum(pooled) / len(pooled)
        sd = math.sqrt(sum((x - m) ** 2 for x in pooled) / (len(pooled) - 1))
        t_p = 0.5 * math.erfc((m / (sd / math.sqrt(len(pooled)))) / math.sqrt(2)) if sd > 0 else None
    complete = [s for s in seeds.values() if s["epochs"] >= epochs]
    result = {
        "seeds": seeds,
        "criterion_groups": bool(complete) and all(s["groups_longest_stable"] >= 50 for s in complete),
        "learning_sign_flip_p": _sign_flip_p(means) if len(means) >= 2 else None,
        "learning_pooled_normal_p": t_p,
        "criterion_learning": len(means) >= 5 and _sign_flip_p(means) < 0.05,
        "criterion_novelty": bool(complete) and all((s["archive_growth_last_50"] or 0) > 0 for s in complete),
    }
    return result


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=["run", "eval"])
    p.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    p.add_argument("--epochs", type=int, default=500)
    p.add_argument("--out", type=Path, default=Path("runs/phase1"))
    a = p.parse_args()
    if a.cmd == "run":
        run(a.seeds, a.epochs, a.out)
    print(json.dumps(evaluate(a.out, a.epochs), indent=2))


if __name__ == "__main__":
    main()
