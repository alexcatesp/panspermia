source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu
for b in coste p4; do for m in edad energia; do
  (cd /tmp && PYTHONPATH=/mnt/d/Development/panspermia-$b/src taskset -c 0-7 python /mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad/bitid2.py $b $m 2>&1 | grep -v Warning)
done; done
cd /mnt/d/Development/panspermia-p4
PYTHONPATH=src taskset -c 0-7 python -m pytest -q tests/test_escalera.py tests/test_units.py 2>&1 | tail -15
