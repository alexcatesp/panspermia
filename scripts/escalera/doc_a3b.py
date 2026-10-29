import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "con selección, σ baja 10 veces y la tasa estructural de 8 a 20 | ⚖ decidir |",
    "con selección, σ baja 10 veces y la tasa estructural de 8 a 20. **Responsable (20-10, 07:01): fijas; en P2, gemelo con las tasas como gen** | ✅ fijas (P2: gemelo) |")
sub(F, "Medir en P0 cuántas mutaciones se pierden por redondeo. Hecho: entre el 6 y el 10 % | ⚖ tras A3 |",
    "Medir en P0 cuántas mutaciones se pierden por redondeo. Hecho: entre el 6 y el 10 % (9–22 % en P1 con σ como gen; 0,7 % con σ fija) | ✅ f16, con A3 (tasas fijas) |")
sub(F, "- **A7 depende de A3:** con σ como gen y selección, el redondeo a f16 borra entre el 9 y el 22 % de las perturbaciones de los pesos (más que en P0). Si las tasas son gen, f16 se convierte en un suelo real de la mutación; con tasas fijas, basta.\n",
    "- **A7 depende de A3:** con σ como gen y selección, el redondeo a f16 borra entre el 9 y el 22 % de las perturbaciones de los pesos (más que en P0). Si las tasas son gen, f16 se convierte en un suelo real de la mutación; con tasas fijas, basta.\n"
    "- **Decisión del responsable (07:01):** tasas **fijas** (σ = 0,05, tasa estructural = 1) en el sustrato integrado; con ellas, **f16 basta** (A7). En P2 se añade un gemelo con las tasas como gen, para ver si mutar menos frena la adaptación cuando hay algo que ganar. Si la ganara, la tasa como gen exigiría revisar A7 (precisión de los pesos).\n")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 07:01 · A3 y A7 decididos

- **Decisión del responsable (07:01):** tasas de mutación **fijas** (σ = 0,05, tasa estructural = 1) en el sustrato integrado; con ellas, los pesos en **f16** bastan (A7). En P2 se añade un gemelo con las tasas como gen: lo que P1 no puede juzgar (si mutar menos frena la adaptación cuando hay ganancias) se prueba allí.
- **Por qué:** sin selección (P0), las tasas como gen derivan hacia arriba al azar y cada mundo acaba con un régimen distinto; con solo selección negativa (P1), se hunden. En los dos casos añaden una deriva que no es la pregunta del peldaño. Fijarlas es la opción limpia y comparable; la versión natural se prueba cuando pueda demostrar su valor.
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-A3":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] += " Decisión (20-10, 07:01): fijas; en P2, gemelo con las tasas como gen."
            n["texto"] = n["texto"].replace(" Decide el responsable.", "")
        if n.get("id") == "p0f-A7":
            n["estado"] = "hecho"; n["resultado"] = "positivo"
            n["texto"] += " Decisión (20-10, 07:01): f16, porque las tasas quedan fijas."
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m); m["actualizado"] = "2026-10-20 07:01"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
C = Path("docs/caminos.md"); s = C.read_text(encoding="utf-8")
anchor = "| Mutación de neuronas \"terrestre\" (perder más que ganar) |"
i = s.index(anchor); j = s.index("\n", i)
s = s[:j+1] + "| Tasas de mutación como gen (σ autoadaptativa y tasa estructural) | Aparcado | Sin selección derivan hacia arriba (P0); con solo selección negativa se hunden 10 veces (P1) | Gemelo en P2: si con ganancias mutar más compensa, se reabre (y con ella A7, la precisión de los pesos) | `docs/escalera/p0_factores.md` (A3) |\n" + s[j+1:]
C.write_text(s, encoding="utf-8", newline="\n")
print("ok")
