# Apertura parte 7, mundo rico (ADR-036): ap6-rico, semillas 30-32 x 2.000 épocas. Marca: apertura6_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
for seed in 30 31 32; do
  for name in ap6-rico; do
    for try in 1 2 3 4 5 6; do
      echo "== $name s$seed intento $try $(date '+%F %H:%M')"
      python -m panspermia.experiment sweep $E/apertura6_$seed.json --out $R --only $name >> $R/apertura6_mundos.log 2>&1
      grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
      sleep 120
    done
  done
done
touch $R/apertura6_hecho
echo "== termina $(date '+%F %H:%M')"
