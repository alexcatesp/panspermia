source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu
cd /mnt/d/Development/panspermia-p4
PYTHONPATH=src taskset -c 0-7 python -m pytest -q tests/test_escalera.py -k "alga or jumps" 2>&1 | tail -15
