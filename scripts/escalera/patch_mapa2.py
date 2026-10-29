import json
from pathlib import Path

P = Path("D:/Development/panspermia/docs/mapa.json")
m = json.loads(P.read_text(encoding="utf-8"))
arbol = [n for n in m["arbol"] if n["id"] != "P6"]
i = next(k for k, n in enumerate(arbol) if n["id"] == "P5") + 1
nuevos = [
    {"id": "P6si", "padre": "P5", "titulo": "Si en P5 aprender compensa: veneno que cambia en el tiempo",
     "corto": "✓ → veneno que cambia", "estado": "pendiente", "resultado": None,
     "anade": "el alga venenosa cambia con el tiempo (las preguntas de E1, ahora en un mundo limpio)",
     "texto": "Rama del sí (decisión del responsable, 18-10): se construye sobre el veneno. Después, la señal entre ellos y el resto de ingredientes, de uno en uno.",
     "ref": "ADR-014"},
    {"id": "P6no", "padre": "P5", "titulo": "Si en P5 aprender no compensa: + química",
     "corto": "✗ → + química", "estado": "pendiente", "resultado": None,
     "anade": "química (nutriente, toxina, feromona) sobre P5",
     "texto": "Rama del no (decisión del responsable, 18-10): lo visto en E1 vendría de otro ingrediente. Se añaden de uno en uno sobre P5, en el orden química → ataque → señal; el primero que haga aparecer el aprendizaje es el culpable. E1b-uniforme (todo junto) sirve de referencia.",
     "ref": "ADR-014"},
    {"id": "P7no", "padre": "P6no", "titulo": "Si sigue sin compensar: + ataque", "corto": "+ ataque",
     "estado": "pendiente", "resultado": None, "anade": "ataque y carroña", "ref": "ADR-014"},
    {"id": "P8no", "padre": "P7no", "titulo": "Si sigue sin compensar: + señal", "corto": "+ señal",
     "estado": "pendiente", "resultado": None, "anade": "señal entre bichos", "ref": "ADR-014"},
]
arbol[i:i] = nuevos
by = {n["id"]: n for n in arbol}
by["larga"]["padre"] = "P6si"
m["arbol"] = arbol
m["camino_principal"] = ["raiz", "escalera", "P0", "P1", "P2", "P3", "P4", "P5", "P6si", "larga", "fuga", "red", "robot"]
for n in arbol:
    n["principal"] = n["id"] in m["camino_principal"]
m["actualizado"] = "2026-10-18 19:10"
P.write_text(json.dumps(m, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
print("ok", len(arbol))
