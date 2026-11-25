"""Parte 7 (mundo rico): T/E y comparación con ap4-ataque-senal, semillas 30-32. Solo observa."""
import glob, json, numpy as np, pyarrow.parquet as pq
R='/mnt/d/Development/panspermia/runs/fase1d/'
def ser(run,s,col='novelty_added'):
    e,v=[],[]
    for f in sorted(glob.glob(f'{R}{run}/s{s}/stats/*.parquet')):
        t=pq.read_table(f,columns=['epoch',col]).to_pydict(); e+=t['epoch']; v+=t[col]
    e=np.array(e); v=np.array(v,float); o=np.argsort(e); return e[o],v[o]
m=lambda e,v,a,z: float(v[(e>a)&(e<=z)].mean())
res={}
for run in ('ap6-rico','ap4-ataque-senal'):
    for s in (30,31,32):
        if not glob.glob(f'{R}{run}/s{s}/result.json'): continue
        e,v=ser(run,s); E=m(e,v,100,300); T=m(e,v,1500,2000)
        res[(run,s)]=dict(E=E,T=T,TE=T/E,ext=json.load(open(f'{R}{run}/s{s}/result.json')).get('extinct_at'))
        print(run,s,{k:(round(x,3) if isinstance(x,float) else x) for k,x in res[(run,s)].items()})
r=[res.get(('ap6-rico',s)) for s in (30,31,32)]; b=[res.get(('ap4-ataque-senal',s)) for s in (30,31,32)]
if all(r):
    print('abierto (T/E>=0,5 en 3/3):',all(x['TE']>=0.5 for x in r))
    mr=np.median([x['T'] for x in r]); mb=np.median([x['T'] for x in b])
    print('mediana T rico',round(mr,2),'ap4',round(mb,2),'cociente',round(mr/mb,2),'rico>ap4 en',sum(x['T']>y['T'] for x,y in zip(r,b)),'/3')
