# Panel 03 · Segunda ronda (25-10-2026, 22:36)

## Coincidencias
- **No estamos preparados** para pedir cómputo a voluntarios.
- **Paquete de la puerta BOINC.** Hay que cumplirlo entero y prerregistrado:
  - **(a) Aprendizaje asociativo real:** el criterio del bicho de la hoja de ruta, más el control positivo y negativo, la ablación de la plasticidad y que M deje de explicar la ventaja.
  - **(b) Crecimiento abierto:** el archivo de novedad y la batería crecen en la mitad tardía de una ejecución larga, más que en un nulo de deriva. La batería da ≈ 0 con la política fija y con genomas al azar.
  - **(c) Escalado:** la capacidad C de (a) o (b), no una aproximación, frente al cómputo. Al menos 3 puntos por eje (N, islas o épocas, uno a la vez), con la pendiente log-log y su IC95 por encima de 0, y la densidad fija.
  - **(d) Reproducibilidad entre máquinas:** bit a bit entre dos GPU distintas (5070 y 5070 Ti) o con una tolerancia declarada, y datos abiertos.
  - **(e) Un resultado intermedio comprensible** para un donante.
- **Frente a los LLM:** no decir «más relevante». Defendible: «Estudiamos si el aprendizaje puede emerger de la selección ecológica; tenemos herramientas de medida rigurosas y, todavía, ningún aprendizaje asociativo demostrado.» Ciencia básica, complementaria a los LLM.
- **Antecedentes (de memoria; verificar antes de citar en un ADR):**
  - Network Tierra: sin una pregunta medible ni el fenómeno en una sola máquina, distribuir no añade nada.
  - Avida: convenció por una métrica clara con nulos.
  - POET: la coevolución entre el entorno y el agente evita el estancamiento.
  - Folding@home: la gente dona por una pregunta concreta y un avance visible, con unidades de trabajo verificables por réplica (aquí ayuda el determinismo).

## Discrepancia: ¿el experimento de escalado ya?
- **Biología:** ya, con la escalera de N (1.024, 4.096 y 16.384) sobre la mejor receta; 6–15 h.
- **Método:** solo con una C que pase la trampa del alga invertida. Escalar maduración o reflejos es el artefacto más probable.
- **Ingeniería:** un factorial N × épocas sobre el mejor peldaño, varios días de GPU, con la densidad fija.

**Síntesis del moderador:**
1. **El escalado (c) espera a tener una C válida**, de (a) o (b). Coincide con Método: la GPU sigue con la hoja de ruta (H1 manchas, H2 veneno diferido, H3). Escalar hoy mediría maduración.
2. **Lo que sí se hace ya, barato y sin quitar GPU a la hoja de ruta:**
   - (b0) **Validar una medida de crecimiento abierto** contra nulos, con los datos que ya existen. Por ejemplo, la pendiente del archivo de novedad y de la batería en las ejecuciones de 600 épocas de P2 y en las de 300 épocas de la escalera, frente a genomas al azar o a un nulo de deriva. Solo observa, en CPU ligera.
   - (d0) **Comprobar el determinismo entre la 5070 y la 5070 Ti** (100 épocas, misma semilla) cuando la otra máquina esté disponible. Hay que preguntar al responsable si lo está: es una acción en su hardware.
3. **El primer experimento de escalado**, cuando exista C: la escalera de N con densidad fija (Biología e Ingeniería), 5 semillas por punto y 10 si hay señal; después épocas, y las islas con P-migra.

Responde en menos de 120 palabras: **ACEPTO** o **RECHAZO** (con el cambio).
