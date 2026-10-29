source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-trazas
PYTHONPATH=src:tests JAX_PLATFORMS=cpu taskset -c 0-5 python - <<'PY'
import numpy as np, jax.numpy as jnp
import test_trazas as T
from panspermia import brain
p,q,trials,gap=2,1,300,7
ph=T._pheno(p,q,eta=0.05); rng=np.random.default_rng(0); cs=rng.random(trials)<0.5; dis=rng.random(trials*(gap+1))<0.5/(gap+1)
def learn(lam, mode):
    w,e,t=jnp.zeros((1,p,q)),jnp.zeros((1,p,q)),0
    for i in range(trials):
        for k in range(gap+1):
            pre=jnp.asarray([[1.0 if (k==0 and (cs[i] or mode=='pos')) else 0.0, 1.0 if dis[t] else 0.0]])
            if mode=='centrada': m=jnp.full((1,),0.5 if cs[i] else -0.5) if k==gap else jnp.zeros(1)
            else: m=jnp.ones(1) if k==gap else jnp.zeros(1)
            w,e=brain.plasticity_trace(ph,w,e,pre,jnp.ones((1,q)),m,lam); t+=1
    return np.round(np.asarray(w)[0,:,0],3)
for mode in ('centrada','pos'):
    print(mode,'con traza',learn(T.LAM,mode),'sin traza',learn(0.0,mode))
print('traza N=4096 MB', 4096*144*72*4/2**20)
PY
