# Panel 01 · Revisión del peldaño «manchas lejanas» antes de calibrar (25-10-2026, 22:12)

## Pregunta
El peldaño P4-manchas-bicho-frena-rampa (ADR-027, `docs/escalera/diseno.md` v2.3) ya está en marcha (suite en GPU desde las 22:08; la calibración empieza hacia las 22:45; los 10 mundos tardan ~6 h). **¿Seguimos tal cual, o hay que cambiar algo (diseño, parámetros, primaria) antes de que empiece la calibración o los 10 mundos?** Opciones:
- A. Seguir tal cual.
- B. Ajustar parámetros (di cuáles y a qué valor).
- C. Cambiar o añadir una medida primaria o secundaria (antes de lanzar: el prerregistro aún se puede tocar).
- D. Parar y rediseñar (di por qué y cómo).

## Contexto (resumen; los números están en la bitácora)
- Proyecto: vida artificial con genoma CPPN, plasticidad hebbiana ABCD con moduladoras y solo selección ecológica (sin fitness explícita). Escalera de complejidad P0–P5, un cambio por peldaño, con una pregunta de sí o no prerregistrada.
- Comer frena (ADR-025): no pasa (6/10). Aprender en vida compensa (sonda mixta: +68 %), pero es maduración (M 0,84).
- Alga por bicho (ADR-026): cada bicho nace con su alga buena sorteada (A o B, sin herencia); la otra se come pero no alimenta. Hay una entrada de «tripa» (energía de lo comido en los últimos 4 pasos). **No pasa (0/10):** no comen más su alga que la otra.
  - La ventaja de aprender es de +136 %, pero la maduración da M 0,97.
  - Los que aprenden pasan más tiempo sobre su alga buena (0,73–0,83 frente a 0,55–0,70).
  - Trampa del alga invertida (criados 200 pasos con su alga o con la invertida; examen congelado): E − X ≤ 0,013 en 10/10, y con el examen barajado entre −0,021 y +0,008. **No aprenden qué alga es la suya: basta un reflejo innato de la tripa**, porque probar es casi gratis.
- Manchas (ADR-027, sustrato 3.5.0):
  - Comida en manchas (`K_CUT` 1,7; 9 % del suelo; 18 manchas de ~71 u a ~177 u de la vecina; sensores ≤ 60 u).
  - Cada mancha de un tipo: dos familias de ondas (pares e impares), z = max(z_A, z_B), tipo A donde z_A ≥ z_B; el 50 % de la comida para cada alga; el 17 % de las componentes son una mancha A y otra B que se tocan.
  - Misma comida total que el padre (`k_mean` 8,792, rampa del doble a la mitad en 100 épocas); freno de comer total en rampa; tripa encendida. Todas las semillas comparten mapa (sale del nodo `fase1d-w0`).
  - Calibración: 3 semillas × 150 épocas (viable: sin extinción, ≥ 500 bichos y población media de las épocas 100–149 < 3.900). Después, 10 semillas × 300 épocas.
  - **Primaria:** trampa del alga invertida con el examen barajado; favorable si `frac_buena`(E) − `frac_buena`(X) ≥ 0,05; pasa con ≥ 9/10. Secundarias: sonda mixta (aprenden frente a congelados, A y `frac_buena`) y su nulo.
- Antecedente: P3-disperso (manchas con `K_CUT` 1,5, sin alga por bicho) no pasó (3/5). P2-buscar (comida dispersa con energía regalada) agotaba la comida. P4-salto64 (manchas que se desplazan 64 u cada 1.000 pasos) fue el mejor indicio (cuerpos grandes, cerebros mayores).

## Ficheros para leer (rutas absolutas)
- `D:\Development\panspermia\docs\escalera\panel.md` (el protocolo del panel y lo que no puede decidir)
- `D:\Development\panspermia\docs\escalera\diseno.md` (lee desde «v1.9» hasta el final)
- `D:\Development\panspermia\docs\escalera\condiciones_aprendizaje.md`
- `D:\Development\panspermia\docs\decisiones.md` (ADR-025, ADR-026 y ADR-027, al final)
- `D:\Development\panspermia\docs\bitacora.md` (las entradas del 25-10, al final)
- `D:\Development\panspermia\docs\bibliografia\escalera\README.md` (§18–§20)
- Código: `D:\Development\panspermia-manchas\src\panspermia\world.py` (`kmax_field`, `_family_fields`, `algae_type_a`), `island.py` (busca `ALGA_PER_AGENT`) y `config.py`.
- Medidas: `C:\Users\aleja\AppData\Local\Temp\claude\D--Development-panspermia\ddea0d1c-f251-40d2-8e99-9e07c65f2199\scratchpad\madura_alga.py` y `sonda_mixta.py`.

## Formato de tu respuesta (máximo ~400 palabras, en español)
1. **Voto:** A, B, C o D (con el cambio concreto si es B, C o D).
2. **Razones** (3–5 puntos, con referencias o números).
3. **Riesgos** del diseño actual que ves, ordenados.
4. **Predicción:** qué crees que saldrá en la primaria (cuántos planetas favorables de 10) y por qué.

Solo lectura: no modifiques ficheros, no lances procesos y no toques ramas.
