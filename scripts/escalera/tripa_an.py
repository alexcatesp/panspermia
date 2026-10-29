"""La tripa (diseno v1.5): P4-alga-tripa frente a P4-alga-sin-tripa; contraste P3-escaso-tripa."""
import json
from pathlib import Path
R = Path("runs/fase1d")
def rows(c, s):
    return json.loads((R / c / f"s{s}" / "stats" / "summary.json").read_text(encoding="utf-8"))
def late(rs, k, a=151, b=300):
    v = [r[k] for r in rs if a <= r["epoch"] <= b and isinstance(r.get(k), (int, float))]
    return sum(v) / len(v) if v else None
keys = ["population", "lifespan_mean", "thrust_mean", "intake", "hidden_mean", "va_intake", "va_log_intake",
        "births", "mean_energy", "cap_patch_success", "mass_mean"]
C = ["P4-alga-tripa", "P4-alga-sin-tripa", "P4-alga", "P3-escaso-tripa", "P3-escaso"]
out = {}
for c in C:
    out[c] = []
    for s in range(5):
        rs = rows(c, s)
        d = {k: late(rs, k) for k in keys}
        d["epochs"] = len(rs)
        d["va_pos"] = sum(1 for r in rs if r["epoch"] > 0 and isinstance(r.get("va_intake"), (int, float)) and r["va_intake"] > 0)
        d["va_n"] = sum(1 for r in rs if isinstance(r.get("va_intake"), (int, float)))
        out[c].append(d)
for k in keys + ["epochs", "va_pos", "va_n"]:
    print(f"\n{k}")
    for c in C:
        print(f"  {c:18s}", " ".join("   -    " if x[k] is None else f"{x[k]:9.3f}" for x in out[c]))
(R / "_analisis_tripa.json").write_text(json.dumps(out, indent=1))
print("\nPRIMARIA (VA 151-300 de P4-alga-tripa > 0 y > P4-alga-sin-tripa):")
ok = 0
for s in range(5):
    a, b = out["P4-alga-tripa"][s]["va_intake"], out["P4-alga-sin-tripa"][s]["va_intake"]
    p = a is not None and a > 0 and a > b and out["P4-alga-tripa"][s]["epochs"] == 300
    ok += p; print(f"  s{s}: tripa {a:+.3f}  sin {b:+.3f}  {'pasa' if p else 'no'}")
print(f"  -> {ok}/5")
for c in C[:4]:
    for s in range(5):
        print(c, s, "VA:", " ".join(f"{r['epoch']}:{r['va_intake']:+.2f}" for r in rows(c, s) if isinstance(r.get('va_intake'), (int, float))))
