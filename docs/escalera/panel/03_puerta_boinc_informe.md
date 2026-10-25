# Panel 03 · La «puerta BOINC»: qué pruebas hacen falta para pedir ordenadores (25-10-2026, 22:35)

## Lo que dice el responsable
«Mi idea de la red era una especie de proyecto BOINC. Pero habría que tener resultados sólidos para convencer a la gente de que estamos ante algo que será más relevante para el desarrollo de la IA que los LLMs. Necesitamos pruebas sólidas. Por eso me preguntaba si estábamos preparados para ese salto.»

La hoja de ruta (`docs/escalera/hoja_de_ruta.md`, ADR-028) fija cuándo se conecta la red como ciencia, pero no qué paquete de pruebas justificaría **pedir cómputo a voluntarios**. Define esa puerta.

## Pregunta
1. **¿Qué pruebas, medibles y prerregistrables, convencerían a un público técnico escéptico de que donar cómputo a Panspermia tiene sentido?** Piensa en al menos estas tres familias:
   - (a) **aprendizaje real**: asociativo, replicado, no maduración;
   - (b) **crecimiento abierto**: capacidades nuevas que siguen apareciendo con el tiempo, sin techo visible (archivo de novedad, batería de capacidades);
   - (c) **escalado con el cómputo**: más islas, más agentes o más tiempo dan medible más capacidad, con una curva.

   (c) es lo que justifica BOINC: si el doble de cómputo no da nada, no hay razón para pedirlo.
2. **Honestidad sobre «más relevante que los LLM».** ¿Qué afirmación es defendible y cuál no? ¿Cómo se debería plantear (complementaria, ciencia básica sobre el origen del aprendizaje, etc.)?
3. **Antecedentes que hay que tener en cuenta:** Network Tierra (Ray, años 90: evolución distribuida por internet), Avida, Polyworld, POET y la literatura de evolución abierta, Folding@home y BOINC (por qué la gente dona). ¿Qué aprendemos de ellos? ¿Qué falló en Network Tierra?
4. **¿Qué experimento de escalado barato** se puede hacer ya, en una sola GPU, para saber pronto si (c) tiene alguna posibilidad? Por ejemplo, 1 frente a 3 frente a 9 islas simuladas en local con migración, N = 1.024, 4.096 o 16.384, o épocas 300 frente a 3.000.
5. **Respuesta corta para el responsable:** ¿estamos preparados? Si no, ¿a qué distancia, en hitos, estamos?

## Contexto
- Estado actual, hallazgos y hoja de ruta: `D:\Development\panspermia\docs\escalera\hoja_de_ruta.md` y `D:\Development\panspermia\docs\escalera\panel\02_hoja_de_ruta_ronda2.md`.
- Spec (fases 2–4, red P2P, salvaguardas y riesgos): `D:\Development\panspermia\docs\spec.md`.
- Visión del proyecto y estado: `D:\Development\panspermia\README.md` y `D:\Development\panspermia\CLAUDE.md`.
- Resumen de lo hallado: no hay aprendizaje asociativo demostrado. Lo que mejoran en vida es maduración (M 0,84–0,97) más un reflejo innato de la tripa. Los cerebros se vacían en mundos estables. Lo publicable hoy son los diagnósticos metodológicos (sonda mixta, trampa del alga invertida, falsos positivos de la batería, sesgo de la mutación).

## Formato (máximo ~600 palabras, en español)
1. **Paquete de pruebas** de la puerta BOINC (lista con criterio medible para cada prueba).
2. **Cómo plantearlo honestamente** frente a los LLM.
3. **Lecciones de los antecedentes.**
4. **Experimento de escalado barato** que propones ya (diseño, coste en GPU y pregunta de sí o no).
5. **¿Estamos preparados?** Respuesta en 2–3 frases.

Solo lectura: no modifiques ficheros ni lances procesos.
