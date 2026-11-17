# Apertura en un mundo que cambia (ADR-036; apertura.md, parte 2): ap-salto-C y ap-salto-Cbar, semillas 30–32, 2.000 épocas.
# 9 mundos × 2.000 épocas (~4 h cada uno): ap-C, ap-Cbar y ap-P0, semillas 30–32 intercaladas. Marca: apertura_salto_hecho.
R=/mnt/d/Development/panspermia/runs/fase1d
E=/mnt/d/Development/panspermia/scripts/escalera
source ~/.venvs/panspermia/bin/activate
export PYTHONPATH=/mnt/d/Development/panspermia-c/src
cd /mnt/d/Development/panspermia-c
for seed in 30 31 32; do
  for name in ap-salto-C ap-salto-Cbar; do
    for try in 1 2 3 4 5 6; do
      echo "== $name s$seed intento $try $(date '+%F %H:%M')"
      python -m panspermia.experiment sweep $E/apertura_salto_$seed.json --out $R --only $name >> $R/apertura_salto_mundos.log 2>&1
      grep -q '"final_population"\|"paused": true' $R/$name/s$seed/result.json 2>/dev/null && break
      sleep 120
    done
  done
done
touch $R/apertura_salto_hecho
echo "== termina $(date '+%F %H:%M')"
