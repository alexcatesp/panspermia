source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-coste/src
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd /tmp
echo "== empieza $(date '+%F %H:%M')"
for c in 5; do
  taskset -c 0-7 python $S/p3c${c}_genes.py 2>&1 | grep -v Warn
  taskset -c 0-7 python $S/hunger_probe.py $R/P3-coste$c --jsonl $R/_hambre.jsonl 2>&1 | grep -v Warn
done
echo "== termina $(date '+%F %H:%M')"
