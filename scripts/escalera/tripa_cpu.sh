source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=src
cd /mnt/d/Development/panspermia-tripa
taskset -c 8-15 python -m pytest -q tests/test_escalera.py tests/test_units.py tests/test_phase0_acceptance.py -x 2>&1 | tail -15
