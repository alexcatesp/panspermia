source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-p4/src
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd /tmp
date '+%T'
taskset -c 0-7 python $S/diag_aprender.py $R/P4-alga --config ALGA_SWAP_PERIOD=2000 --seeds 1 --parts AC --jsonl $S/diag_test.jsonl 2>&1 | grep -v Warn
date '+%T'
