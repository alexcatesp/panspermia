# Apertura parte 5: ap4 a 5.000 épocas (semilla 30, 1 mundo). Marca: apertura5_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
name=ap4-largo; seed=30
for try in 1 2 3 4 5 6; do
  echo "== $name s$seed intento $try $(date '+%F %H:%M')"
  python -m panspermia.experiment sweep $E/apertura5_$seed.json --out $R --only $name >> $R/apertura5_mundos.log 2>&1
  grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
  sleep 120
done
touch $R/apertura5_hecho
echo "== termina $(date '+%F %H:%M')"
