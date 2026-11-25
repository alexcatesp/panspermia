"""Carga el genoma de los vivos de un checkpoint (CPU, solo lectura)."""
import os; os.environ.setdefault('JAX_PLATFORMS','cpu')
import numpy as np, orbax.checkpoint as ocp, pathlib
def carga(run, ep):
    p=pathlib.Path(run).resolve()/'checkpoints'/str(ep)
    tree=ocp.PyTreeCheckpointer().restore(p/'default')
    return tree
if __name__=='__main__':
    import sys; t=carga(sys.argv[1],int(sys.argv[2]))
    def walk(d,pre=''):
        for k,v in d.items():
            if isinstance(v,dict): walk(v,pre+k+'.')
            else: print(pre+k,getattr(v,'shape',None),getattr(v,'dtype',None))
    walk(t)
