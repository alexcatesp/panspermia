import json, sys
from pathlib import Path
R = Path("runs/fase1d")
keys = ["hidden_mean", "hidden_max", "cppn_nodes_mean", "cppn_edges_mean", "genome_distance", "genome_distance_struct",
        "clades_alive", "clade_shannon", "kin_local", "kin_global", "synapses_mean", "thrust_mean"]
def late(rows, k, lo=151, hi=300):
    v = [r[k] for r in rows if lo <= r["epoch"] <= hi and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
def at(rows, k, e):
    v = [r[k] for r in rows if r["epoch"] == e and isinstance(r.get(k), (int, float))]
    return v[0] if v else None
out = {}
for cond in sys.argv[1:]:
    for s in range(5):
        p = R / cond / f"s{s}" / "stats" / "summary.json"
        if not p.exists(): continue
        rows = json.loads(p.read_text(encoding="utf-8"))
        out[f"{cond}/s{s}"] = {k: (late(rows, k), at(rows, k, 300)) for k in keys}
for k in keys:
    print(f"\n{k}")
    for cond in sys.argv[1:]:
        vals = [out.get(f"{cond}/s{s}", {}).get(k) for s in range(5)]
        print(f"  {cond:24s}", " ".join("   -   " if v is None or v[0] is None else f"{v[0]:8.3f}/{v[1]:8.3f}" for v in vals))
(R / "_analisis_A1_P1.json").write_text(json.dumps(out, indent=1))
