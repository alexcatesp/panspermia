import glob, json
import pyarrow.parquet as pq
R = "/mnt/d/Development/panspermia/runs/fase1d/_calAlgaBicho2"
for s in (0, 1, 2):
    try:
        r = json.load(open(f"{R}/s{s}/result.json"))
    except FileNotFoundError:
        r = None
    rows = [x for f in sorted(glob.glob(f"{R}/s{s}/stats/*.parquet"))
            for x in pq.read_table(f, columns=["epoch", "population", "population_min", "births", "mean_energy", "reinjected"]).to_pylist()]
    print(s, r)
    for x in rows:
        if x["epoch"] % 5 == 0 or x["epoch"] == rows[-1]["epoch"]:
            print("   ", x)
