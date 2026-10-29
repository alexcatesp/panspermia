source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-veneno
PYTHONPATH=src JAX_PLATFORMS=cpu taskset -c 0-5 python -m pytest -q -x tests/test_escalera.py -k "poison or alga_per_agent or patch_families" 2>&1 | tail -15
