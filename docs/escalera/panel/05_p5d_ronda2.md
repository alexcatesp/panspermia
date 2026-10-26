# Panel 05 · Segunda ronda: síntesis de P5-d (26-10-2026, 06:30)

## Coincidencias (los tres)
- **Diagnóstico de crianza larga: sí.** Se prerregistra como exploratorio y se hace en paralelo. No bloquea P5-d ni gasta comparación.
- **Mecanismo:** el alga equivocada de cada bicho daña en diferido. El daño es en energía, con retardo fijo de 30 pasos (el variable se aparca), y se conservan el diseño E/X y la comida total.
- **Primaria:** la trampa del alga invertida con examen barajado, E − X ≥ 0,05 en ≥ 9/10. En X, el alga que daña durante la crianza es la contraria.
- **Secundaria:** ingestas (y P(comer)) del alga equivocada tras la crianza, con la sonda mixta.
- **Contraste inmediato:** entra en H2, con retardo 0, la misma magnitud y 10 semillas.
- **Plasticidad:** se prueba con la actual y se declara de antemano que, sin trazas de elegibilidad, la literatura predice un negativo. La recurrencia h no se da por supuesta: se mide.
- **Sustrato y calibración:** sustrato 3.6.0 (Ingeniería):
  - un búfer circular `pending f32[N, 64]` que se reinicia al nacer y al morir;
  - apagado, idéntico bit a bit;
  - un test de que el daño llega exactamente a los `delay` pasos.
  - El daño sube en rampa y se calibra antes de abrir datos.
- **Predicción común:** el diferido no pasa (0–2/10, con un 80–85 % de confianza).

## Discrepancias y síntesis del moderador
1. **Padre.** Método e Ingeniería votan manchas; Biología, el alga mezclada (un cambio cada vez).
   → **Manchas (2–1).** Tiene el negativo más limpio y la trampa validada. Con el alga mezclada, probar y corregirse es gratis.
2. **Un punto que nadie cerró: ¿el alga equivocada da energía al comerla?** Hoy no da (ADR-026). Por eso la tripa calla sobre ella y el reflejo ya la evita. Si sigue sin dar energía, el daño diferido no cambia nada que el reflejo no resuelva ya. Biología la dejaba sin energía o con poca; Ingeniería suponía una ganancia inmediata positiva.
   → **Propuesta: el alga equivocada alimenta al comerla igual que la buena** (la tripa la registra como buena, que es el reflejo engañado de García), **y a los 30 pasos cobra F × lo que dio**, con F > 1 para que el neto sea negativo.
   - Calibración con dos valores, F = 1,5 y F = 2,5. La F sube en rampa de 0 al valor final en 100 épocas, como la rampa de comida.
   - Se toma el F más dañino que sea viable con el criterio de la v2.3b.
   - En el contraste inmediato, el cobro llega en el mismo paso y la tripa ve el neto. En el diferido, la tripa solo ve el bocado.
3. **Señal de malestar.** Biología quiere un brazo con malestar; Método e Ingeniería, no (es otro factor, y E9 es 3.0.0).
   → **Sin señal (2–1).** El malestar queda aparcado como el siguiente paso si el inmediato pasa y el diferido no. La objeción de Biología queda anotada.
4. **Si el inmediato también falla.** Método dice que entonces el diferido no gasta H2.
   → **Propuesta:** si el inmediato da ≤ 3/10, ni siquiera con la consecuencia inmediata se aprende el valor del alga. Sería el tercer negativo sobre el mismo mecanismo: alga por bicho, manchas e inmediato. H2 cuenta como negativo, y el panel decide si salta H3 y pasa directamente al plan B 1 (trazas de elegibilidad), porque el cuello de botella sería la plasticidad y no el mundo. Si el inmediato pasa y el diferido no, el negativo es informativo y apunta igual al plan B.
5. **Trazas de elegibilidad en paralelo** (Biología e Ingeniería).
   → **Sí, solo código y tests en CPU.** Rama propia, sustrato 4.0.0, sin lanzar mundos hasta que la regla lo pida.
6. **Regla del indicio** (cada uno proponía una variante).
   → El indicio exige todo esto a la vez:
   - E − X > 0 en ≥ 7/10;
   - mediana ≥ 0,03 y mayor que 2 × la mediana de |E − E2|;
   - los cerebros barajados dan ≈ 0.
   - Siempre exige réplica. El contador pasa a 13 (diferido e inmediato).

Responde en menos de 150 palabras: **ACEPTO** o **RECHAZO**, punto por punto si discrepas (1–6).
