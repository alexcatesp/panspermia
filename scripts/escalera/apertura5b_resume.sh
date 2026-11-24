# Apertura parte 5b: ap4-largo (5.000 épocas), semillas 31 y 32. Marca: apertura5b_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
name=ap4-largo
for seed in 32; do
  for try in 1 2 3 4 5 6; do
    echo "== $name s$seed intento $try $(date '+%F %H:%M')"
    python -m panspermia.experiment sweep $E/apertura5_$seed.json --out $R --only $name >> $R/apertura5_mundos.log 2>&1
    grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
    sleep 120
  done
done
touch $R/apertura5b_hecho
echo "== termina $(date '+%F %H:%M')"
