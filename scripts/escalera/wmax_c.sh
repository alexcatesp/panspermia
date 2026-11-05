source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-c/src JAX_PLATFORMS=cpu
R=/mnt/d/Development/panspermia/runs/fase1d
cd /mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
BASE="ALGA_PER_AGENT=1 ALGA_PATCH_FAMILIES=1 K_CUT=1.7 EAT_MOVE_FACTOR=0 EAT_MOVE_RAMP_STEPS=100000 K_MEAN_RAMP_STEPS=100000 K_MEAN_RAMP_FROM=2 POISON_FACTOR=2.5 POISON_RAMP_STEPS=100000 POISON_DELAY=0 DELTA_K=8.65 DELTA_TAU=50"
python wmax.py $R/P5-inmediato-C --seeds 0 1 2 --epoch 300 --config $BASE DELTA_ON=1 --jsonl $R/_wmax_c.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
python wmax.py $R/P5-inmediato-Cbar --seeds 0 1 2 --epoch 300 --config $BASE DELTA_ON=2 --jsonl $R/_wmax_c.jsonl 2>&1 | grep -E "^\{|Traceback|Error"
