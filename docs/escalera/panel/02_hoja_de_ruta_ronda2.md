# Panel 02 · Segunda ronda: síntesis de la hoja de ruta (25-10-2026, 22:29)

## Coincidencias (los tres)
- **Red 4a: construirla ya, en paralelo, sin GPU** (rama `red`, CPU, genomas sintéticos, *fuzzing*; nunca a la vez que un barrido pesado por la memoria). **No conectarla** como ciencia hasta cumplir los criterios. La migración entra después como **peldaño propio** (P-migra, un solo cambio), con islas que difieran de verdad (por ejemplo, otra alga buena u otro mapa). ADR-012 queda matizado: se construye ahora y se conecta después.
- **Criterio del bicho** para abrir la red como ciencia, todo a la vez:
  - la trampa del alga invertida, E − X ≥ 0,05 en ≥ 9/10;
  - `sel_entrada` E − X mayor que |E − E2|;
  - **replicado en un segundo mapa** (otro nodo distinto de `fase1d-w0`).
- **Criterio del mundo:** al menos dos presiones independientes activas, viable 10/10 durante 300 épocas y la batería limpia. **Criterio de la plataforma:** el de la spec (3 nodos 7 días, 0 corruptos en 10⁵).
- **Plan B en este orden:**
  1. Cambiar el mecanismo de plasticidad: trazas de elegibilidad en ABCD o una moduladora de recompensa predicha. Sustrato major, en rama propia.
  2. Publicar la maduración como resultado: es un hallazgo firme y bien medido.
  3. Lo social: Biología lo descarta sin aprendizaje individual.
- **Rigor:**
  - un contador de comparaciones en la bitácora (cuántas variantes llevamos con el umbral 9/10);
  - tamaños de efecto con intervalos, además de la prueba de signos;
  - los criterios y la regla de parada se fijan **antes** del resultado de las manchas.

## Discrepancias y propuesta del moderador
1. **Siguiente peldaño tras las manchas.** Método e Ingeniería ponen P5, el veneno fijo. Biología pide **un veneno con daño diferido** (de 20 a 50 pasos), porque el daño inmediato lo resuelve otra vez el reflejo de la tripa. **Propuesta: el P5 de la escalera será el veneno diferido** (P5-d). Hay dos razones: P5 aún no está diseñado, y es el único ingrediente que ataca directamente el atajo del reflejo, que ha explicado todos los negativos. El veneno fijo e inmediato queda como control dentro del mismo peldaño si cabe en la GPU (10 semillas más) o se aparca.
2. **Regla de parada.** Método propone 3 diseños independientes; Biología, 3 más desde hoy; Ingeniería, 4. **Propuesta: 3 diseños independientes desde hoy**, cada uno con un cambio de estructura del mundo y no de parámetros: manchas (H1), veneno diferido (H2) y uno más que decida el panel, o la réplica en otro mapa si H1 o H2 dan indicio. Si ninguno pasa (≥ 9/10 con la selectividad a favor) ni da un indicio replicado, se cambia de mecanismo (plan B 1) sin más mundos.
3. **Integrar ramas (H0 de Ingeniería).** Hay 17 ramas sin integrar y `main` sigue con el examen contaminado (ADR-021). **Propuesta:** el moderador la hace en paralelo, en CPU y sin bloquear la GPU. Rama de integración desde `escalera-manchas`, examen limpio en `main` y formato de genoma congelado y versionado. La suite en GPU solo cuando la GPU esté libre. No bloquea ningún peldaño.
4. **Control positivo (Método)** antes de interpretar las manchas: un cerebro con el aprendizaje que buscamos impuesto a mano. Por ejemplo, a E se le añade un peso que lleva del canal del alga propia al empuje hacia ella, y a X el contrario. Las medidas (`frac_buena`, `sel_entrada`) **deben detectarlo** (E − X claramente > 0,05). Si no lo detectan, la prueba no sirve y hay que rehacerla. **Propuesta:** hacerlo ya sobre los mundos del alga por bicho, que solo observa y es barato, antes de que acaben las manchas.

## Hitos resultantes (provisional)
H-red (paralelo, CPU) · H-int (paralelo, CPU) · H-control (ya) → H1 manchas → H2 P5-d veneno diferido → H3 (decide el panel o réplica en otro mapa) → [si sí] P6 (veneno cambiante, un ingrediente cada vez) → larga → P-migra (3 islas distintas frente a aisladas) → granja «fuga» → 4a real. [Si no tras H3] → plan B 1 (mecanismo).

Responde en menos de 150 palabras: **ACEPTO** o **RECHAZO**, punto por punto si discrepas (1–4).
