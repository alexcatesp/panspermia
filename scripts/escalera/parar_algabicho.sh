R=/mnt/d/Development/panspermia/runs/fase1d
pkill -f scratchpad/algabicho.sh
pkill -f 'experiment sweep experiments/fase1d/algabicho.json'
sleep 2
pkill -f 'experiment run experiments/fase1d/algabicho.json'
sleep 3
pgrep -af 'algabicho|experiment' | grep -v pgrep || echo "nada corriendo"
cd $R
mv P4-alga-bicho-frena-rampa _P4-alga-bicho-k3804-parado
mv _calAlgaBicho _calAlgaBicho-k3804
echo "== parado por el tope (responsable) $(date '+%F %H:%M')" >> algabicho_cadena.log
ls -d *lga*icho* _P4-alga-bicho* 2>/dev/null
date
