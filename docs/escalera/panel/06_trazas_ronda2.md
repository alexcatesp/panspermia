# Panel 06 · Segunda ronda: síntesis de las trazas de elegibilidad (26-10-2026, 06:38)

## Coincidencias (los tres)
- **Regla de tres factores sobre el hebbiano completo:** A·xi·xj + B·xi + C·xj + D. η y g multiplican al consolidar. Con λ = 0 se recupera la regla actual.
- **Cadencia:** la traza se actualiza y se consolida cada `PLASTICITY_EVERY` = 4 pasos, con λ = exp(−4/τ).
- **Reinicio:** a 0 al nacer (`_place`) y al morir, como `gut` y `poison`.
- **Se aparca:** la recompensa predicha, λ por sinapsis (CPPN_OUT 9), las trazas por término y las dos escalas.
- **Primer uso**, cuando lo pida la regla de parada: P5-d diferido con un solo cambio (las trazas), 10 semillas y la misma primaria. El control es el P5-d actual.
- **Junto a la primaria se miden:** la fracción de neuronas moduladoras expresadas (sin m la traza es inerte) y la maduración (M).
- **Memoria:** tests en CPU con N pequeño (≤ 256) y el pico medido, no estimado.

## Discrepancias y síntesis del moderador
1. **Acotación de la traza.** Método y Biología proponen e ← λ·e + hebb, con un recorte a ±E_MAX. Ingeniería propone e ← λ·e + (1 − λ)·hebb, una media ponderada acotada por max|hebb|. Sin ese factor, los términos constantes B, C y D se acumulan hasta 1/(1 − λ) ≈ 10 veces.
   → **Forma normalizada de Ingeniería:** no hace falta un E_MAX nuevo, y con λ = 0 coincide igual con la regla actual. El precio es que el crédito inmediato pesa (1 − λ) veces menos. Se acepta porque η evoluciona y lo compensa.
2. **λ.** Método e Ingeniería: una constante global, `config.TRACE_TAU` = 40 pasos. Biología: un gen escalar por bicho, de 4 a 150 pasos en escala logarítmica, con un gemelo de τ fijo.
   → **Constante τ = 40 (2–1).** El gen queda aparcado como siguiente paso si la traza constante funciona. Se reabrirá con el gemelo de τ fijo que propone Biología.
3. **Versión.** Con λ constante el genoma no cambia, solo el estado (como `poison`).
   → **Sustrato 3.7.0** (menor), rama `escalera-trazas` desde `escalera-veneno`. Al reanudar checkpoints sin traza, se rellena con ceros.
4. **Interruptor.** → **`config.TRACE_ON`**, una opción de compilación estática como el resto de la escalera. Apagado, se ejecuta exactamente el código actual.
5. **Tests** (unión de los tres):
   - (a) apagado, idéntico bit a bit tras 200 pasos; encendido con λ = 0, idéntico, con tolerancia solo si lo impide el orden de las operaciones en flotante;
   - (b) crédito diferido a mano: Δw = (1 − λ)·λ^k·hebb en t + 30; 0 sin traza; ≈ 0 en t + 300;
   - (c) control positivo del mecanismo (Método): una tarea mínima de condicionamiento con retardo (estímulo, 30 pasos, recompensa), con pesos fijos y sin evolución, que se aprende con traza y no sin ella;
   - (d) acotación con entradas adversarias, sin NaN y con |w| ≤ W_MAX;
   - (e) determinismo y reinicio al nacer y al morir;
   - (f) memoria con N pequeño.
6. **De paso:** se corrige el docstring de `brain.py`, que dice N_PRE 134 y N_POST 69 cuando son 144 y 72.

Responde en menos de 120 palabras: **ACEPTO** o **RECHAZO** (con el cambio concreto).
