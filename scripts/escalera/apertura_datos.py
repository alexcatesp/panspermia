"""Apertura evolutiva, primer vistazo en CPU con datos ya generados (auditoría 15-11, rec. 3; ADR-036; solo observa).
Por mundo y por tramo de épocas (1–100, 101–200, 201–300): media de novelty_added, bp_new_activity y groups_k.
Mediana entre semillas. Lo que importa es la razón tardío/temprano frente al nulo P0 (sin selección).
Uso: python apertura_datos.py run1 run2 ... > salida.json"""
import glob, json, sys
import numpy as np, pyarrow.parquet as pq
R = '/mnt/d/Development/panspermia/runs/fase1d/'
COLS = ['epoch', 'novelty_added', 'bp_new_activity', 'groups_k', 'population', 'clades_alive']
def world(run, s):
    fs = sorted(glob.glob(f'{R}{run}/s{s}/stats/*.parquet'))
    if not fs: return None
    cols = {}
    for f in fs:
        tb = pq.read_table(f, columns=[c for c in COLS if c in pq.read_schema(f).names]).to_pydict()
        for k, v in tb.items(): cols.setdefault(k, []).extend(v)
    o = np.argsort(cols['epoch'])
    return {k: np.asarray(v, float)[o] for k, v in cols.items()}
out = {}
for run in sys.argv[1:]:
    rows = []
    for s in range(10):
        d = world(run, s)
        if d is None or len(d['epoch']) < 300: continue
        r = {}
        for k in ('novelty_added', 'bp_new_activity', 'groups_k', 'clades_alive'):
            if k not in d: continue
            e = d['epoch']; v = d[k]
            r[k] = [float(v[(e > a) & (e <= a + 100)].mean()) for a in (0, 100, 200)]
        rows.append(r)
    if rows:
        out[run] = {'n': len(rows), **{k: [round(float(np.median([r[k][i] for r in rows])), 4) for i in range(3)] for k in rows[0]}}
print(json.dumps(out, ensure_ascii=False, indent=1))
