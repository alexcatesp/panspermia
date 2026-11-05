source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
R=/mnt/d/Development/panspermia/runs/fase1d
cd $S
PYTHONPATH=/mnt/d/Development/panspermia-frena/src /usr/bin/time -f "seg %e RSS_MB %M" python madura.py $R/P4-alga-tripa-frena-rampa --seeds 8 --rear 200 --test 500 \
  --config ALGA_SWAP_PERIOD=2000 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 --jsonl $S/_madura_prueba.jsonl 2>&1 | grep -E "^\{|seg|Error|Traceback|error" | tail -8
