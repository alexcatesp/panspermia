import json
for s in [1,2,3,4]:
    rows=json.load(open(f"runs/phase1/s{s}/stats/summary.json"))
    keys=[k for k in rows[-1] if "patch" in k or "cap" in k or "ring" in k]
    late=[r for r in rows if r["epoch"]>400]
    print(s, len(rows), keys)
    for k in keys:
        v=[r[k] for r in rows if r.get(k) is not None and r["epoch"]>100]
        print("  ",k, [round(x,3) for x in v][-8:])
    for c in ["population","hidden_mean","attack_gene_mean","comm_mi","toxic_intake_frac"]:
        v=[r[c] for r in late if r.get(c) is not None]
        if v: print("  ",c, round(sum(v)/len(v),3))
