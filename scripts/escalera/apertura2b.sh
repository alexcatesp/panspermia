# Réplica de la parte 2 (ADR-036): ap2-salto y ap2-salto-fijo, semillas 33-35. Marca: apertura2b_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /mnt/d/Development/panspermia-p4
for seed in 33 34 35; do
  for name in ap2-salto ap2-salto-fijo; do
    for try in 1 2 3 4 5 6; do
      echo "== $name s$seed intento $try $(date '+%F %H:%M')"
      python -m panspermia.experiment sweep $E/apertura2_$seed.json --out $R --only $name >> $R/apertura2b_mundos.log 2>&1
      grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
      sleep 120
    done
  done
done
touch $R/apertura2b_hecho
echo "== termina $(date '+%F %H:%M')"
