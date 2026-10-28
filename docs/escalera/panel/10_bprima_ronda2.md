# Panel 10 · Ronda 2 (28-10-2026, 07:31)

## Ronda 1 (07:29–07:30; resúmenes del moderador)
- **Biología:** b′ tal cual (k sin tocar: m binaria con signo, como en C). b′ y b′bar, 10 + 10, semillas nuevas 20–29, 300 épocas. Calibración de viabilidad de 1–2 semillas × 100 épocas. Primaria E − X con H-control: > 0 en ≥ 9/10, diferencia frente a b′bar > 0,05 y Mann-Whitney p < 0,01. ΔD secundaria ≥ 8/10. Negativo: |E − X| < 0,03 en ≥ 7/10 sin diferencia; 6–8/10, indicio. Secundarias: |w|, W_MAX, f_mod, crianza (descriptiva). Predicción 15 % (ΔD 80 %).
- **Método:** b′ tal cual; cada retoque tras el control positivo es un grado de libertad. Semillas 0–9, emparejadas con C. Calibración de 3–4 mundos solo de viabilidad (población, sin extinción, sin W_MAX), un ajuste como mucho. Primaria:
  - H-control;
  - E − X > 0 en ≥ 9/10 y mediana ≥ 0,04;
  - Mann-Whitney frente a b′bar p < 0,01, con diferencia de medianas ≥ 0,03.

  ΔD es guarda (≥ 9/10), no vía alternativa de éxito. Negativo: ≤ 6/10 o mediana dentro de ±0,02; entre medias, o con W_MAX, indicio no concluyente. W_MAX > 50 %, no interpretable. Sin crianza. Predicción 12 % (8–20 %).
- **Ingeniería:** b′ tal cual. Calibración de 3 semillas × 100 épocas (población, W_MAX, f_mod). Primaria: E − X mediana ≥ 0,03, > 0 en ≥ 9/10, Mann-Whitney frente a b′bar p < 0,01, H-control. ΔD secundaria ≥ 9/10 y mediana ≥ 0,10. Negativo: ±0,02 en ≥ 8/10 con ΔD > 0 («qué comer, no a dónde ir»); ΔD por debajo de C, las trazas dañan; W_MAX > 50 % en la época 100, saturado (no concluyente). Ablación de las trazas en la sonda si hay hueco. Predicción 12 % (ΔD 80 %).

## Propuesta de síntesis del moderador
1. **b′ tal cual:** ε = 0,05, k = 8,65, TRACE_TAU 40. Unánime.
2. **Tanda:**
   - P5-inmediato con b′ (DELTA_ON 1) y b′bar (DELTA_ON 2), los dos con ε = 0,05 y trazas;
   - 10 + 10 mundos, **semillas 0–9** (mismo mundo inicial que C y Cbar), 300 épocas, desde cero.
3. **Calibración solo de viabilidad:**
   - 3 mundos de b′ (s0–s2) × 100 épocas;
   - es viable si no hay extinción, la población media de las épocas 50–100 es ≥ 1.000 y menos del 50 % de los pesos plásticos de los vivos están en W_MAX en la época 100.
   - Si no es viable, un único ajuste: k/2 (la regla de C). No se mira ninguna medida de aprendizaje.
4. **Primaria (deben cumplirse todas):**
   - H-control pasa;
   - E − X > 0 en ≥ 9/10 mundos de b′ y mediana ≥ +0,04;
   - Mann-Whitney unilateral b′ > b′bar con p < 0,01 y diferencia de medianas ≥ +0,03.
5. **Negativo:** E − X > 0 en ≤ 6/10, o mediana ≤ +0,02. Lo de en medio es indicio no concluyente, sin segunda tanda automática.
6. **Guarda ΔD** (sonda mixta, b′): ΔD > 0 en ≥ 9/10. No es una vía de éxito. Si falla, se registra «las trazas dañan lo de C».
7. **No interpretable:** > 50 % de los pesos plásticos en W_MAX en la época 300 (mediana de los mundos).
8. **Descriptivas** (sin puerta): |w| medio, fracción en W_MAX, f_mod, fracción de m saturada, fracción de pasos con suceso, P(comer buena). Sin crianza (innata en C). La ablación de las trazas en la sonda, solo si b′ pasa.
9. **Predicción del panel:** P(pasa) ≈ 12–15 %; guarda ΔD ≈ 80 %.

## Respuestas de la ronda 2
- **Biología (07:31):** acepta, sin objeción bloqueante. Hay que registrar que las semillas 0–9 dan el mismo mundo inicial que C. Sugiere escribir que 7–8/10, o una mediana entre 0,02 y 0,04, es indicio no concluyente.
- **Método (07:31):** acepta. Pide que k/2, si hace falta, se aplique a los 20 mundos (b′bar comparte k y sigue siendo el nulo válido) y que conste que la calibración (épocas 50–100) no mira el aprendizaje.
- **Ingeniería (07:31):** acepta. Advierte que W_MAX se mira en la época 100 en la calibración y en la 300 en la tanda: si la saturación crece con la edad, la calibración puede dar luz verde y el resultado acabar no interpretable. Basta con registrarlo.

## Decisión (unánime, 07:31)
La síntesis, con las tres notas. Ver ADR-035.
