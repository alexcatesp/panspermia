source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-algabicho
JAX_PLATFORMS=cpu PYTHONPATH=src taskset -c 0-7 python -m pytest -q tests/test_escalera.py tests/test_phase1d.py -k "ramp or alga or gut or brake or sparse or jump or config or experiment" 2>&1 | tail -15
