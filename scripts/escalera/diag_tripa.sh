source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-tripa/src:$S
R=/mnt/d/Development/panspermia/runs/fase1d
O=$R/_diag_tripa.jsonl
cd /tmp
echo "== empieza $(date '+%F %H:%M')"
taskset -c 0-7 python $S/diag_tripa.py $R/P4-alga-tripa --config ALGA_SWAP_PERIOD=2000 --jsonl $O 2>&1 | grep -v Warn
taskset -c 0-7 python $S/diag_tripa.py $R/P4-alga-sin-tripa --config ALGA_SWAP_PERIOD=2000 --jsonl $O 2>&1 | grep -v Warn
taskset -c 0-7 python $S/diag_tripa.py $R/P3-escaso-tripa --jsonl $O 2>&1 | grep -v Warn
echo "== termina $(date '+%F %H:%M')"
