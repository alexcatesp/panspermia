import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "El juicio necesita P1 | 📋 análisis de P0 + prueba en P1 |",
    "El juicio necesita P1. P1 con tasas fijas: la selección limpia en 5/5 y la carga es pequeña (vida −1 %). **Responsable (20-10, 09:28): se mantienen σ = 0,05 y tasa 1** | ✅ 0,05 y 1 (revisar si el gemelo de P2 las aleja) |")
sub(F, "La decisión (\"ley del mundo\" o \"gen\") se toma ahora y se prueba en P1 o P2 | 📚 decidir ahora |",
    "La decisión (\"ley del mundo\" o \"gen\") se toma ahora y se prueba en P1 o P2. **Responsable (20-10, 09:28): ley del mundo en toda la escalera; la vejez como gen, en un peldaño propio tras P5** | ✅ ley (gen: peldaño propio) |")
sub(F, "**Gemelos de P2:** tasas como gen y sexo (con tasas fijas).",
    "**Gemelos de P2:** tasas como gen y sexo (con tasas fijas). A4 y C2, decididos a las 09:28: **todas las filas en ✅ o ⏭**.")
Path(F).write_text(Path(F).read_text(encoding="utf-8").rstrip("\n") + """

### 20-10-2026, 09:28 · A4 y C2 decididos: P0 cerrado

- **A4 · cuánto se muta:** se mantienen σ = 0,05 y tasa estructural = 1 (un 11 % de cambios estructurales por hijo). En P0 la variedad crece sin estancarse; en P1, con esas tasas fijas, la selección sigue limpiando en 5/5 y la carga es pequeña (vida un 1 % más corta). No hay señal de exceso (umbral de error, eigen1971selforganization) ni de defecto. Se revisa si el gemelo de P2 con tasas como gen las lleva lejos de estos valores.
- **C2 · muerte y vejez:** ley del mundo en toda la escalera (P0: vida fija de 600 pasos; desde P1, coste creciente desde 5.000 pasos). Es la hipótesis nula y un interruptor menos. La vejez como gen (williams1957pleiotropy, kirkwood1977ageing, werfel2015death) será un peldaño propio cuando aprender compense (tras P5), con su pregunta prerregistrada.
- **Todas las filas están en ✅ o ⏭.** Faltan la ADR de cierre de P0 y la rama de integración (plan, puntos 6 y 7).
""", encoding="utf-8", newline="\n")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 09:26–09:28 · A4 y C2 decididos: todos los factores de P0 cerrados

- **Decisiones del responsable (09:28):**
  - A4: se mantienen σ = 0,05 y tasa estructural = 1. P1 con tasas fijas no muestra exceso ni defecto; se revisa con el gemelo de P2;
  - C2: la vejez es una ley del mundo en toda la escalera; como gen, peldaño propio tras P5.
- **Estado:** todas las filas de `docs/escalera/p0_factores.md` en ✅ o ⏭. Siguiente: ADR de cierre de P0 y rama de integración (5 ramas → un sustrato con tests, determinismo y la CPPN neutral corregida comprobada en P0).
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-A4":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] = (n.get("texto") or "") + " Decisión (20-10, 09:28): se mantienen σ = 0,05 y tasa estructural = 1; P1 con tasas fijas no muestra exceso ni defecto. Revisar con el gemelo de P2."
        if n.get("id") == "p0f-C2":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] = (n.get("texto") or "") + " Decisión (20-10, 09:28): ley del mundo en toda la escalera; la vejez como gen, peldaño propio tras P5."
        if n.get("id") == "p0cierre":
            n["texto"] += " 20-10, 09:28: todos los factores cerrados; faltan la ADR de cierre y la rama de integración."
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m)
arbol = m["arbol"]
i = next(k for k, n in enumerate(arbol) if n.get("id") == "social")
arbol.insert(i + 1, {
    "id": "vejez", "padre": "P6si",
    "titulo": "Peldaño de la vejez: que el envejecimiento evolucione (C2)",
    "corto": "Vejez como gen", "estado": "pendiente", "resultado": None,
    "anade": "la vejez deja de ser una ley del mundo y pasa a ser un gen",
    "texto": "Decisión del responsable (20-10, 09:28): en la escalera la vejez es una ley del mundo; cuando aprender compense (tras P5), un peldaño propio la deja evolucionar. En la Tierra, el envejecimiento evoluciona (Williams 1957, Kirkwood 1977) y en mundos con espacio puede convenir una muerte programada (Werfel et al. 2015). Cambia cuánto dura una generación y cuánto compensa aprender.",
    "ref": "docs/escalera/p0_factores.md"})
m["actualizado"] = "2026-10-20 09:28"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
f = Path("CLAUDE.md"); s = f.read_text(encoding="utf-8")
old = "en P0 quedan A4 y C2."
assert s.count(old) == 1
f.write_text(s.replace(old, "A4 (σ = 0,05, tasa 1) y C2 (vejez como ley; como gen, peldaño propio tras P5) decididos a las 09:28: **todos los factores de P0 cerrados**. Siguiente: ADR de cierre de P0 y rama de integración."), encoding="utf-8", newline="\n")
print("ok")
