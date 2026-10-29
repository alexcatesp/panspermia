import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")

F = "docs/escalera/p0_factores.md"
sub(F, "**Responsable (19-10, 07:20): decidir tras P1-peaje-tasas-fijas frente a P1-peaje** | 🔬 P1 en cola |",
    "**Responsable (19-10, 07:20): decidir tras P1-peaje-tasas-fijas frente a P1-peaje.** P1 hecho (20-10, 02:32): con selección, σ baja 10 veces y la tasa estructural de 8 a 20 | ⚖ decidir |")
Path(F).write_text(Path(F).read_text(encoding="utf-8").rstrip("\n") + """

### 20-10-2026, 02:32 · A3 con selección: P1 con tasas fijas frente a P1-peaje (5 mundos)

P1-peaje-tasas-fijas (rama `escalera-p0x`) terminó a las 02:26, 0,62 h por mundo. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (nest, tasas como gen), emparejado por semilla. Datos en `runs/fase1d/_analisis_A3_P1.json`, `_host_P1-peaje.json` y `_host_P1-peaje-tasas-fijas.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | Tasas como gen (P1-peaje) | Tasas fijas | Signo |
|---|---|---|---|
| σ de los pesos, mediana en la época 300 | **0,0046–0,0069** (empieza en 0,05) | 0,05 | — |
| Tasa estructural, mediana en la época 300 | **0,05–0,13** (empieza en 1) | 1 | — |
| Neuronas ocultas | 0,11–0,42 (0,05–0,10) | 0,48–0,54 (0,49–0,56) | 5/5 más con fijas |
| Distancia estructural | 13–27 | 63–79 | 5/5 más con fijas |
| Vida media (pasos) | 521–528 | 516–518 | 5/5 menos con fijas |
| Nacimientos por época | 7.746–7.848 | 7.895–7.920 | 5/5 más con fijas |
| CPPN en el techo, época 300 | 0 % | 0–38 % | — |
| Perturbaciones borradas por f16 (A7) | **9–22 %** | 0,7 % | — |

- **Con selección, las tasas como gen bajan solas, y mucho:** σ cae unas 10 veces y la tasa estructural entre 8 y 20 veces, en los 5 mundos. En P0, sin selección, subían (σ 0,013–0,055 y tasa 1,05–2,58, por el suelo en 0). Es lo que predice la teoría para un mundo que no cambia: si casi toda mutación es dañina, la selección baja la tasa hasta la barrera de la deriva (lynch2016driftbarrier). Con las tasas como gen, el genoma aprende a mutar menos.
- **Con tasas fijas, la población carga con más mutaciones dañinas:** más neuronas que cuestan (equilibrio entre mutación y selección), más variedad estructural, vidas algo más cortas y más nacimientos. El efecto es pequeño y no amenaza a nadie (siempre 4.096).
- **Lo que P1 no puede juzgar:** en un mundo sin nada que ganar, mutar menos siempre conviene. En un mundo que cambia o con mejoras por descubrir (P2 en adelante), mutar poco frena la adaptación y los mutadores pueden ganar (sniegowski1997mutators, taddei1997mutator). Si las tasas se dejan como gen, P1 las hunde y P2 empezaría con poblaciones casi congeladas.
- **A7 depende de A3:** con σ como gen y selección, el redondeo a f16 borra entre el 9 y el 22 % de las perturbaciones de los pesos (más que en P0). Si las tasas son gen, f16 se convierte en un suelo real de la mutación; con tasas fijas, basta.
""", encoding="utf-8", newline="\n")

B = "docs/bitacora.md"
Path(B).write_text(Path(B).read_text(encoding="utf-8").rstrip("\n") + """

## 20-10-2026

### 23:22–02:32 · A3 con selección: P1 con tasas fijas frente a P1-peaje

- **Qué:** P1-peaje-tasas-fijas (rama `escalera-p0x`, cola `p1x.json`, 5 mundos), de 23:22 a 02:26, 0,62 h por mundo; σ = 0,05 y tasa estructural = 1 en todos los bichos. Llenos, sin extinciones ni pausas. Referencia: P1-peaje (tasas como gen), emparejado por semilla.
- **Datos:** `runs/fase1d/_analisis_A3_P1.json` (series, ventana 151–300) y `_host_P1-peaje.json`, `_host_P1-peaje-tasas-fijas.json` (genomas de la época 300, en CPU).
- **Resultado:**
  - tasas como gen en P1, época 300: mediana de σ 0,0046–0,0069 (empieza en 0,05) y de la tasa estructural 0,05–0,13 (empieza en 1). En P0 subían;
  - con tasas fijas: neuronas 0,48–0,54 frente a 0,11–0,42 (5/5); distancia estructural 63–79 frente a 13–27 (5/5); vida media 516–518 frente a 521–528 pasos (5/5 menor); nacimientos 5/5 mayores;
  - f16 (A7): borra entre el 9 y el 22 % de las perturbaciones con σ como gen, y el 0,7 % con σ fija.
- **Conclusión (firme para P1):** con selección y sin nada que ganar, la tasa de mutación como gen baja un orden de magnitud (dirección de la barrera de la deriva, lynch2016driftbarrier). Con tasas fijas, la población arrastra una carga de mutaciones algo mayor. Lo que P1 no puede decir es si mutar tan poco frena la adaptación cuando sí hay algo que ganar (P2).
- **Pendiente:** decisión del responsable sobre A3 (y con ella A7).
""", encoding="utf-8", newline="\n")

M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-A3":
            n["texto"] = ("P0: tasas fijas, algo menos de neuronas (5/5, efecto pequeño) y f16 deja de ser un problema. "
                          "P1 (20-10, 02:32): con selección, las tasas como gen bajan solas (σ 10 veces, tasa estructural 8–20 veces); "
                          "con tasas fijas, algo más de carga de mutaciones (5/5). Falta saber si mutar tan poco frena la adaptación en P2. Decide el responsable.")
        if n.get("id") == "p0f-A7":
            n["texto"] = ("f16 borra el 6–10 % de las pequeñas perturbaciones en P0 y el 9–22 % en P1 cuando σ es gen (la selección la baja); "
                          "solo el 0,7 % con σ fija en 0,05. Se decide con A3.")
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m)
m["actualizado"] = "2026-10-20 02:32" if "actualizado" in m else m.get("actualizado")
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

R = Path("docs/bibliografia/escalera/refs.bib")
R.write_text(R.read_text(encoding="utf-8").rstrip("\n") + """

@article{taddei1997mutator,
  author  = {Taddei, F. and Radman, M. and Maynard-Smith, J. and Toupance, B. and Gouyon, P. H. and Godelle, B.},
  title   = {Role of mutator alleles in adaptive evolution},
  journal = {Nature},
  volume  = {387},
  pages   = {700--702},
  year    = {1997},
  doi     = {10.1038/42696}
}
""", encoding="utf-8", newline="\n")

D = Path("docs/bibliografia/escalera/README.md")
D.write_text(D.read_text(encoding="utf-8").rstrip("\n") + """

## 10. ¿Tasa de mutación como gen o constante? (A3 con selección)

- **En un mundo que no cambia, la selección baja la tasa de mutación.** Casi toda mutación es dañina, así que los linajes que mutan menos dejan hijos más sanos. La tasa baja hasta que la ventaja de bajarla más es menor que el ruido de la deriva (barrera de la deriva, lynch2016driftbarrier). Es lo que se ve en P1: σ cae 10 veces y la tasa estructural de 8 a 20 veces en 300 épocas.
- **En un mundo con algo por descubrir, mutar más puede ganar.** Los mutadores viajan junto a las mejoras que producen (autostop genético) y llegan a dominar poblaciones que se adaptan (taddei1997mutator; en *E. coli*, sniegowski1997mutators). Por eso la tasa como gen solo se puede juzgar en un peldaño con ganancias (P2 o después).
- **En evolución artificial**, la autoadaptación de σ (beyer2002es) funciona cuando hay un gradiente de mejora; sin él, σ cae hasta el límite inferior y la búsqueda se detiene.
""", encoding="utf-8", newline="\n")
print("ok")
