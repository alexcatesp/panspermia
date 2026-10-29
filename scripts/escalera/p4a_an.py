"""P4-alga (diseno v1.3) frente a P3-escaso."""
import json
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    rs = json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
    return rs
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
def mn(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return min(v) if v else None
keys = ["population", "lifespan_mean", "thrust_mean", "intake", "hidden_mean", "va_intake", "va_log_intake",
        "births", "deaths_starvation", "deaths_age", "mean_energy", "generation_max",
        "cap_patch_success", "cap_patch_gain", "cap_maze_gain", "cap_patch_baseline_random", "cap_patch_baseline_controls", "mass_mean", "resources_total"]
C = ["P3-escaso", "P4-alga"]
out = {}
for c in C:
    out[c] = []
    for s in range(5):
        rs = rows(c, s)
        d = {k: late(rs, k) for k in keys}
        d["pop_min"] = mn(rs, "population"); d["epochs"] = len(rs)
        d["pop_e1_50"] = late(rs, "population", 1, 50)
        out[c].append(d)
for k in keys + ["pop_min", "pop_e1_50", "epochs"]:
    print(f"\n{k}")
    for c in C:
        print(f"  {c:14s}", " ".join("   -    " if x[k] is None else f"{x[k]:9.3f}" for x in out[c]))
(R / "_analisis_P4alga.json").write_text(json.dumps(out, indent=1))
print("\nPRIMARIA (VA 151-300 > 0 y > P3-escaso):")
ok = 0
for s in range(5):
    a, b = out["P4-alga"][s]["va_intake"], out["P3-escaso"][s]["va_intake"]
    p = a is not None and a > 0 and a > b and out["P4-alga"][s]["epochs"] == 300
    ok += p; print(f"  s{s}: P4 {a:+.3f}  P3 {b:+.3f}  {'pasa' if p else 'no'}")
print(f"  -> {ok}/5")
for c in C:
    for s in range(5):
        rs = rows(c, s)
        print(c, s, "VA por prueba:", " ".join(f"{r['epoch']}:{r['va_intake']:+.2f}" for r in rs if isinstance(r.get('va_intake'), (int, float))))
    print(c, "examen e300:", [next((r.get('cap_patch_success') for r in rows(c, s) if r['epoch'] == 300), None) for s in range(5)],
          "ref:", [next((r.get('cap_patch_baseline_controls') for r in rows(c, s) if r['epoch'] == 300), None) for s in range(5)])
