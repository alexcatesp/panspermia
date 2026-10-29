import json
from pathlib import Path
def sub(p, old, new):
    f = Path(p); s = f.read_text(encoding="utf-8")
    assert s.count(old) == 1, (p, old[:60], s.count(old))
    f.write_text(s.replace(old, new), encoding="utf-8", newline="\n")
F = "docs/escalera/p0_factores.md"
sub(F, "| 🔬 P1 en marcha (fin ≈ 09:00) |", "| ⚖ decidir (P1 hecho, 20-10, 09:01) |")
Path(F).write_text(Path(F).read_text(encoding="utf-8").rstrip("\n") + """

### 20-10-2026, 09:01 · B1 con selección: P1 con sexo frente a P1-peaje (5 mundos)

P1-peaje-sexual-bloques (rama `escalera-p0z`, cruce corregido de ADR-018) terminó a las 08:54, 0,67 h por mundo. Todos llenos (4.096), sin extinciones ni pausas. Se compara con P1-peaje (asexual), emparejado por semilla; las dos con las tasas de mutación como gen. Datos en `runs/fase1d/_analisis_B1_P1.json`, `_host_P1-peaje-sexual-bloques.json` y `_b1_cppn_P1.json`. Ventana 151–300 (época 300 entre paréntesis).

| Medida | Asexual (P1-peaje) | Sexual | Signo | Asexual con tasas fijas (A3) |
|---|---|---|---|---|
| σ, mediana en la época 300 | 0,0046–0,0069 | **0,015–0,033** | 5/5 mayor | 0,05 |
| Tasa estructural, mediana | 0,05–0,13 | **0,67–0,97** | 5/5 mayor | 1 |
| Neuronas ocultas | 0,11–0,42 (0,05–0,10) | 0,45–0,79 (0,47–0,79) | 5/5 más | 0,48–0,54 |
| Empuje | 0,004–0,10 | 0,16–0,24 | 5/5 más | 0,02–0,20 |
| Distancia genética (pesos) | 8–15 | 29–43 | 5/5 más | 14–16 |
| Distancia estructural | 13–27 | 97–116 | 5/5 más | 63–79 |
| Vida media (pasos) | 521–528 | 514–520 | 5/5 menos | 516–518 |
| Nodos de la CPPN sin salida, época 300 | 0–10 % | 3–7 % | — | — |

- **Pregunta prerregistrada de P1 (menos empuje que en P0):** se cumple también con sexo (0,16–0,24 frente a 5–7).
- **Con sexo, la selección purga peor en P1:** queda más cerebro, más movimiento, más variedad y vidas algo más cortas. La causa principal es la tasa de mutación: con sexo apenas baja (σ de 0,05 a 0,015–0,033, la tasa estructural de 1 a 0,7–1), mientras que sin sexo cae 10 veces. Es lo que predice la teoría: el cruce separa al gen que sube la tasa de las mutaciones malas que causa, y la selección deja de verlo (johnson1999mutation, lynch2010mutationrate). Por tanto, esta comparación mezcla dos cosas: el sexo y la tasa de mutación.
- **Frente al asexual con tasas fijas** (más parecido en tasas), el sexo deja algo más de cerebro y movimiento (4/5 en empuje) y mucha más variedad estructural, con tasas menores. El efecto propio del sexo existe, pero es pequeño.
- **El cruce corregido funciona:** los nodos de la CPPN sin salida son el 3–7 % (con el error eran el 83–88 %).
- **Lo que P1 no puede juzgar:** la gran ventaja del sexo, juntar en un hijo mejoras que aparecieron en bichos distintos (colegrave2002sex, hill1966linkage), necesita mejoras que ganar (P2). La ventaja de limpiar mutaciones malas (kondrashov1988deleterious) no aparece en P1.
""", encoding="utf-8", newline="\n")
B = Path("docs/bitacora.md")
B.write_text(B.read_text(encoding="utf-8").rstrip("\n") + """

### 05:32–09:01 · B1 con selección: P1 con sexo frente a P1-peaje

- **Qué:** P1-peaje-sexual-bloques (rama `escalera-p0z`, cola `p1z.json`, cruce corregido de ADR-018, 5 mundos), de 05:32 a 08:54, 0,67 h por mundo. Llenos, sin extinciones ni pausas. Fin de `tras_p1.sh` (marca `p1_z_hecho`): la GPU queda libre.
- **Datos:** `runs/fase1d/_analisis_B1_P1.json`, `_host_P1-peaje-sexual-bloques.json`, `_b1_cppn_P1.json`.
- **Resultado (sexual frente a asexual, ventana 151–300):** neuronas 0,45–0,79 frente a 0,11–0,42; empuje 0,16–0,24 frente a 0,004–0,10; distancia estructural 97–116 frente a 13–27; vida 514–520 frente a 521–528 (todo 5/5). Mediana de σ en la época 300: 0,015–0,033 frente a 0,005–0,007; tasa estructural 0,67–0,97 frente a 0,05–0,13. CPPN sin salida: 3–7 %.
- **Conclusión (firme para P1, con una mezcla):** con sexo, la selección purga peor, sobre todo porque la tasa de mutación como gen apenas baja (el cruce desliga la tasa de sus efectos; johnson1999mutation). Frente al asexual con tasas fijas, el efecto propio del sexo es pequeño. El cruce corregido funciona. La ventaja principal del sexo (juntar mejoras) no se puede ver en P1.
- **Pendiente:** decisión del responsable sobre B1.
""", encoding="utf-8", newline="\n")
M = Path("docs/mapa.json"); m = json.loads(M.read_text(encoding="utf-8"))
def walk(n):
    if isinstance(n, dict):
        if n.get("id") == "p0f-B1":
            n["texto"] = ("P0: casi neutral con el cruce corregido. P1 (20-10, 09:01): con sexo la selección purga peor (más cerebro, empuje y variedad, 5/5), "
                          "sobre todo porque la tasa de mutación como gen apenas baja con sexo (σ 0,015–0,033 frente a 0,005). "
                          "La ventaja de juntar mejoras solo se ve con algo que ganar (P2). Decide el responsable.")
        for v in n.values(): walk(v)
    elif isinstance(n, list):
        for v in n: walk(v)
walk(m); m["actualizado"] = "2026-10-20 09:01"
M.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
R = Path("docs/bibliografia/escalera/refs.bib")
R.write_text(R.read_text(encoding="utf-8").rstrip("\n") + """

@article{johnson1999mutation,
  author  = {Johnson, Toby},
  title   = {Beneficial mutations, hitchhiking and the evolution of mutation rates in sexual populations},
  journal = {Genetics},
  volume  = {151},
  number  = {4},
  pages   = {1621--1631},
  year    = {1999},
  doi     = {10.1093/genetics/151.4.1621}
}

@article{kondrashov1988deleterious,
  author  = {Kondrashov, Alexey S.},
  title   = {Deleterious mutations and the evolution of sexual reproduction},
  journal = {Nature},
  volume  = {336},
  pages   = {435--440},
  year    = {1988},
  doi     = {10.1038/336435a0}
}

@article{lynch2010mutationrate,
  author  = {Lynch, Michael},
  title   = {Evolution of the mutation rate},
  journal = {Trends in Genetics},
  volume  = {26},
  number  = {8},
  pages   = {345--352},
  year    = {2010},
  doi     = {10.1016/j.tig.2010.05.003}
}
""", encoding="utf-8", newline="\n")
D = Path("docs/bibliografia/escalera/README.md")
D.write_text(D.read_text(encoding="utf-8").rstrip("\n") + """

## 12. Sexo con selección: por qué en P1 purga peor (B1)

- **Con sexo, la tasa de mutación casi no baja.** En un asexual, el gen que sube la tasa viaja siempre con las mutaciones malas que causa, y la selección lo elimina con ellas. Con cruce, se separa de ellas en pocas generaciones, y la selección apenas lo ve (johnson1999mutation; lynch2010mutationrate: los organismos sexuales toleran tasas mayores). En P1, σ baja 10 veces sin sexo y solo de 1,5 a 3 con sexo.
- **La ventaja de limpiar mutaciones malas** (kondrashov1988deleterious) necesita que los daños se potencien entre sí (epistasia sinérgica) y muchas mutaciones por hijo. En P1 no se ve: cada neurona cuesta lo mismo, se sume a otras o no.
- **La ventaja principal del sexo es juntar mejoras** que aparecen en bichos distintos (hill1966linkage, felsenstein1974recombination, colegrave2002sex). Sin nada que ganar (P1) no puede aparecer; hay que probarla en P2.
""", encoding="utf-8", newline="\n")
print("ok")
