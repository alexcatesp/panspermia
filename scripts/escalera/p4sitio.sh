# P4-salto64 (diseno v1.4): 5 mundos × 300 épocas. Mismo código con el que pasó la suite (15:43).
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-p4
echo "== P4-salto64 empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/p4sitio.json --out $R >> $R/p4sitio.log 2>&1 && touch $R/p4sitio_hecho
echo "== P4-salto64 termina $(date '+%F %H:%M')"
