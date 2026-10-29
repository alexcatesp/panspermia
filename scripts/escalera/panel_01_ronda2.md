# Panel 01 · Segunda ronda (25-10-2026, 22:15)

Votos de la primera ronda:
- Biología: **A** (seguir), y añadir secundarias: tiempo dentro de la mancha equivocada, manchas visitadas por vida (C5) y abandono tras un bocado sin tripa.
- Método: **C**. Prerregistrar el tipo de la primera comida tocada (con `frac_buena` después del primer contacto) y un nulo de ruido con una segunda baraja.
- Ingeniería: **B + C**. Calibrar 200 épocas en vez de 150, porque las dos rampas acaban en la época 100. Añadir la selectividad de entrada: la fracción de entradas a una mancha que son de la propia, con E frente a X.

Nadie pide parar ni tocar la primaria. El moderador propone esta **síntesis** y pide aceptarla o rechazarla:
1. **Diseño, parámetros y primaria, tal cual** (E − X de `frac_buena` ≥ 0,05, ≥ 9/10, con el examen barajado).
2. **Calibración a 200 épocas.** La ventana de viabilidad pasa a ser la de las épocas 100–199 (el script toma las épocas ≥ 100) y no puede haber extinción en ninguna. Solo cambia `manchascal.json`, porque el script de la cadena no se puede editar mientras corre.
3. **Secundarias prerregistradas** en el examen barajado, para los cinco cerebros (N, E, X, D, A):
   - a. **Selectividad de entrada:** de los pasos en que un bicho pasa de fuera de la comida a dentro, la fracción que son de su alga buena. Es la medida directa de «elegir por el color antes de probar», y engloba el tipo del primer contacto.
   - b. **Primer contacto:** el tipo de la primera casilla con comida que pisa cada bicho tras barajar.
   - c. **Entradas por bicho** en los 500 pasos (proxy de C5) y **tiempo medio por visita** en la propia y en la ajena (permanencia).
   - d. **Nulo de ruido:** el examen de E repetido con una segunda baraja; |E₁ − E₂| de `frac_buena` y de la selectividad de entrada, por mundo.
4. **Al interpretar:** los 10 mundos comparten mapa (`fase1d-w0`); la conclusión vale para este mapa. Con un efecto real en el 7–50 % de los linajes (C8), 9/10 es exigente: un resultado como 3–8/10, con la selectividad de entrada a favor, se contará como indicio y no como negativo.

**Objeción del moderador al riesgo 1 de Método** (que la primaria dé falsos positivos por un reflejo reforzado de «quedarse si suena la tripa»): en la crianza X la tripa también suena, aunque sobre la otra alga. Una regla de «quedarse si suena la tripa» que no dependa del color la aprenden igual E y X, y se anula al restar. Solo una regla que dependa del color (aprendizaje de verdad) separa E de X. ¿Estás de acuerdo?

Responde en menos de 150 palabras: **ACEPTO** o **RECHAZO** (con el cambio que pedirías), y si te convence la objeción.
