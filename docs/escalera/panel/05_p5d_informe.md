# Panel 05 · Tras las manchas: diseño de H2, P5-d (veneno diferido) (26-10-2026, 06:26)

## Resultado que lo motiva
Manchas lejanas de un solo tipo (ADR-027), 10 × 300 épocas, terminado el 26-10 a las 06:22. Detalle en `docs/bitacora.md`, última entrada.

- **Primaria: no pasa (0/10).** frac_buena E − X entre −0,021 y +0,012 (mediana −0,004). Ruido |E − E2| ≤ 0,019.
- **Secundarias:** la selectividad de entrada E − X queda entre −0,013 y +0,016, sin indicio. El primer contacto, las entradas y los pasos por visita son iguales en E y X.
- **Lo que mejora con la crianza:**
  - frac_buena: N 0,55 → D 0,62 → E 0,71 ≈ X 0,72 → A (adulto) 0,77.
  - M mediana 0,49 (padre 0,97): pesa la experiencia con comida, pero no la de su alga.
  - **El adulto supera a E en 9/10** (+0,03 a +0,08). Vive ~640 pasos y la crianza dura 200. No existe un «adulto con el alga invertida», así que no se sabe si esa parte extra depende del alga.
- **Sonda mixta:** A +135 % (nulo +0,6 a +12,8 %), ΔD ≈ 0. Viables 10/10.
- **H-control** (26-10, 02:44): la trampa detecta una taxia impuesta a mano (positivo 10/10, débil 9/10, negativo 10/10). Las medidas valen, y el negativo es real.
- **Contador de comparaciones:** 11. H1 está gastado (regla de parada, ADR-028, `docs/escalera/hoja_de_ruta.md` §4).

## Lo que toca según la hoja de ruta
**H2: P5-d, veneno diferido.** El daño llega entre 20 y 50 pasos después de comer, con el veneno inmediato como contraste prerregistrado si cabe (10 semillas más). La pregunta es si aparece la discriminación cuando el reflejo de la tripa ya no basta. Biología lo propuso en el panel 02: el daño inmediato lo resuelve otra vez el reflejo.

## Preguntas
1. **¿Un diagnóstico barato antes de P5-d?** Por ejemplo, la trampa con crianza larga: 600 pasos, para E y X. Separaría si la ventaja del adulto sobre E depende del alga. Solo observa; unos 20–40 min de GPU sobre los checkpoints de manchas y del alga por bicho. ¿Vale la pena, o es un desvío?
2. **Diseño de P5-d:**
   - **Padre:** ¿P4-alga-bicho-frena-rampa (alga mezclada) o manchas (ADR-027)?
   - **Mecanismo:**
     - ¿Un alga tóxica (como en la fase 1b: `tox_mode`, `TOXIC_FACTOR`), o la propia «alga equivocada» de cada bicho, que pasa a dañar en diferido?
     - ¿El retardo es fijo o variable (20–50 pasos)?
     - ¿Daño en energía, o en salud o malestar? La rama `fase1d-e9` tiene una entrada de malestar (3.0.0; no mezclar 3.x).
     - ¿Hace falta una señal sensorial del daño (malestar) que la plasticidad pueda usar, o basta la energía?
   - **Qué ve el bicho:** el color del alga, con el signo del canal de recurso (ya existe).
   - **Primaria prerregistrada:** ¿la trampa del alga invertida otra vez (en X, la tóxica para la crianza es la contraria), o una medida de evitación (P(comer | tóxica) aprendida)?
   - **Contraste inmediato:** ¿entra o se aparca?
   - **Calibración y viabilidad:** cuánto daño, cuánta comida y si hace falta rampa.
3. **La plasticidad actual (ABCD con modulación inmediata)** puede no unir comer con un daño que llega 20–50 pasos después: no hay trazas de elegibilidad. ¿Se prueba igual P5-d con la plasticidad actual (para que el negativo cuente para la regla de parada), o eso es diseñar un fracaso seguro? ¿Hay alguna forma, dentro de la física actual, en que la recurrencia h haga de memoria?
4. **Predicción y regla del indicio.**

## Ficheros
- `docs/escalera/hoja_de_ruta.md`, `docs/escalera/diseno.md` (v2.0–v2.3b) y `docs/escalera/condiciones_aprendizaje.md`.
- `docs/decisiones.md`: ADR-024 a ADR-029, y la fase 1b y E9 si se citan.
- Código de la rama actual: `D:\Development\panspermia-manchas\src\panspermia\` (world.py: `toxic_cells`, `eat`, `good_alga_a`; island.py: `world_step`, la tripa; brain.py: plasticidad; config.py: TOXIC_*, GUT_*).
- La rama E9, solo para ver la entrada de malestar: `D:\Development\panspermia-e9\src\panspermia\`.

## Formato (máximo ~500 palabras, en español)
Voto sobre el diagnóstico (1) · diseño cerrado de P5-d (2) · postura sobre la plasticidad (3) · predicción. Solo lectura: no modifiques ficheros ni lances procesos.
