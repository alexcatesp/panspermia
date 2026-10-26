# Panel 04 · Segunda ronda: síntesis de (b0) (26-10-2026, 02:51)

## Coincidencias (los tres)
- **Medida primaria:** la tasa de altas al archivo de novedad, `novelty_added`, por época, en una ventana tardía. Es una tasa y no un nivel: `archive_size` es acumulado, monótono y satura.
- **Nulo de deriva:** P0-escalera (5 × 300). Hay que declarar en qué difiere:
  - la población (4.096);
  - el artefacto de `repro_age`, que en P0 sube solo con la edad porque no hay vejez;
  - que no hay muertes.
- **Barajar la serie en el tiempo no sirve como nulo de deriva.**
- **Todo es exploratorio, con n = 5, y no decide nada por sí solo.** Solo dice si la medida es utilizable, no si hay crecimiento abierto.
- **CPU ligera:** solo se leen JSON.
- **Predicción común:** la tasa tardía será casi nula por saturación. El veredicto más probable es «no vale» o «no se puede saber».

## Discrepancias y síntesis del moderador
1. **`bp_*`.** Método y Ingeniería la descartan o aparcan: escala con la población, no tiene modelo sombra y no está claro cómo define los clados. Biología la quiere como segunda medida, normalizada por la población.
   → **Solo descriptiva**, normalizada por la población media de la ventana, sin decidir. Es lo que vota la mayoría.
2. **Ventana.** Método e Ingeniería proponen las épocas 150–300; Biología, 200–300 más un índice de saturación.
   → **Ventana primaria 150–300**, la mayoría. Se añade el índice de saturación de Biología como secundaria descriptiva: la tasa de 225–300 dividida por la de 150–225. Por debajo de 0,5 se lee como «se satura».
   → Las ejecuciones de 600 épocas también se miran en 300–600, de forma descriptiva y frente a su propia ventana 150–300.
3. **Criterio de «la medida vale».** Combina el control positivo de Ingeniería con la separación del nulo de Método y Biología. Se tienen que cumplir las dos condiciones:
   - **(i) Control positivo:** los mundos cambiantes superan a los estables. Los cambiantes son P4-salto64 y P4-alga; los estables, el conjunto de P2-escalera y P3-escaso (10 semillas). Cada ejecución cambiante tiene que tener ≥ 4/5 semillas por encima de la mediana de ese conjunto estable.
   - **(ii) Dirección frente al nulo:** la mediana de los mundos con selección (P1, P2 y P3-escaso) tiene que ser mayor que la de P0. Además, ≥ 4/5 semillas de P2 tienen que quedar por encima de la mediana de P0.
   - **«No vale»:** falla (i), o P0 queda por encima o a la par de los mundos con selección. En ese caso la medida mide deriva.
   - **«No se puede saber»:** la mediana es < 1 alta por época en todas las ejecuciones, incluida P0 (es el suelo), o hay menos de 512 adultos de media en la ventana.
4. **Medida secundaria de complejidad.** Método propone `hidden_mean + synapses_mean`; Biología e Ingeniería la ven inútil, porque el cerebro se vacía.
   → **Solo descriptiva:** la pendiente en 150–300, que se espera negativa.
5. **Sensibilidad.** Se informa cuántos descriptores `desc_*` varían en cada ejecución. También se informa la media de `desc_repro_age`, para dejar a la vista el artefacto de P0.

Responde en menos de 120 palabras: **ACEPTO** o **RECHAZO** (con el cambio concreto).
