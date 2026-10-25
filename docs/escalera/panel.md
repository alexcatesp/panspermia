# Panel de expertos: cómo se toman las decisiones de la escalera

**Decisión del responsable (25-10-2026, 22:11).** Las decisiones de diseño e investigación ya no se le preguntan una a una. Las toma un panel de tres agentes que deben ponerse de acuerdo. Claude modera el panel, ejecuta lo decidido y le cuenta al responsable qué se decidió y por qué. El responsable pregunta, sugiere o corrige cuando prefiera otra cosa, y su palabra prevalece siempre.

## Qué decide el panel

- El siguiente peldaño o rama tras un resultado, y qué única cosa añade.
- Los parámetros de diseño y calibración: cortes, comida, rampas, número de semillas.
- La medida primaria y su umbral, que se prerregistran en `diseno.md` **antes** de lanzar.
- Qué diagnóstico hacer ante un negativo, y cuándo aparcar o reabrir un camino.

## Qué NO decide el panel (sigue siendo del responsable)

- Subir umbrales de la batería (salvaguarda 5) o firmar `CAPABILITY_REVIEW.json`.
- Cambiar los principios innegociables de `CLAUDE.md` o de la spec.
- Cualquier acción externa o difícil de deshacer: borrar datos, publicar o gastar dinero.
- Cambios de rumbo del proyecto: abandonar la escalera, saltar de fase o integrar en `main`.

## Los tres expertos

1. **Biología evolutiva y del aprendizaje.** Qué predice la bibliografía, sobre todo `docs/escalera/condiciones_aprendizaje.md` y `docs/bibliografia/escalera/`. Qué condición falta y qué peldaño la aísla.
2. **Método experimental y estadística.** Un cambio cada vez, controles y nulos, confusiones (por ejemplo, la maduración), potencia (10 semillas, prueba de signos), prerregistro y si la medida responde de verdad a la pregunta.
3. **Ingeniería de vida artificial y cómputo.** Viabilidad (extinción, tope), coste en GPU, riesgo de implementación, determinismo y cambios de sustrato, y qué se puede reutilizar.

## Procedimiento

1. Claude prepara un **informe común**: la pregunta, el resultado que la motiva (con números), las opciones que ve y los ficheros que hay que leer. Cada experto puede añadir opciones.
2. **Primera ronda, por separado:** cada experto lee, ordena las opciones y vota una, con sus razones, sus riesgos y lo que predice que saldrá.
3. Si los tres coinciden, queda decidido. Si no, hay una **segunda ronda**: cada uno ve los argumentos de los otros y vota de nuevo. Decide la mayoría y la discrepancia queda anotada.
4. Claude ejecuta y lo **registra**: en `docs/decisiones.md` («Decisión del panel», con hora real, votos y razones), en la bitácora y en el mapa. Al responsable le cuenta qué se decidió, por qué y qué alternativas se descartaron.
5. Las decisiones menores y técnicas que no cambian la pregunta, como arreglar un error o elegir un nombre, las sigue tomando Claude sin panel.

Los agentes del panel solo leen y razonan: no tocan ficheros, no lanzan trabajos y no cambian ramas.
