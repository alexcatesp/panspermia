"""¿Sigue moviéndose algo al final? (apertura, CPU, solo observa). Por variable y mundo: cambio entre las épocas 1501–1750 y 1751–2000
en unidades de la desviación típica de la época dentro de cada tramo (z); mediana de |z| entre las 3 semillas por condición."""
import glob, numpy as np, pyarrow.parquet as pq
R = '/mnt/d/Development/panspermia/runs/fase1d/'
VARS = ['desc_speed','desc_turn','desc_intake','desc_dispersion','desc_aggregation','desc_repro_age','hidden_mean','synapses_mean','genome_distance','lifespan_mean','mass_mean','max_thrust_mean','population','generation_mean','clades_alive']
def cols(run, s):
    out = {}
    for f in sorted(glob.glob(f'{R}{run}/s{s}/stats/*.parquet')):
        for k, v in pq.read_table(f).to_pydict().items():
            if k in VARS + ['epoch']: out.setdefault(k, []).extend(v)
    o = np.argsort(out['epoch']); return {k: np.asarray(v, float)[o] for k, v in out.items()}
for run in ('ap-C', 'ap-Cbar', 'ap-P0'):
    z = {k: [] for k in VARS}
    for s in (30, 31, 32):
        d = cols(run, s); e = d['epoch']
        a = (e > 1500) & (e <= 1750); b = (e > 1750) & (e <= 2000)
        for k in VARS:
            if k in d:
                sd = np.sqrt((d[k][a].var() + d[k][b].var()) / 2) or 1e-9
                z[k].append((d[k][b].mean() - d[k][a].mean()) / sd * np.sqrt(125))  # z de la diferencia de medias
    print(run, {k: round(float(np.median(np.abs(v))), 1) for k, v in z.items() if v}, flush=True)
