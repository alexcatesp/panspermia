"""Contraste prerregistrado de H1 y H2 con los resultados de E1 (diseño 1d §8; solo lectura).

Por semilla se usa la media tardía (épocas > última/2) de VA_log, uso del reloj y anticipación.
Las semillas extinguidas quedan fuera (se informa).

- H1 (aleatorio): VA = a + b·log T + c·(log T)². Hay campana si el IC del 95 % de c (*bootstrap*
  por semillas dentro de cada periodo) queda por debajo de 0 y el vértice cae dentro del rango.
- H2 (periódico frente a aleatorio, emparejado por semilla en cada T): VA, reloj. Permutación de
  signos exacta (bilateral) y Holm por los 4 periodos. La anticipación solo existe en el periódico:
  se contrasta contra 0 con la misma permutación de signos.
- Exploratorio: lo mismo agrupando los 4 periodos (una sola prueba de signos sobre todos los pares).

Uso: python scripts/e1_hypotheses.py runs/fase1d [--boot 10000]
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path

import numpy as np

PERIODS = (35, 140, 560, 2240)
KEYS = ("va_log_population", "clock_rhythm", "anticipation")


def seed_values(d: Path) -> dict | None:
    rows = json.loads((d / "stats" / "summary.json").read_text())
    res = json.loads((d / "result.json").read_text()) if (d / "result.json").exists() else {}
    if res.get("stopped_extinct") or res.get("extinct_at") is not None:
        return None
    last = rows[-1]["epoch"]
    late = [r for r in rows if r["epoch"] > last / 2]
    out = {}
    for k in KEYS:
        v = [r[k] for r in late if r.get(k) is not None and not math.isnan(r[k])]
        out[k] = float(np.mean(v)) if v else None
    return out


def load(root: Path, cond: str) -> dict[int, dict]:
    out = {}
    for d in sorted((root / cond).glob("s*")):
        v = seed_values(d)
        if v is not None:
            out[int(d.name[1:])] = v
    return out


def sign_flip_p(diffs: np.ndarray) -> float:
    """p bilateral exacta de la permutación de signos (media de las diferencias)."""
    diffs = np.asarray(diffs, float)
    obs = abs(diffs.mean())
    n = len(diffs)
    if n > 16:  # demasiadas combinaciones: Monte Carlo con semilla fija (solo análisis)
        rng = np.random.default_rng(0)
        signs = rng.choice((-1.0, 1.0), size=(100_000, n))
    else:
        signs = np.array(list(itertools.product((-1.0, 1.0), repeat=n)))
    null = np.abs((signs * diffs).mean(axis=1))
    return float((null >= obs - 1e-12).mean())


def holm(ps: list[float]) -> list[float]:
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[i])
        adj[i] = min(1.0, run)
    return adj.tolist()


def quad_fit(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    c, b, _ = np.polyfit(x, y, 2)
    vertex = -b / (2 * c) if c != 0 else float("nan")
    return float(c), float(vertex)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("root", type=Path)
    p.add_argument("--boot", type=int, default=10_000)
    a = p.parse_args()
    rnd = {T: load(a.root, f"E1-aleatorio-T{T:03d}") for T in PERIODS}
    per = {T: load(a.root, f"E1-periodico-T{T:03d}") for T in PERIODS}
    fixed = load(a.root, "E1-fijo")

    print("H1 · VA_log por semilla (aleatorio) y control fijo")
    for T in PERIODS:
        print(f"  T{T:<5d}", " ".join(f"s{s}:{v['va_log_population']:+.2f}" for s, v in rnd[T].items()))
    print("  fijo  ", " ".join(f"s{s}:{v['va_log_population']:+.2f}" for s, v in fixed.items()))
    xs = np.array([math.log(T) for T in PERIODS for _ in rnd[T]])
    ys = np.array([v["va_log_population"] for T in PERIODS for v in rnd[T].values()])
    c, vertex = quad_fit(xs, ys)
    rng = np.random.default_rng(0)  # solo análisis
    boot_c, boot_v = [], []
    groups = [np.array([v["va_log_population"] for v in rnd[T].values()]) for T in PERIODS]
    for _ in range(a.boot):
        yb = np.concatenate([g[rng.integers(0, len(g), len(g))] for g in groups])
        cb, vb = quad_fit(xs, yb)
        boot_c.append(cb)
        boot_v.append(vb)
    lo, hi = np.percentile(boot_c, [2.5, 97.5])
    inside = math.log(PERIODS[0]) <= vertex <= math.log(PERIODS[-1])
    print(f"  c = {c:+.3f}, IC95 [{lo:+.3f}, {hi:+.3f}]; vértice en T ≈ {math.exp(vertex):.0f} "
          f"({'dentro' if inside else 'fuera'} del rango); P(c < 0) bootstrap = "
          f"{np.mean(np.array(boot_c) < 0):.3f}")
    print(f"  → campana {'SÍ' if hi < 0 and inside else 'NO'} según el criterio prerregistrado")
    med_fixed = float(np.median([v["va_log_population"] for v in fixed.values()]))
    print(f"  control fijo (T = ∞): mediana VA_log = {med_fixed:+.2f} (H1 predice ≈ 0)")

    print("\nH2 · periódico − aleatorio, emparejado por semilla (permutación de signos, Holm × 4)")
    pooled = {k: [] for k in KEYS}
    for k in ("va_log_population", "clock_rhythm"):
        ps, lines = [], []
        for T in PERIODS:
            seeds = sorted(set(rnd[T]) & set(per[T]))
            d = np.array([per[T][s][k] - rnd[T][s][k] for s in seeds])
            pooled[k].extend(d.tolist())
            ps.append(sign_flip_p(d))
            lines.append((T, len(seeds), float(np.median(d)), int((d > 0).sum())))
        for (T, n, med, pos), pr, pa in zip(lines, ps, holm(ps), strict=True):
            print(f"  {k:18s} T{T:<5d} n={n} mediana dif {med:+.3f} ({pos}/{n} > 0) "
                  f"p = {pr:.3f}, Holm = {pa:.3f}")
    ps = []
    for T in PERIODS:
        d = np.array([v["anticipation"] for v in per[T].values() if v["anticipation"] is not None])
        pooled["anticipation"].extend(d.tolist())
        ps.append((T, d, sign_flip_p(d)))
    for (T, d, pr), pa in zip(ps, holm([x[2] for x in ps]), strict=True):
        print(f"  {'anticipation':18s} T{T:<5d} n={len(d)} mediana {np.median(d):+.3f} "
              f"({(d > 0).sum()}/{len(d)} > 0) p = {pr:.3f}, Holm = {pa:.3f}")
    n_min = min(len(set(rnd[T]) & set(per[T])) for T in PERIODS)
    print(f"  nota: con n = {n_min} pares, la p bilateral mínima posible es {2 / 2 ** n_min:.3f}; "
          f"Holm × 4 exige p < {0.05 / 4:.4f} en la menor")

    print("\nExploratorio · los 4 periodos agrupados (una prueba por medida)")
    for k, d in pooled.items():
        d = np.array(d)
        print(f"  {k:18s} n={len(d)} mediana {np.median(d):+.3f} ({(d > 0).sum()}/{len(d)} > 0) "
              f"p = {sign_flip_p(d):.4f}")


if __name__ == "__main__":
    main()
