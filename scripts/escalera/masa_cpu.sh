source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu
S=/mnt/c/Users/aleja/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad
cd /tmp
for w in p4 masa; do PYTHONPATH=/mnt/d/Development/panspermia-$w/src taskset -c 8-15 python $S/bitid_masa.py $w energia 2>&1 | grep -v Warn; done
cd /mnt/d/Development/panspermia-masa
PYTHONPATH=src taskset -c 8-15 python -m pytest -q tests/test_escalera.py -k "fixed or alga or jump" 2>&1 | tail -3
PYTHONPATH=src python -m panspermia.experiment check experiments/fase1d/masa.json
PYTHONPATH=src python -m panspermia.experiment check experiments/fase1d/masa_e50.json
