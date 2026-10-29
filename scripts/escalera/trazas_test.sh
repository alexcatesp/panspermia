source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-trazas
PYTHONPATH=src JAX_PLATFORMS=cpu taskset -c 0-5 /usr/bin/time -v python -m pytest -q -x tests/test_trazas.py tests/test_units.py -k "trace or delayed or conditioning or bounded or plasticity" 2>&1 | grep -E "passed|failed|Error|assert|Maximum resident|^E " | head -30
