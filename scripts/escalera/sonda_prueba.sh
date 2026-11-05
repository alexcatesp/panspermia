source ~/.venvs/panspermia/bin/activate
S=/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
cd $S
free -g | head -2
JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-masa/src /usr/bin/time -f "seg %e  RSS_MB %M" taskset -c 0-7 \
  python sonda_mixta.py /mnt/d/Development/panspermia/runs/fase1d/P4-salto64-grande --seeds 0 --steps 100 \
  --config K_CUT=1.5 FOOD_JUMP_PERIOD=1000 FOOD_JUMP_DIST=64 BODY_RADIUS_FIXED=6.6 --jsonl $S/_prueba_mixta.jsonl 2>&1 | tail -5
python -c "
import json; r=[json.loads(l) for l in open('$S/_prueba_mixta.jsonl')][-1]
print(r['plastico']['pasos_bicho'], r['congelado']['pasos_bicho']); print(r['plastico']['pasos_por_edad'])
print({k:(v.get('n'), v.get('frac_cambia')) for k,v in r['pesos'].items()})"
