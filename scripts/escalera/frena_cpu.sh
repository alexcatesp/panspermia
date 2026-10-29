source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-frena
export JAX_PLATFORMS=cpu PYTHONPATH=src
taskset -c 0-7 python -m pytest -q tests/test_escalera.py -k "eating_brakes or gut_sense or alga_swap" 2>&1 | tail -15
