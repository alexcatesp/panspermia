source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
export JAX_PLATFORMS=cpu
cd /tmp
echo "== empieza $(date '+%F %H:%M')"
export PYTHONPATH=/mnt/d/Development/panspermia-tripa/src
for c in P4-alga-tripa P4-alga-sin-tripa P3-escaso-tripa; do taskset -c 0-7 python $S/genes_any.py $c 2>&1 | grep -v Warn; done
echo "== suelo de ruido $(date '+%F %H:%M')"
PYTHONPATH=$PYTHONPATH:$S taskset -c 0-7 python $S/diag_aprender.py $R/P4-alga-tripa --seeds 3 1 --parts B --config ALGA_SWAP_PERIOD=2000 --jsonl $R/_diag_aprender.jsonl 2>&1 | grep -v Warn
taskset -c 0-7 python $S/p4a_hunger.py $R/P4-alga-tripa --jsonl $R/_hambre.jsonl 2>&1 | grep -v Warn
taskset -c 0-7 python $S/p4a_hunger.py $R/P4-alga-sin-tripa --jsonl $R/_hambre.jsonl 2>&1 | grep -v Warn
echo "== P4-salto64 $(date '+%F %H:%M')"
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
taskset -c 0-7 python $S/genes_any.py P4-salto64 2>&1 | grep -v Warn
taskset -c 0-7 python $S/p4s_hunger.py $R/P4-salto64 --jsonl $R/_hambre.jsonl 2>&1 | grep -v Warn
echo "== termina $(date '+%F %H:%M')"
