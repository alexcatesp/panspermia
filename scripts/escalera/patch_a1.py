from pathlib import Path
ROOT = Path("D:/Development/panspermia")
def sub(p, old, new):
    f = ROOT / p; s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

F = "docs/escalera/p0_factores.md"
sub(F, "- ⏭ no es de P0 (se decide en su peldaño).",
    "- ⚖ simulado; falta la decisión del responsable;\n- ⏭ no es de P0 (se decide en su peldaño).")
sub(F, "| P0 con nest (✅ 5/5), neutral y terrestre (🔬) | 🔬 |",
    "| P0 con nest, neutral y terrestre (✅ 15 mundos; 5/5 en las dos comparaciones) | ⚖ |")
sub(F, "| stanley2002neat | Se decide junto con A1 | 📚 |",
    "| stanley2002neat, lynch2003origins | Se decide junto con A1: con la física neutral, el tamaño inicial es el punto alrededor del cual deriva | ⚖ con A1 |")
F2 = ROOT / F
F2.write_text(F2.read_text(encoding="utf-8") + """
### 19-10-2026, 03:08 · A1: P0 con mutación neutral y terrestre (10 mundos)

La cola terminó a las 02:56. Ventana de las épocas 151–300; los valores son por semilla, s0 a s4. Datos en `runs/fase1d/_analisis_A1.json`, `_host_P0-feliz-neutral.json`, `_host_P0-feliz-terrestre.json` y `_dist_neuronas.json`.

**Neuronas ocultas, media tardía:**

| Física | s0 | s1 | s2 | s3 | s4 | En la época 300 |
|---|---|---|---|---|---|---|
| nest (la de siempre) | 24,1 | 23,8 | 28,9 | 21,0 | 24,5 | 25–35 de media; siguen creciendo |
| neutral | 8,0 | 7,9 | 8,0 | 8,0 | 8,8 | 6,1–11,2 de media, desviación típica de 4,5 a 7,7; entre el 3 y el 8 % sin neuronas ocultas |
| terrestre | 1,6 | 1,7 | 0,8 | 1,3 | 1,9 | 0,7–1,3 de media; **entre el 51 y el 67 % sin neuronas ocultas**; máximo de 8 a 12 |

**Contrastes prerregistrados (ADR-015):**
- neutral < nest: **5/5** (p = 0,031), con diferencias de −13,0 a −20,9 neuronas;
- terrestre < neutral: **5/5** (p = 0,031), con diferencias de −6,2 a −7,2.

**Lectura:**
- **nest** infla el cerebro sin que sirva para nada. Es un sesgo de la mutación, no de la selección.
- **neutral** conserva la media en el punto de partida (8) y solo ensancha la distribución por deriva: el tamaño del cerebro queda libre para que lo decida la selección.
  - Matiz: el suelo en 0 rebota, así que a muy largo plazo la media sube despacio (s4: +3,4 por 100 épocas). Hay que vigilarlo en peldaños largos.
- **terrestre** vacía el cerebro en 300 épocas. Con selección, solo sobrevivirían las neuronas cuya ventaja supere la barrera de la deriva (lynch2016driftbarrier). Es el modo "procariota", de genoma compacto (mira2001deletional, kuo2009deletional).

**Control:** la CPPN, el cuerpo, las tasas de mutación, f16 y los nacimientos son **idénticos** en las tres físicas (mismo valor en cada semilla). La física de neuronas solo cambia las neuronas: la comparación es limpia.

**Para la decisión:**
- desde P1, cada neurona cuesta energía (`C_NEURON` = 0,02 por paso; "tejido caro", aiello1995expensive);
- con la física neutral, la presión hacia cerebros pequeños vendría del mundo y no de la mutación;
- con la terrestre, las dos presiones se sumarían.

A6 (genoma inicial) se decide con A1: con la física neutral, las 8 neuronas iniciales son el centro de la deriva.
""", encoding="utf-8", newline="\n")
print("ok")
