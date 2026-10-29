source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
for wt in c bprima; do
  PYTHONPATH=/mnt/d/Development/panspermia-$wt/src python $S/bitid_bprima.py $S/bitid_$wt.npz /mnt/d/Development/panspermia-$wt 2>&1 | grep -v Warning | tail -2
done
python -c "import numpy as np; a=np.load('$S/bitid_c.npz'); b=np.load('$S/bitid_bprima.npz'); print({k: bool(np.array_equal(a[k], b[k])) for k in a}, 'rbar max', float(abs(a['rbar']).max()))"
