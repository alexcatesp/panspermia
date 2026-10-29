"""Comprobación de la integración (ADR-019): control bit a bit y P0-escalera."""
import json
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    return json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
# 1) control: mismas filas que P0-feliz s0 en todas las claves comunes salvo el tiempo
a, b = rows("P0-feliz", 0), rows("P0-feliz-control-int", 0)
skip = {"seconds"}
diff = [(r1["epoch"], k) for r1, r2 in zip(a, b) for k in r1 if k in r2 and k not in skip and r1[k] != r2[k]]
print("control: épocas", len(a), len(b), "· diferencias", len(diff), diff[:5])
# 2) P0-escalera frente a P0-feliz, P0-feliz-neutral y P0-feliz-cppn-neutral
keys = ["hidden_mean", "cppn_nodes_mean", "cppn_edges_mean", "genome_distance", "genome_distance_struct", "clades_alive", "thrust_mean"]
def late(rs, k): 
    v = [r[k] for r in rs if 151 <= r["epoch"] <= 300 and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
def at(rs, k, e=300):
    v = [r[k] for r in rs if r["epoch"] == e]
    return v[0] if v else None
out = {}
for c in ("P0-feliz", "P0-feliz-neutral", "P0-feliz-cppn-neutral", "P0-escalera"):
    for s in range(5):
        p = R / c / f"s{s}" / "stats" / "summary.json"
        if p.exists():
            rs = rows(c, s); out[f"{c}/s{s}"] = {k: (late(rs, k), at(rs, k)) for k in keys}
for k in keys:
    print(f"\n{k}")
    for c in ("P0-feliz", "P0-feliz-neutral", "P0-feliz-cppn-neutral", "P0-escalera"):
        v = [out.get(f"{c}/s{s}", {}).get(k) for s in range(5)]
        print(f"  {c:24s}", " ".join("   -   " if x is None or x[0] is None else f"{x[0]:7.2f}/{x[1]:7.2f}" for x in v))
(R / "_analisis_P0int.json").write_text(json.dumps({"control_diffs": len(diff), "series": out}, indent=1))
