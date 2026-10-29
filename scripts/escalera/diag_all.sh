source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-p4/src
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
O=$R/_diag_aprender.jsonl
cd /tmp
echo "== empieza $(date '+%F %H:%M')"
taskset -c 0-7 python $S/diag_aprender.py $R/P4-alga --config ALGA_SWAP_PERIOD=2000 --jsonl $O 2>&1 | grep -v Warn
taskset -c 0-7 python $S/diag_aprender.py $R/P3-escaso --jsonl $O 2>&1 | grep -v Warn
taskset -c 0-7 python $S/diag_aprender.py $R/P3-disperso --config K_CUT=1.5 --jsonl $O 2>&1 | grep -v Warn
echo "== termina $(date '+%F %H:%M')"
