"""Sonda de hambre sobre P4-salto64: misma sonda, con la configuración de la cola (K_CUT 1,5; salto 64 u cada 1.000 pasos)."""
import runpy, sys
from panspermia import config as C
C.K_CUT = 1.5
C.FOOD_JUMP_PERIOD = 1000
C.FOOD_JUMP_DIST = 64.0
runpy.run_path(sys.argv[0].replace("p4s_hunger.py", "hunger_probe.py"), run_name="__main__")
