import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "con selección conserva las aristas | ⚖ decidir |",
    "con selección conserva las aristas. **Responsable (20-10, 07:10): neutral corregida** (añadir y quitar equilibrados; se comprueba en P0 en la integración) | ✅ neutral corregida |")
sub(F, "Hecho: el de neuronas no limita con ninguna física; el de la CPPN sí (8–34 %) | ⚖ tras A2 |",
    "Hecho: el de neuronas no limita con ninguna física; el de la CPPN sí (8–34 %), salvo con la CPPN neutral | ✅ se mantiene (con A1 y A2 neutrales nadie lo toca; vigilarlo en P2) |")
sub(F, "- **Lo que P1 no puede juzgar:** si una receta más pequeña limita construir cerebros complejos cuando compensa (P2 en adelante).\n",
    "- **Lo que P1 no puede juzgar:** si una receta más pequeña limita construir cerebros complejos cuando compensa (P2 en adelante).\n"
    "- **Bibliografía** (`docs/bibliografia/escalera/README.md`, §11): el inflado sin ganancia es un fallo conocido de los operadores (soule1998removal, langdon1998bloat). De los remedios clásicos (coste por tamaño, operadores de tamaño neutro, igualación de operadores), el que encaja con los principios es el de **operadores equilibrados** (langdon2000sizefair): la misma hipótesis nula que en A1.\n"
    "- **Decisión del responsable (07:10):** CPPN **neutral corregida**: añadir y quitar aristas equilibrados, contando las que arrastra quitar un nodo, para que el tamaño esperado no cambie por sí solo. Se implementa en la rama de integración y se comprueba en P0 (5 mundos) antes de P2. Con A1 y A2 neutrales, el techo (A5) no limita; se vigila en P2. Pagar por la receta (soule1998parsimony, lynch2015bioenergetic) queda de reserva si en P2 se inflara sin motivo.\n")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 07:06–07:10 · A2 y A5 decididos

- **Pregunta del responsable:** «¿A qué apunta la bibliografía?». Respuesta (`docs/bibliografia/escalera/README.md`, §11, 5 referencias nuevas comprobadas en Crossref): el inflado sin ganancia es un sesgo de los operadores; el remedio que respeta los principios son los operadores de tamaño neutro (langdon2000sizefair). La igualación de operadores (dignum2008equalisation) filtra hijos por tamaño, así que sería una métrica externa decidiendo; el coste por tamaño (soule1998parsimony) añadiría una ley física nueva.
- **Decisión del responsable (07:10):** CPPN **neutral corregida** (añadir y quitar aristas equilibrados, contando las que arrastra quitar un nodo). Se implementa en la rama de integración y se comprueba en P0 antes de P2. El techo (A5) se mantiene: con A1 y A2 neutrales nadie lo toca; se vigila en P2.
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-A2":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] = n["texto"].replace(" Decide el responsable.", " Decisión (20-10, 07:10): neutral corregida (añadir y quitar equilibrados), comprobada en P0 en la integración.")
        if n.get("id") == "p0f-A5":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] += " Decisión (20-10, 07:10): se mantiene; con A1 y A2 neutrales nadie lo toca. Vigilarlo en P2."
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m); m["actualizado"] = "2026-10-20 07:10"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
C = Path("docs/caminos.md"); s = C.read_text(encoding="utf-8")
anchor = "| Tasas de mutación como gen"
i = s.index(anchor)
s = s[:i] + ("| Mutación de la CPPN de siempre (añadir 5 %, quitar 2 %, dividir 3 %, quitar nodo 1 %) | Descartado | Se infla sin selección (P0: 10–13 nodos) y también con ella, porque la receta no paga peaje (P1: hasta 12 de 18; en el techo con tasas fijas) | — (sustituida por la neutral corregida) | `docs/escalera/p0_factores.md` (A2) |\n"
             "| Pagar energía por el tamaño de la CPPN (presión de parsimonia) | Aparcado | No probado; añadiría una ley física nueva | Si en P2 la receta se inflara sin motivo con la física neutral corregida | `docs/bibliografia/escalera/README.md` §11 |\n") + s[i:]
C.write_text(s, encoding="utf-8", newline="\n")
print("ok")
