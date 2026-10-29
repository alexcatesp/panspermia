# P3-disperso (misma comida que P3-escaso, en el 9 % del suelo), 5 mundos, con el examen sin química (ADR-021).
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-buscar
# Una sola carga pesada en la GPU: espera a que termine la calibración del coste.
while pgrep -f "p3ccal.json" > /dev/null; do sleep 60; done
echo "== empieza $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/p3disperso.json --out $R --only P3-disperso >> $R/p3disperso.log 2>&1
echo "== termina $(date '+%F %H:%M')"
touch $R/p3disperso_hecho
