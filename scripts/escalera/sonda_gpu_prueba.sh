source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
cd $S; export PYTHONPATH=/mnt/d/Development/panspermia-masa/src
/usr/bin/time -f "seg %e RSS_MB %M" python sonda_mixta.py /mnt/d/Development/panspermia/runs/fase1d/P4-salto64 --seeds 1 --steps 300 --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 --jsonl $S/_prueba_gpu.jsonl 2>&1 | tail -3
