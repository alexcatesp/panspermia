"""Pruebas de la masa (diseno v1.6): grande frente a chico, ramas y hijo8; referencia P4-salto64."""
import json, sys
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    p = R / c / f"s{s}" / "stats" / "summary.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
keys = ["va_intake", "mass_mean", "hidden_mean", "lifespan_mean", "population", "intake", "thrust_mean"]
C = {"P4-salto64": range(5), "P4-salto64-grande": range(5), "P4-salto64-chico": range(5), "P4-salto64-hijo8": range(5),
     "P4-salto64-rama1": [1, 2], "P4-salto64-rama2": [1, 2], "P4-salto64-rama3": [1, 2]}
out = {}
for c, ss in C.items():
    out[c] = {}
    for s in ss:
        rs = rows(c, s)
        if not rs or not (R / c / f"s{s}" / "result.json").exists():
            continue
        d = {k: late(rs, k) for k in keys}
        d["epochs"] = max(r["epoch"] for r in rs)
        d["extinct_at"] = json.loads((R / c / f"s{s}" / "result.json").read_text())["extinct_at"]
        out[c][s] = d
f = lambda x: "    -   " if x is None else f"{x:+8.3f}"
for k in keys + ["epochs", "extinct_at"]:
    print(f"\n{k}")
    for c in C:
        print(f"  {c:18s}", " ".join(f"s{s}:{f(d[k]) if isinstance(d[k], float) else d[k]}" for s, d in out[c].items()))
print("\n(1)-(2) VA grande > chico y grande > 0:")
ok = 0
for s in range(5):
    g, ch = out["P4-salto64-grande"].get(s, {}).get("va_intake"), out["P4-salto64-chico"].get(s, {}).get("va_intake")
    p = g is not None and ch is not None and g > 0 and g > ch
    ok += p; print(f"  s{s}: grande {f(g)} chico {f(ch)} {'sí' if p else 'no'}")
print(f"  -> {ok}/5")
print("\n(3) ramas: masa 151-300 (grande si > 1,5)")
for c in ["P4-salto64", "P4-salto64-rama1", "P4-salto64-rama2", "P4-salto64-rama3"]:
    print(f"  {c:18s}", " ".join(f"s{s}:{out[c][s]['mass_mean']:.2f}" for s in (1, 2) if s in out[c]))
(R / "_analisis_masa.json").write_text(json.dumps(out, indent=1))
