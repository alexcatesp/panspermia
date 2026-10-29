cd /mnt/d/Development/panspermia/runs/fase1d/P4-alga-tripa-frena-rampa/s4/stats
ls | head
python3 - <<'EOF'
import json, glob, pandas as pd
fs = sorted(glob.glob("*.parquet")) or sorted(glob.glob("*.jsonl"))
print(fs[:3])
if fs[0].endswith(".parquet"):
    df = pd.concat([pd.read_parquet(f) for f in fs])
else:
    df = pd.DataFrame([json.loads(l) for f in fs for l in open(f)])
cols = [c for c in ("epoch", "population", "population_min", "births", "hidden_mean") if c in df.columns]
print(df[(df.epoch >= 110) & (df.epoch <= 135)][cols].to_string())
EOF
