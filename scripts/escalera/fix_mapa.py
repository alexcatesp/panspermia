import json
from pathlib import Path
p = Path("docs/mapa.json"); m = json.loads(p.read_text(encoding="utf-8"))
parent = {"f1": "f0", "larga": "E9", "larga-sin": "larga", "fuga": "larga"}
for n in m["arbol"]:
    if n["id"] in parent: n["padre"] = parent[n["id"]]
m["camino_principal"] = ["raiz", "f0", "f1", "f1-aprender", "f1b", "f1d", "E0", "veneno05", "E0b", "E1",
                         "recompensa", "E9", "larga", "fuga", "red", "robot"]
for n in m["arbol"]:
    n["principal"] = n["id"] in m["camino_principal"]
ids = {n["id"] for n in m["arbol"]}
assert all(n["padre"] is None or n["padre"] in ids for n in m["arbol"])
p.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
print("ok")
