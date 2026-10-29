import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "**Responsable (19-10, 07:22): decidir tras P1-peaje-cppn-neutral** | 🔬 P1 en cola |",
    "**Responsable (19-10, 07:22): decidir tras P1-peaje-cppn-neutral.** P1 hecho (20-10, 07:15): la de siempre se infla incluso con selección; la neutral no, y con selección conserva las aristas | ⚖ decidir |")
Path(F).write_text(Path(F).read_text(encoding="utf-8").rstrip("\n") + """

### 20-10-2026, 07:15 · A2 con selección: P1 con CPPN neutral frente a P1-peaje (5 mundos)

P1-peaje-cppn-neutral (rama `escalera-p0x`) terminó a las 05:32. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (CPPN de siempre), emparejado por semilla. Datos en `runs/fase1d/_analisis_A2_P1.json` y `_dist_cppn_P1.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | CPPN de siempre (P1-peaje) | CPPN neutral | Signo |
|---|---|---|---|
| Nodos ocultos de la CPPN | 0,8–11,2 (1,1–12,0) | 0,4–2,7 (0,4–2,9) | 4/5 menos con neutral |
| Aristas de la CPPN | 51–61 (52–61) | 35–45 (34–45) | 5/5 menos con neutral |
| Mínimo de aristas, época 300 | 39–57 | 29–36 (nadie con 10 o menos) | — |
| Neuronas ocultas | 0,11–0,42 | 0,09–0,22 | 3/5 menos |
| Empuje, vida media y nacimientos | iguales | iguales | — |

- **La receta del cerebro no paga peaje:** en P1 cuestan las neuronas y moverse, no los nodos de la CPPN. Por eso, con la mutación de siempre, la CPPN sigue inflándose incluso con selección (hasta 12 de 18 nodos en s0) y la selección no lo corrige. Con tasas fijas (A3, ya decidido), la de siempre llega al techo en 3 de 5 mundos (27–38 % de los bichos en la época 300).
- **La neutral no se infla y, con selección, ya no se vacía:** en P0 perdía aristas (26–35 en la época 300, mínimo 2). En P1 se queda en 34–45, y nadie baja de 29: los bichos con la receta casi vacía dejan menos hijos. El sesgo hacia perder aristas sigue ahí (la media baja de 48), pero la selección lo frena.
- **No cambia nada de lo que la selección mide:** empuje, vida y nacimientos salen iguales. El cerebro no se resiente.
- **Lo que P1 no puede juzgar:** si una receta más pequeña limita construir cerebros complejos cuando compensa (P2 en adelante).
""", encoding="utf-8", newline="\n")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 02:26–07:15 · A2 con selección: P1 con CPPN neutral frente a P1-peaje

- **Qué:** P1-peaje-cppn-neutral (rama `escalera-p0x`, cola `p1x.json`, 5 mundos), de 02:26 a 05:32, 0,62 h por mundo. Llenos, sin extinciones ni pausas. Fin de `tras_p0.sh` a las 05:32 (marca `p1_x_hecho`). Después arrancó `tras_p1.sh` (P1 con sexo, B1).
- **Datos:** `runs/fase1d/_analisis_A2_P1.json` (series, ventana 151–300) y `_dist_cppn_P1.json` (nodos y aristas de la CPPN en la época 300, en CPU).
- **Resultado:**
  - nodos ocultos de la CPPN: 0,4–2,7 frente a 0,8–11,2 (4/5 menos);
  - aristas: 35–45 frente a 51–61 (5/5 menos); mínimo 29–36, nadie con 10 o menos (en P0 neutral, hasta un 10 % y mínimo 2);
  - empuje, vida media, nacimientos y población: iguales.
- **Conclusión (firme para P1):** la CPPN no paga peaje, así que con la mutación de siempre sigue inflándose aunque haya selección. Con la neutral no se infla, y la selección frena la pérdida de aristas que se veía en P0. Falta saber si una receta pequeña limita construir cuando compensa (P2).
- **Pendiente:** decisión del responsable sobre A2 (y con ella A5, el techo).
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-A2":
            n["texto"] = ("P0: CPPN neutral, 1,6–3,0 nodos frente a 10–13 (5/5) y nadie en el techo, pero pierde aristas (26–35; mínimo 2). "
                          "P1 (20-10, 07:15): la de siempre se infla incluso con selección (la receta no paga peaje); la neutral no, "
                          "y la selección frena la pérdida de aristas (34–45; mínimo 29). Empuje y vida iguales. Decide el responsable.")
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m); m["actualizado"] = "2026-10-20 07:15"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
print("ok")
