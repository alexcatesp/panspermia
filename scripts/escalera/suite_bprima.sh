source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-bprima
export PYTHONPATH=src
echo "== suite b′ $(date '+%F %H:%M')"
python -m pytest -q 2>&1 | grep -v Warning | tail -8
echo "== termina $(date '+%F %H:%M')"
touch /mnt/d/Development/panspermia/runs/fase1d/suite_bprima_hecha
