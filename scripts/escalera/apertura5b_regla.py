"""Parte 5b: ap4-largo (5.000 épocas), semillas 30, 31 y 32. Solo observa."""
import glob, numpy as np, pyarrow.parquet as pq
R='/mnt/d/Development/panspermia/runs/fase1d/ap4-largo/s%d/stats/'
for s in (30,31,32):
    e,v=[],[]
    for f in sorted(glob.glob(R%s+'*.parquet')):
        t=pq.read_table(f,columns=['epoch','novelty_added']).to_pydict(); e+=t['epoch']; v+=t['novelty_added']
    e=np.array(e); o=np.argsort(e); e=e[o]; v=np.array(v,float)[o]
    m=lambda a,z: float(v[(e>a)&(e<=z)].mean())
    E=m(100,300); T=m(1500,2000); T5=m(4500,5000)
    print(f's{s} épocas',int(e.max()),'E',round(E,2),'T',round(T,2),'T5',round(T5,2),'T5/T',round(T5/T,2),'T5/E',round(T5/E,2))
