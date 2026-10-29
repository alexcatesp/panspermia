import json
from pathlib import Path

p = Path("/mnt/d/Development/panspermia/docs/mapa.json")
m = json.loads(p.read_text(encoding="utf-8"))
m["actualizado"] = "2026-10-25 09:10"
n = next(x for x in m["arbol"] if x["id"] == "P4atf")
n["texto"] += (" Diagnóstico (25-10, 09:06; scratchpad/madura.py): sobre todo es maduración. Criados desde el cerebro de recién nacido sin comida, los bichos rinden casi"
               " como criados con comida (M mediana 0,84 con freno; 0,76–0,92 en las cuatro condiciones; M ≥ 0,7 en 19 de 27 mundos). La experiencia con la comida pesa en 8 de 27.")
b = next(x for x in m["arbol"] if x["id"] == "P4atfb")
b["texto"] += (" El diagnóstico de maduración (25-10) lo apoya: lo que hoy se aprende en vida es sobre todo maduración; con el alga sorteada para cada bicho, solo la experiencia"
               " dice qué comer (la madurez no basta), y M debería bajar.")
p.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
print("ok")
