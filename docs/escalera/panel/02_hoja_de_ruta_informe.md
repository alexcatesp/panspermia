# Panel 02 · Hoja de ruta hasta la red P2P (25-10-2026, 22:27)

## Pregunta del responsable
«¿Podemos preguntar al panel la hoja de ruta prevista hasta alcanzar un bicho lo suficientemente inteligente y un mundo lo suficientemente complejo para que podamos dar el paso al P2P? ¿O es pronto para esto?»

El panel debe proponer una **hoja de ruta provisional**, que se revisará con cada resultado, desde hoy hasta la fase 4a (red de mundos con tracker). Tiene que incluir:
1. **¿Hay que esperar?** La spec dice que la 4a «puede empezar en paralelo nada más cerrar la 1, porque solo depende del formato de genoma». ADR-012 la puso detrás de la 1d (condiciones del aprendizaje) y de la granja «fuga» (ADR-009). ¿Sigue teniendo sentido esperar? ¿O conviene construir la red en paralelo y conectarla cuando haya algo que merezca migrar? ¿O la migración misma puede ser un ingrediente que favorezca aprender (C10, más retos; flujo génico)?
2. **Criterios medibles de «bicho suficientemente inteligente» y «mundo suficientemente complejo»** para abrir la red. Deben ser coherentes con el principio 1 (ninguna métrica decide la reproducción) y con la sonda mixta y la trampa del alga invertida como medidas de aprendizaje.
3. **Los hitos, en orden,** con lo que añade cada uno (un cambio cada vez), su pregunta de sí o no, el coste estimado en GPU (un mundo de 300 épocas ≈ 36 min en una RTX 5070 Ti; 10 semillas por condición) y las bifurcaciones: qué hacer si sale sí y qué si sale no.
4. **El plan B** si el aprendizaje asociativo no evoluciona en la escalera después de N intentos. ¿Cuántos intentos antes de cambiar de estrategia? Opciones: otra arquitectura de plasticidad (trazas de elegibilidad, moduladoras con otro papel), otra medida, aceptar la maduración como resultado publicable, ir a P5 o a lo social igualmente…
5. **Riesgos principales** del camino y cómo detectarlos pronto.

## Dónde estamos
- Escalera P0–P5 (ADR-014). P0–P3 cerrados: P3-escaso es el mundo base, con hijos pagados por el padre y la mitad de comida.
- P4 (comida que cambia) lleva varios negativos:
  - P4-alga, 3/5.
  - P4-salto64, 2/5, el mejor indicio: cuerpos grandes y cerebros mayores.
  - La tripa, 4/5.
  - Comer frena, 6/10: aprender en vida compensa (+68 %), pero es maduración.
  - Alga por bicho, 0/10: +136 %, pero maduración; la trampa invertida da E − X ≤ 0,013.
  - En marcha, manchas lejanas de un solo tipo (ADR-027). Predicción del panel 01: 1/10.
- Hallazgo firme: cada bicho cambia en vida (sonda mixta, +15 a +166 %), pero es sobre todo maduración. No hay aprendizaje asociativo demostrado. Un reflejo innato de la tripa resuelve los problemas planteados.
- Después de P4 vienen P5 (veneno; ¿compensa aprender?) y P6si (veneno que cambia, señal entre ellos y los demás ingredientes de uno en uno). Luego una ejecución larga con la mejor receta, la granja «fuga» (ADR-009) y la red 4a. Más tarde, el robot (salvaguarda 2, ADR propio), el mundo 3D (fase 2) y la fase 3 (modelo interno del mundo, sexo).
- Visiones del responsable, sin diseñar (memoria): un lenguaje propio emergente y una mente colmena o peldaño social (cultura, robots que comparten lo aprendido).

## Ficheros para leer (rutas absolutas)
- `D:\Development\panspermia\docs\spec.md` (sobre todo «Red P2P», «Fases y criterios de aceptación», «Salvaguardas» y «Riesgos»)
- `D:\Development\panspermia\docs\decisiones.md` (ADR-009, ADR-012, ADR-014 y ADR-024 a ADR-027)
- `D:\Development\panspermia\docs\escalera\diseno.md` (lo general al principio y desde v1.9 hasta el final)
- `D:\Development\panspermia\docs\escalera\condiciones_aprendizaje.md`
- `D:\Development\panspermia\docs\caminos.md`
- `D:\Development\panspermia\docs\mapa.json` (los nodos P4*, P5, P6si, larga, fuga, red, robot y vejez)
- `D:\Development\panspermia\docs\bibliografia\escalera\README.md`
- `D:\Development\panspermia\docs\escalera\panel.md` (lo que el panel puede y no puede decidir)

## Formato de tu respuesta (máximo ~700 palabras, en español)
1. **¿Esperar o no a la red?** Postura y razones.
2. **Criterios de apertura de la red** (medibles).
3. **Hitos en orden** (tabla: hito · qué añade · pregunta · coste en GPU · si sí → / si no →).
4. **Plan B** y regla de parada.
5. **Riesgos** (3–5).
6. **Lo que cambiarías ya**, si algo, del plan actual.

Solo lectura: no modifiques ficheros, no lances procesos y no toques ramas.
