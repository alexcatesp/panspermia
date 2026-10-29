"""Sonda de hambre sobre P4-alga: misma sonda, con el cambio de alga de la cola (ALGA_SWAP_PERIOD 2000)."""
import runpy, sys
from panspermia import config as C
C.ALGA_SWAP_PERIOD = 2000
sys.argv = [sys.argv[0]] + sys.argv[1:]
runpy.run_path(sys.argv[0].replace("p4a_hunger.py", "hunger_probe.py"), run_name="__main__")
