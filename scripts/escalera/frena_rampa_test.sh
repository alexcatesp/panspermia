source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-frena
JAX_PLATFORMS=cpu PYTHONPATH=src taskset -c 0-7 python -m pytest -q tests/test_escalera.py -k "brake or gut" 2>&1 | tail -15
