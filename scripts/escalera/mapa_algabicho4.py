import json
from pathlib import Path
p = Path("/mnt/d/Development/panspermia/docs/mapa.json")
m = json.loads(p.read_text(encoding="utf-8"))
m["actualizado"] = "2026-10-25 14:25"
b = next(x for x in m["arbol"] if x["id"] == "P4atfb")
b["texto"] += (" Con la mitad de algas se extinguen al arrancar (2/3). Responsable: rampa de comida del doble a la mitad en 100 épocas (sustrato 3.4.0, diseno v2.2)."
               " Suite, calibración y 10 mundos desde las 14:25 (scratchpad/algabicho3.sh); fin hacia las 21:30.")
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
