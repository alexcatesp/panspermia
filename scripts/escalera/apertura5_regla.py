"""Parte 5: ap4-largo (5.000 épocas, s30). Solo observa."""
import glob, numpy as np, pyarrow.parquet as pq
R='/mnt/d/Development/panspermia/runs/fase1d/ap4-largo/s30/stats/'
e,v,g=[],[],[]
for f in sorted(glob.glob(R+'*.parquet')):
    t=pq.read_table(f,columns=['epoch','novelty_added','bp_new_activity']).to_pydict(); e+=t['epoch']; v+=t['novelty_added']; g+=t['bp_new_activity']
e=np.array(e); o=np.argsort(e); e=e[o]; v=np.array(v,float)[o]; g=np.array(g,float)[o]
m=lambda x,a,z: float(x[(e>a)&(e<=z)].mean())
E=m(v,100,300); T=m(v,1500,2000); T5=m(v,4500,5000)
print('épocas',int(e.max()),'E',round(E,2),'T',round(T,2),'T5',round(T5,2),'T5/T',round(T5/T,2),'T5/E',round(T5/E,2))
for a in range(0,5000,500): print(a+1,'-',a+500,round(m(v,a,a+500),2),'bp',round(m(g,a,a+500),2))
