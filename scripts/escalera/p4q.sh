source ~/.venvs/panspermia/bin/activate
cd /mnt/d/Development/panspermia-p4
JAX_PLATFORMS=cpu PYTHONPATH=src python -c "
from pathlib import Path; from panspermia.experiment import load_queue
for s in load_queue(Path('/mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad/p4cal.json')): print(s['name'], s.get('config'), s.get('env'))"
