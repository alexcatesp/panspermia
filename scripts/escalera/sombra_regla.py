"""Parte 6: R/S de novelty_added en 5001-5500 y actividad de Bedau-Packard. Solo observa."""
import glob, json, collections, numpy as np, pyarrow.parquet as pq
B='/mnt/d/Development/panspermia/runs/fase1d/%s/s%d/'
def nov(c,s):
    e,v=[],[]
    for f in sorted(glob.glob(B%(c,s)+'stats/*.parquet')):
        t=pq.read_table(f,columns=['epoch','novelty_added']).to_pydict(); e+=t['epoch']; v+=t['novelty_added']
    e=np.array(e); v=np.array(v,float); return e,v
def act(c,s):
    A=collections.Counter(); n=0
    for l in open(B%(c,s)+'clades.jsonl'):
        d=json.loads(l)
        if 5000<d['epoch']<=5500:
            n+=1
            for i,k in zip(d['ids'],d['counts']): A[i]+=k
    return A,n
out={}
for s in (30,31,32):
    r={}
    for c in ('sombra-real','sombra-neutral'):
        e,v=nov(c,s); m=(e>5000)&(e<=5500); r[c]=float(v[m].mean()); r['n_'+c]=int(m.sum())
    Ar,nr=act('sombra-real',s); An,nn=act('sombra-neutral',s)
    thr=float(np.percentile(list(An.values()),99)) if An else float('nan')
    r['R/S']=r['sombra-real']/r['sombra-neutral']
    r['umbral_p99']=thr; r['clados_real']=len(Ar); r['clados_neutral']=len(An)
    r['reales_sobre_umbral']=int(sum(1 for x in Ar.values() if x>thr))
    r['neutral_sobre_umbral']=int(sum(1 for x in An.values() if x>thr))
    r['epocas_clades']=(nr,nn); out[s]=r
    print(s,{k:(round(x,3) if isinstance(x,float) else x) for k,x in r.items()})
rs=[out[s]['R/S'] for s in out]
print('R/S',[round(x,2) for x in rs],'adaptativa(≥1,5 en 3/3):',all(x>=1.5 for x in rs),'deriva(≤1,2 en ≥2/3):',sum(x<=1.2 for x in rs)>=2)
json.dump(out,open('/mnt/d/Development/panspermia/runs/fase1d/_sombra_regla.json','w'),indent=1)
