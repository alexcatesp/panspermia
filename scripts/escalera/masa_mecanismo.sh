source ~/.venvs/panspermia/bin/activate
export JAX_PLATFORMS=cpu PYTHONPATH=/mnt/d/Development/panspermia-p4/src
cd /tmp
taskset -c 0-7 python /mnt/c/Users/<usuario>/AppData/Local/Temp/claude/D--Development-panspermia/ddea0d1c-f251-40d2-8e99-9e07c65f2199/scratchpad/masa_mecanismo.py 2>&1 | grep -v Warn
