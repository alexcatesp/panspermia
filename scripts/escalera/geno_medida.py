"""Parte 8: novedad GENÉTICA (CPU, solo observa). Para cada checkpoint, genomas de hasta 1.000 vivos
(muestra fija por semilla) como vector [W enmascarada, sesgo, cuerpo, vida, ocultas, aristas]; cada
rasgo se divide por max(desv. típica en el checkpoint de referencia, 0,05). Distancia = RMS sobre rasgos.
Medidas por checkpoint c frente a la población de referencia r:
  desp(c,r)  = media de la distancia al vecino más cercano de r (desplazamiento genético);
  div(c)     = media de la distancia al vecino más cercano dentro de c (diversidad interna);
  nuevo(c,r) = desp(c,r) / div(r)  (>1: genomas más lejos de r de lo que r lo está de sí misma)."""
import os; os.environ.setdefault('JAX_PLATFORMS','cpu')
import sys, gc, json, pathlib, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from geno_carga import carga
R='/mnt/d/Development/panspermia/runs/fase1d/'
N=1000
def vec(t, rng):
    a=np.asarray(t['alive']).astype(bool); idx=np.flatnonzero(a)
    if len(idx)>N: idx=np.sort(rng.choice(idx,N,replace=False))
    g=t['genome']; W=np.asarray(g['W'])[idx].astype(np.float32)*np.asarray(g['W_mask'])[idx]
    f=[W.reshape(len(idx),-1), np.asarray(g['bias'])[idx].astype(np.float32), np.asarray(g['body'])[idx].astype(np.float32),
       np.asarray(g['life'])[idx].astype(np.float32), np.asarray(g['hid_mask'])[idx].sum(1,keepdims=True).astype(np.float32),
       np.asarray(g['W_mask'])[idx].sum((1,2))[:,None].astype(np.float32)]
    return np.concatenate(f,1)
def nn(a,b,same=False):
    d=np.sqrt(np.maximum((a**2).sum(1)[:,None]+(b**2).sum(1)[None,:]-2*a@b.T,0)/a.shape[1])
    if same: np.fill_diagonal(d,np.inf)
    return d.min(1)
def pob(run,ep,seed,sc=None):
    t=carga(R+run,ep); v=vec(t,np.random.default_rng(seed)); del t; gc.collect(); return v
def medir(run,eps,ref_ep,seed,pop_ref=None):
    ref=pop_ref if pop_ref is not None else pob(run,ref_ep,seed)
    sc=np.maximum(ref.std(0),0.05); r=ref/sc; divr=float(nn(r,r,True).mean()); out=[]
    for e in eps:
        c=pob(run,e,seed)/sc
        d=float(nn(c,r).mean()); out.append(dict(epoca=e,desp=d,div=float(nn(c,c,True).mean()),nuevo=d/divr))
        print(run,e,{k:round(x,3) for k,x in out[-1].items() if k!='epoca'},flush=True)
    return out
if __name__=='__main__':
    modo=sys.argv[1]; res={}
    for s in (30,31,32):
        if modo=='sombra':   # real y neutral frente a la época 5000 de ap4-largo (mismo punto de partida)
            ref=pob('ap4-largo/s%d'%s,5000,s)
            for c in ('sombra-real','sombra-neutral'):
                res[f'{c} s{s}']=medir(f'{c}/s{s}',[5100,5200,5300,5400,5500],None,s,ref)
        else:                # ritmo de cambio de ap4-largo: cada muestra frente a la anterior (300 épocas antes)
            eps=list(range(200,5001,300)); out=[]; prev=pob('ap4-largo/s%d'%s,eps[0]-300 if eps[0]>300 else 100,s)
            for e in eps:
                cur=pob('ap4-largo/s%d'%s,e,s); sc=np.maximum(prev.std(0),0.05); r=prev/sc; c=cur/sc
                d=float(nn(c,r).mean()); dv=float(nn(r,r,True).mean()); out.append(dict(epoca=e,desp=d,div=dv,nuevo=d/dv))
                print('ap4-largo',s,e,{k:round(x,3) for k,x in out[-1].items() if k!='epoca'},flush=True); prev=cur
            res[f'ap4-largo s{s}']=out
    json.dump(res,open(R+f'_geno_{modo}.json','w'),indent=1)
