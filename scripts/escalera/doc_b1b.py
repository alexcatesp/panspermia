import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "| ⚖ decidir (P1 hecho, 20-10, 09:01) |", "| ✅ asexual (P2: gemelo con sexo) |")
sub(F, "La ventaja de limpiar mutaciones malas (kondrashov1988deleterious) no aparece en P1.\n",
    "La ventaja de limpiar mutaciones malas (kondrashov1988deleterious) no aparece en P1.\n"
    "- **Decisión del responsable (09:17):** el sustrato integrado sigue **asexual** (spec v1). En P2 se añade un gemelo con sexo (cruce corregido, ADR-018) y tasas fijas, donde puede demostrar su ventaja. El cruce queda en el código como opción (`REPRODUCTION`). Si en P2 el sexo gana, se adopta desde P2 y se anota que P0 y P1 fueron asexuales; los dos peldaños son de purga, donde el sexo apenas cambia la respuesta a su pregunta.\n")
sub(F, "5. **A2, A3 y B1 en P1 (responsable, 19-10, 23:39):** decidir caso a caso; lo que P1 no pueda juzgar (en P1 la selección solo quita) se prueba en P2 antes de fijarlo.",
    "5. **A2, A3 y B1 en P1 (responsable, 19-10, 23:39):** decidir caso a caso; lo que P1 no pueda juzgar (en P1 la selección solo quita) se prueba en P2 antes de fijarlo. ✅ Decididos el 20-10: A3 tasas fijas (07:01), A2 CPPN neutral corregida (07:10), B1 asexual (09:17). **Gemelos de P2:** tasas como gen y sexo (con tasas fijas).")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 09:17 · B1 decidido

- **Decisión del responsable (09:17):** sustrato **asexual**; en P2, gemelo con sexo (cruce corregido) y tasas fijas, donde la ventaja de juntar mejoras puede aparecer. El cruce queda en el código como opción.
- **Con esto, en P0 solo quedan A4 (cuánto se muta, ahora con tasas fijas: elegir σ y la tasa estructural) y C2 (muerte y vejez).** La GPU está libre desde las 08:54.
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-B1":
            n["estado"] = "hecho"; n["resultado"] = "no concluyente"
            n["texto"] = n["texto"].replace(" Decide el responsable.", " Decisión (20-10, 09:17): asexual; en P2, gemelo con sexo y tasas fijas.")
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m); m["actualizado"] = "2026-10-20 09:17"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
C = Path("docs/caminos.md"); s = C.read_text(encoding="utf-8")
anchor = "| Tasas de mutación como gen"
i = s.index(anchor)
s = s[:i] + "| Reproducción sexual (cruce por índice con bloques, ADR-018) | Aparcado | P0: casi neutral. P1: la selección purga peor, sobre todo porque con sexo la tasa de mutación como gen apenas baja; efecto propio pequeño | Gemelo en P2 con tasas fijas: si junta mejoras y acelera la adaptación, se adopta desde P2 | `docs/escalera/p0_factores.md` (B1) |\n" + s[i:]
C.write_text(s, encoding="utf-8", newline="\n")
f = Path("CLAUDE.md"); s = f.read_text(encoding="utf-8")
old = "Queda B1 (P1 con sexo, en marcha)."
assert s.count(old) == 1
f.write_text(s.replace(old, "B1 (09:17): asexual; en P2, gemelo con sexo y tasas fijas. Las colas de GPU terminaron el 20-10 a las 08:54; en P0 quedan A4 y C2."), encoding="utf-8", newline="\n")
print("ok")
