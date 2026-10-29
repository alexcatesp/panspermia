# (4.ª vez, 23-10 13:45: la cadena murió a las 12:17 al cerrarse la sesión de Claude; solo masa.json, que salta lo hecho
# y reanuda P4-salto64-grande s1 desde el checkpoint 200. Lanzado con setsid/nohup para no depender de la sesión.)
R=/mnt/d/Development/panspermia/runs/fase1d
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=src
cd /mnt/d/Development/panspermia-masa
echo "== masa reanuda $(date '+%F %H:%M')"
python -m panspermia.experiment sweep experiments/fase1d/masa.json --out $R >> $R/masa.log 2>&1 && touch $R/masa_hecho
echo "== masa termina $(date '+%F %H:%M')"
