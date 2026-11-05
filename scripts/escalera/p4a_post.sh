source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-p4/src
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd /tmp
echo "== empieza $(date '+%F %H:%M')"
taskset -c 0-7 python $S/p4a_genes.py 2>&1 | grep -v Warn
taskset -c 0-7 python $S/p4a_hunger.py $R/P4-alga --jsonl $R/_hambre.jsonl 2>&1 | grep -v Warn
echo "== termina $(date '+%F %H:%M')"
