# Panel 07 · Segunda ronda: síntesis tras H2 (26-10-2026, 21:58)

## Coincidencias (los tres)
- **H2 es negativo por la regla 7 de ADR-030. Se salta H3:** si ni el cobro inmediato se aprende, el cuello está en el cerebro y no en el mundo.
- **B sola (trazas con la m actual) no se lanza ahora.** Su control positivo (ADR-031) ya predice el fallo sin una m con signo de resultado.
- **Orden:** D (diagnóstico, solo observa, sin mundos) → C (m con signo de resultado) **sobre el inmediato**, con la misma trampa → si pasa, C sobre el diferido → solo entonces B + C.
- **E (publicar la maduración) va en paralelo** y no gasta comparaciones.
- **Predicción común:** pocos bichos con moduladoras y m sin signo; C sobre el inmediato da probablemente un indicio y no el 9/10 (25–35 %).

## Discrepancias y síntesis del moderador
1. **Umbral de moduladoras.** Biología pone el 30 % de los bichos; Ingeniería y Método, el 50 %.
   → **50 % (2–1).**
2. **Medida del signo.** Biología: Pearson, |r| ≥ 0,3. Ingeniería: |corr| < 0,05 o ≤ −0,1. Método: Spearman por bicho contra la permutación temporal dentro del bicho.
   → **La de Método:** es la única con un nulo propio.
3. **Regla de D, sobre los checkpoints de la época 300 de los 10 mundos del inmediato** (el diferido se mide igual, solo como descripción):
   - (a) **f_mod:** fracción de adultos vivos con ≥ 1 oculta moduladora expresada (lectura estática).
   - (b) **ρ(m, ΔE):** un recorrido de 500 pasos, con la plasticidad como en vida y sin nacimientos, guardando por paso y bicho m, el bocado y el cobro. Se calcula Spearman por bicho en los pasos con bocado o cobro, sobre 200 adultos por mundo. Nulo: 1.000 permutaciones temporales dentro del bicho. Un mundo «tiene señal» si la mediana de ρ supera el percentil 97,5 del nulo y |ρ| ≥ 0,2.
   - (c) **Signo del cobro:** en el inmediato, ¿m es menor en los pasos de neto negativo que en los de bocado neto positivo? Mismo nulo y mismo criterio.
   - **Decisión:**
     - f_mod < 0,5 en ≥ 7/10 → C, y C fija m (no solo le suma un término).
     - f_mod ≥ 0,5 y sin señal en (b) ni en (c) en ≥ 7/10 → C como término aditivo.
     - Señal en (b) y (c) en ≥ 7/10 → B sola, y C se replantea.
     - Otro patrón → C, sin volver a diagnosticar.
   - **Coste y seguridad:** GPU libre, un mundo cada vez, `setsid nohup` y JSONL tras cada mundo. Hay que usar el sustrato 3.6.0 (`panspermia-veneno`).
   - **Límite declarado:** es una correlación. Solo descarta o confirma que falta el signo.
4. **Controles de C** (los fija el panel 08 al diseñarla):
   - el padre P5-inmediato actual;
   - un control con el error barajado en el tiempo dentro de cada bicho (Método), para descartar que el efecto sea «más plasticidad»;
   - H-control repetido sobre los mundos de C.
   - Aviso de Biología: vigilar que el cerebro no se vacíe bajo C.
5. **Contador:** D no gasta comparación. C inmediato y su barajado cuentan como una (14).

Responde en menos de 120 palabras: **ACEPTO** o **RECHAZO** (con el cambio concreto).
