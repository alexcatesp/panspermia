"""Aplica la regla de docs/escalera/apertura.md a los mundos ap-* ya terminados (CPU, solo observa)."""
import glob, json, numpy as np, pyarrow.parquet as pq
R = '/mnt/d/Development/panspermia/runs/fase1d/'
def ser(run, s, col):
    fs = sorted(glob.glob(f'{R}{run}/s{s}/stats/*.parquet')); e, v = [], []
    for f in fs:
        t = pq.read_table(f, columns=['epoch', col]).to_pydict(); e += t['epoch']; v += t[col]
    e = np.array(e); v = np.array(v, float); o = np.argsort(e); return e[o], v[o]
res = {}
for run in ("ap2-salto","ap2-salto-fijo"):
    for s in (30, 31, 32, 33, 34, 35):
        if not glob.glob(f'{R}{run}/s{s}/result.json'): continue
        e, v = ser(run, s, 'novelty_added'); _, b = ser(run, s, 'bp_new_activity'); _, g = ser(run, s, 'clades_alive')
        m = lambda x, a, z: float(x[(e > a) & (e <= z)].mean())
        res[f'{run} s{s}'] = {'E_101_300': round(m(v, 100, 300), 2), 'M_701_1000': round(m(v, 700, 1000), 2), 'T_1501_2000': round(m(v, 1500, 2000), 2),
                              'T/E': round(m(v, 1500, 2000) / m(v, 100, 300), 2), 'bp_T': round(m(b, 1500, 2000), 2), 'clados_T': round(m(g, 1500, 2000), 1)}
for k, x in res.items(): print(k, json.dumps(x))

for run in ('ap2-salto','ap2-salto-fijo'):
    v=[res[f'{run} s{s}']['T_1501_2000'] for s in range(30,36) if f'{run} s{s}' in res]
    print(run,'T',v,'mediana',float(np.median(v)))
ps=[(res[f'ap2-salto s{s}']['T_1501_2000'],res[f'ap2-salto-fijo s{s}']['T_1501_2000']) for s in range(30,36)]
gana=sum(a>b for a,b in ps); ms=np.median([a for a,_ in ps]); mf=np.median([b for _,b in ps])
print('pares gana salto:',gana,'/6 | mediana',ms,'vs',mf,'x',round(ms/mf,2),'| CONFIRMA:',ms>1.25*mf and gana>=5)
print('T/E salto:',[res[f'ap2-salto s{s}']['T/E'] for s in range(30,36)])
