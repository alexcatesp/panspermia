# Informe de auditoría independiente

15-11-2026 · Claude Fable 5.2 · solo lectura (no se lanzó ningún mundo ni se modificó código o documentos; los análisis se hicieron en CPU sobre datos ya generados).

Niveles usados: **[V]** verificado por mí en datos o código · **[Va]** verificado por un ayudante de lectura, no recomprobado por mí · **[P]** afirmación del proyecto · **[I]** inferencia mía.

## 1. Veredicto

**Camino parcial. Confianza media-alta.**

El método es honrado y los instrumentos son buenos, pero el proyecto lleva cuatro semanas persiguiendo una meta intermedia (aprendizaje asociativo «a dónde ir») que nadie ha demostrado que sea requisito de la meta declarada (apertura evolutiva), y la meta declarada no se mide desde el 16-10. El único positivo (C) es real, pero se consiguió con una señal de recompensa puesta a mano que contradice la letra de la spec, y no da ninguna ventaja absoluta a los bichos. El hallazgo que se propone publicar («la ventaja de aprender es maduración») tiene una explicación alternativa sin descartar que un revisor verá enseguida: los pesos innatos están limitados a ±1 y los aprendidos a ±4. Además, el proyecto está parado desde el 30-10 con b′ a medio medir.

## 2. En palabras sencillas

Queríamos saber si en estos mundos siguen apareciendo cosas nuevas sin parar. Para eso alguien pensó que primero los bichos tenían que aprender, y llevamos un mes intentando que aprendan a ir hacia su comida buena. No lo hacen. Lo único que aprenden es a distinguir qué comer, y solo cuando les damos nosotros un «chivato» que les dice si el bocado fue bueno; aun así, no comen más que los bichos sin chivato. Mientras tanto, nadie ha vuelto a mirar la pregunta original. Y lo que parecía el gran descubrimiento (que los bichos «maduran» en vez de aprender) puede ser solo una rareza de cómo está hecho el programa: al nacer no se les deja tener conexiones fuertes, y solo pueden conseguirlas viviendo. Hay que comprobarlo antes de contarlo. El trabajo está hecho con cuidado y sin trampas; lo que falla es hacia dónde apunta.

## 3. Hallazgos, por importancia

### H1. Deriva de objetivo: la apertura evolutiva no se mide y su único criterio no discrimina

- **Evidencia.** La spec fija como meta «sostener la aparición de novedad conductual» (`spec.md` §Objetivo). La fase 1 quedó «no aceptada formalmente» (ADR-010) [Va]. Desde el 16-10 novedad, grupos y clados solo aparecen como descriptores; ningún peldaño tiene criterio de apertura [Va]. El único intento posterior, (b0), dio «no vale» (bitácora 26-10, 02:51) [P] y la línea no se reabrió en los paneles 05–10 [Va]. El criterio de la spec «silueta ≥ 0,3 durante 50 épocas» lo cumple el nulo sin selección P0 en 150 de 150 épocas tardías [Va]. MODES nunca se implementó; Bedau-Packard está simplificado y sin modelo sombra (ADR-007) [Va].
- **Sobre si aprender es condición previa.** A favor solo hay un argumento («lo social no tendría qué compartir», hoja de ruta §4) [P]; no hay ningún dato. En contra tampoco hay datos, porque no se ha medido. Sistemas de referencia con dinámica abierta medible (Avida, POET) no dependen de aprendizaje en vida [I, de conocimiento general, sin verificar en la bibliografía del proyecto].
- **Consecuencia.** No se puede decir si el proyecto se acerca o se aleja de su meta.
- **Acción.** Recomendación 3.

### H2. La «maduración» puede ser un artefacto de la codificación

- **Evidencia.** `develop.py`: `w0 = W_INIT_SCALE * tanh(o)` con `W_INIT_SCALE = 1.0`; `W_MAX = 4.0` (rama `escalera-c`, `config.py`) [V]. Los pesos innatos no pueden pasar de ±1; los plásticos llegan a ±4. En C, el |w| medio de los adultos es 1,59 (s0) y 2,04 (s1), con |w − w0| de 1,44 y 1,97 (`_wmax_c.jsonl`) [V]: los adultos viven fuera del rango que el genoma puede escribir al nacer. El recién nacido «apenas empuja» (velocidad 0,2–4 frente a 8–15 tras la crianza, con o sin comida; `_madura.jsonl`) [V]. Ningún documento menciona `W_INIT_SCALE` ni este tope (búsqueda en `docs/`) [V].
- **Lectura [I, confianza media].** La plasticidad sería la única vía para tener conexiones fuertes; «madurar» sería escapar del tope, no un programa de desarrollo. Alternativa compatible: no hay entrada de edad, y la plasticidad hace de reloj («quédate donde nació tu madre y luego muévete»).
- **Consecuencia.** El plan B («publicar la maduración») y toda cifra de «ventaja de aprender» (+68 %, +117 %, +136 %) quedan en el aire hasta descartarlo.
- **Acción.** Recomendación 1.

### H3. El positivo de C es real, pero está mal encuadrado

- **Lo que se sostiene [V].** ΔD de C: mediana +0,176, 9/10; réplica 10/10, mediana +0,1235; Mann-Whitney unilateral frente a Cbar p = 9,1·10⁻⁵; ablación de δ, mediana −0,073. Todo recalculado desde `_sonda_c_*.jsonl`. La p resiste una corrección de Bonferroni por 15 comparaciones.
- **Prueba más fuerte que el proyecto no ha contado [V].** En la propia trampa, `D_comer` E − X en C es positivo en 10/10 (de +0,069 a +0,504); en Cbar y en el padre queda en ±0,08. Con el cerebro ya congelado, haberse criado con el alga invertida cambia qué comen: es aprendizaje guardado en los pesos, específico del alga y dependiente de la experiencia. Está en `_analisis_c.json` y no aparece en la bitácora, ADR-034 ni el panel 09. Es mejor prueba que ΔD, que compara con un recién nacido congelado y por tanto mezcla maduración. Además, E − X de `frac_buena` en C tiene diez veces más dispersión que en Cbar (−0,088 a +0,040 frente a −0,005 a +0,014) con signo inconsistente: la crianza sí mueve dónde están, en las dos direcciones; «mediana 0, sin indicio» lo tapa.
- **Lo que rebaja el resultado.**
  1. **δ es una recompensa cableada por el diseñador** (bocado − cobro − media; `island.py`) [Va]. `spec.md` §Cerebro dice «no existe una recompensa externa». ADR-033 no enmienda la spec [Va]. Con recompensa dada, el resultado reproduce lo ya conocido (Niv 2002; Soltoggio 2008) [I].
  2. **Sin ventaja absoluta [V].** Ingesta por paso de los que aprenden: C 0,0756, Cbar 0,0760, padre 0,0773 (medianas de la sonda). Población final: C 2.510, Cbar 2.610. En el examen congelado, los adultos de Cbar discriminan al comer igual o mejor que los de C (`D_comer` de A: 0,65 frente a 0,56) y los recién nacidos también (0,58 frente a 0,44). Con δ, la evolución traslada al aprendizaje lo que sin δ resuelve el reflejo innato; no produce bichos mejores. [I: falta confirmar si «ingesta» es neta del cobro.]
  3. **Umbral rebajado tras ver los datos.** `diseno.md` v2.0 exigía ΔD ≥ 0,10 en ≥ 9/10; con esa vara C da 8/10 y la réplica 5/10 [V]. v2.6 pide ΔD > 0. Se fijó antes de la réplica, así que no es trampa, pero no es el listón original.
  4. **Comprobación de manipulación abandonada.** v2.0 pedía |D de congelados| < 0,05 («si no, la primaria no se interpreta»); en C es 0,10–0,34 en 10/10 [V]. v2.6 la omite sin decirlo.
  5. **«Firme» incumple la regla propia.** La hoja de ruta §4 exige réplica en otro mapa; las 20 semillas usan `fase1d-w0` (`run.json`) [V]. Los Cbar no se replicaron. La trampa no se pasó a las semillas 10–19.
- **¿Publicable tal cual?** No. Le falta: segundo mapa, Cbar replicado, `D_comer` E − X como primaria prerregistrada, rendimiento absoluto, y decir en el título que la señal de valor es dada.

### H4. Causa común de los negativos: bien identificada a medias

- **Lo que el proyecto vio bien.** «El reflejo basta»: tres diseños distintos dan E ≈ X con H-control positivo (alga por bicho |E − X| ≤ 0,013; manchas −0,021 a +0,012; veneno ±0,026) [V]. La saturación de m (diagnóstico D) explica que no haya señal de resultado [P].
- **Lo que no ha contrastado.**
  1. **Tiempo evolutivo.** Todo son 300 épocas (~500 generaciones); la bibliografía que se toma como modelo necesitó decenas de miles (panel 08, informe) [Va]. La ejecución «Larga» se condicionó a un indicio que no llegó. Ningún mundo pasa de 600 épocas [Va].
  2. **Coste por neurona.** `C_NEURON` 0,02 no se ha variado nunca, aunque estaba en el plan de la 1d [Va].
  3. **Tope de w0** (H2).
  4. **Mapa único** y 5–10 semillas sobre la misma geografía.
  5. **La pregunta misma.** «Ir a distancia hacia un color» lleva 0 de más de 40 mundos en la trampa; el panel le daba a b′ un 12–15 % sin base de frecuencia [Va].
- **Los «pasa» de la escalera son comprobaciones de manipulación** (moverse cuesta → menos empuje; hay comida → se vive más) [Va]. Ningún contraste sobre aprender pasó antes de C.

### H5. b′ lleva 16 días sin cerrar y los documentos no lo dicen

- Los 20 mundos terminaron el 30-10 a las 20:15; las medidas tumbaron WSL y solo hay 3 de 20 (`_madura_alga_bp_bprima.jsonl`) [V]. Con esas tres: E − X = +0,029, +0,010, +0,027, por debajo de la mediana exigida de 0,04 y con ruido de hasta 0,022 [V]; no concluye nada. En b′ el recién nacido ya discrimina al comer (`D_comer` de N: 0,54–0,76) [V]: el reflejo vuelve a ganar.
- `CLAUDE.md` sigue diciendo «No tocar `panspermia-bprima` mientras corre»; `mapa.json` y la hoja de ruta, «en curso» [V]. `_memoria_bprima.log` marca hoy 75 GB comprometidos, por encima del tope de 63,9 GB: probablemente ya hay archivo de paginación y no consta [I].

### H6. El panel no es un revisor independiente

- Tres instancias del mismo modelo, con el mismo contexto redactado por el moderador, que incluye su interpretación; paneles completos en 2–6 minutos; votos de ronda 1 solo resumidos por el moderador salvo en 09 y 10; dos decisiones de diseño clave (la forma de m_eff, «el alga equivocada alimenta») las introdujo el moderador, no un voto [Va].
- **Nunca hubo la opción «parar o medir la apertura directamente»** en ningún informe [Va].
- Acierta los negativos (4 de 4 primarias predichas «no pasa») [Va]. Eso significa también que se lanzaron unas 30 h de GPU en experimentos que el propio panel daba por perdidos al 80–85 %.
- **Regla de parada incumplida.** Decía «se cambia de mecanismo sin lanzar más mundos»; después se lanzaron 50 (C, réplica, b′) [V en fechas y colas].
- El contador de comparaciones no aplica ninguna corrección; funciona como incentivo para no arreglar defectos conocidos («tocar δ gasta intento») [Va].

### H7. Reproducibilidad: suficiente para trabajar, insuficiente para publicar

- `main` está en sustrato 2.0.0, sin nada del código de la escalera (58 commits en `escalera-bprima`, 186 de documentación en `main`) [V]. El examen contaminado de ADR-021 sigue en `main` [Va].
- **La rama `red` no existe**; `net/` es una línea de docstring [V]. La hoja de ruta y `CLAUDE.md` dicen que la red «se construye ya».
- 94 GB de `runs/` fuera de git y sin copia de seguridad; los JSONL de medida no llevan commit ni versión; `run.json` lleva versión de sustrato pero no commit [V]. Los scripts de medida se versionaron el 29-10, después de generar los datos de C [Va].
- «Idéntica bit a bit» entre sustratos: test real de 60 pasos, N = 64 y 6 campos; b′ = C con un script suelto [Va]. Nunca dos máquinas. La versión 3.0.0 designa dos sustratos distintos (E9 y tripa) [Va].
- El determinismo dentro de una máquina sí está probado (C s0 repetido a 100 épocas, 0 de 92 hojas distintas) [P].

### H8. Estadística

- Caminos que se bifurcan [Va]: calibrar con las semillas que luego puntúan (P3-escaso; P4-salto64 elegido por el VA de s0); seis «no pasa» rebautizados «indicio»; la medida primaria cambió cuatro veces (VA de cohorte → VA de población → sonda mixta → trampa → sonda mixta).
- «Un interruptor cada vez» no se cumple en P3-disperso, P4-alga ni en el control sin tripa [Va].
- 9/10 es demasiado exigente si el aprendizaje surge en parte de los linajes, pero aquí no ha tapado nada: los negativos tienen mediana ≈ 0, no «casi pasan» [V].
- La sonda mixta infla A por competencia entre mitades (reconocido en la bitácora, 24-10) [P].

### H9. Visiones a largo plazo

Condicionan de forma prematura: tres paneles (02, 03 y parte del 05) y la hoja de ruta giran en torno a la red y BOINC cuando no existe el fenómeno ni una línea de código de red. La conclusión del panel 03 («no estamos preparados») es correcta [P]. Lenguaje y mente colmena no han costado cómputo.

## 4. Discrepancias de datos

Contrastadas 14 cifras; las principales coinciden.

| Afirmación | Fuente | Lo que dicen los datos |
|---|---|---|
| Cbar: ΔD positivo en 3/10 | bitácora 27-10 | 2/10 (+0,008 y +0,006) |
| C > Cbar p = 0,0008; C > padre p = 0,0004 | bitácora 27-10 | Son bilaterales; unilateral (como en la réplica) 0,00038 y 0,00022 |
| Réplica: mediana +0,124 | bitácora 28-10 | +0,1235 (redondeo) |
| Manchas: M mediana 0,49 | bitácora 26-10 | 0,485 (redondeo) |
| «Sin indicio» en la primaria de C | bitácora 27-10 | `D_comer` E − X > 0 en 10/10 y dispersión de `frac_buena` 10× la de Cbar: no informado |
| Manipulación: congelados con \|D\| < 0,05 | `diseno.md` v2.0 | En C, 0,10–0,34 en 10/10; la comprobación desaparece en v2.6 |
| La red «se construye ya en la rama `red`» | hoja de ruta §1, `CLAUDE.md` | La rama no existe |
| b′ «en curso»; «no tocar mientras corre» | `CLAUDE.md`, `mapa.json` | Parado desde el 30-10 |
| «Llegan a la mancha el 88–98 %» | `p0_factores.md` (P2) [Va] | Refutado por ADR-021 (0–14 %); sin corregir |
| Sin discrepancia | — | ΔD de C y ablación; crianza (0,795 / 0,807 / 0,689 / 0,373 / 0,409); maduración 19 de 27; alga por bicho (ΔD +0,014, M 0,97, \|E − X\| ≤ 0,013); manchas E − X; H-control; nueve cifras de P1–P4 [Va] |

## 5. Lo que está bien hecho y conviene proteger

- La bitácora con los fallos incluidos, las horas reales y los errores propios anotados.
- Los instrumentos: sonda mixta con nulo, trampa del alga invertida con segunda baraja, H-control positivo y negativo, ablación de δ, control barajado Cbar. Son lo más valioso del proyecto.
- La costumbre de diagnosticar antes de variar (comer como reflejo, hambre, signo de m).
- Haber cazado sus propios falsos positivos (anillo, examen con química, VA de población).
- La validación de genomas en `genome.from_bytes` (rangos, NaN, canonicidad, hash) [Va].
- El panel 03 negándose a vender lo que no hay.

## 6. Recomendaciones priorizadas

| # | Acción | Coste | Pregunta de sí o no | Cómo se ve el fracaso |
|---|---|---|---|---|
| 1 | **Prueba del tope de w0.** (a) En checkpoints existentes, recortar los pesos del adulto a ±1 y examinar congelado. (b) Repetir un peldaño con mucha «maduración» (P3-escaso-tripa-frena-rampa o alga por bicho) con `W_INIT_SCALE` 4. | (a) ~1 h de GPU ligera, medio día de persona. (b) 10 mundos, ~6 h de GPU | ¿La ventaja de aprender cae por debajo de la mitad cuando el genoma puede nacer con pesos fuertes? | Si A sigue en +100 %, la maduración es un fenómeno de desarrollo real y el plan B se refuerza |
| 2 | **Cerrar b′** con las 17 medidas que faltan, la guarda y la saturación; anotar el resultado y **no abrir el intento 16**. | ~3 h de GPU, con el archivo de paginación | ¿E − X > 0 en ≥ 9/10 con mediana ≥ 0,04 y por encima de b′bar? | Lo esperable: no pasa. Se cierra la línea «a dónde ir» |
| 3 | **Medir la meta.** Una medida de apertura con nulo (actividad de clados persistentes con P0 como sombra; descriptores sin censura guardados por época) sobre ejecuciones largas: 3–5 semillas × 2.000 épocas de un mundo con presión (C o P4-salto64) y de P0. | ~30–40 h de GPU; 2–3 días de persona para la medida | ¿Sigue cambiando algo después de la época 300 más que en el nulo? | Si todo se aplana como en P0, el cuello está en el mundo, no en el aprendizaje, y hay que enriquecerlo (coevolución, más de un reto) |
| 4 | **Réplica de C en un segundo mapa**, con Cbar nuevo, `D_comer` E − X de la trampa como primaria prerregistrada y rendimiento absoluto como secundaria. | 20 mundos, ~12 h de GPU | ¿El aprendizaje guardado en los pesos se repite fuera de `fase1d-w0`? | Si no se repite, C es un resultado de un mapa |
| 5 | **H-int y datos.** Integrar `escalera-bprima` en `main`, examen limpio, commit en cada `run.json` y JSONL, copia de `runs/` fuera de la máquina, corregir documentos obsoletos. | 1–2 días de persona; solo la suite en GPU | ¿P3-escaso sale bit a bit antes y después? | Si no, hay deriva de sustrato que resolver antes de publicar |

**Aparcar explícitamente:** más variantes de plasticidad (predecir la tripa, poda, trazas nuevas), la sonda de curiosidad, la red P2P y BOINC (hoy no hay ni fenómeno ni código), y el panel como órgano que decide el rumbo.

**Abandonar:** el objetivo «aprender a dónde ir por el color» como puerta de todo lo demás, salvo sorpresa en b′.

**Coste frente a información [I].** Unas 260–270 h de GPU y unos 500 mundos en un mes (≈ 175 h hasta el 23-10 [Va]; ≈ 90 h después, estimación mía por las horas de la bitácora). De 15 comparaciones primarias, los resultados que cambiaron lo que se sabía salieron de diagnósticos baratos (sonda mixta, maduración, comer como reflejo, signo de m), no de los peldaños. La escalera de un interruptor se ha convertido en un óptimo local lento: conviene pasar a diagnósticos sobre datos existentes y a pocas ejecuciones largas.

**Artículos defendibles hoy.**
- *Metodológico* (el más sólido): instrumentos para separar maduración, reflejo y aprendizaje asociativo en agentes plásticos evolucionados, con la serie de negativos. Lo tumbaría un revisor por el tope de w0 (H2), el mapa único y la competencia en la sonda mixta.
- *C*: «dada una señal de valor fija, evoluciona una plasticidad que la usa». Lo tumbaría un revisor por novedad escasa frente a Niv y Soltoggio, por la falta de ventaja absoluta y por el mapa único.
- «Publicar la maduración» tal cual sería racionalizar: primero la recomendación 1.

## 7. Decisiones que solo puede tomar el responsable

1. ¿Se enmienda la spec para admitir una señal de valor cableada (δ), o C queda como experimento fuera de principios? **Recomiendo** enmendarla con un ADR que diga claramente que es una recompensa dada.
2. ¿Deja de ser el aprendizaje «a dónde ir» la puerta de la hoja de ruta, y pasa a serlo una medida de apertura con nulo? **Recomiendo** sí.
3. ¿Se cierra la escalera tras b′, sin intento 16? **Recomiendo** sí.
4. ¿Se congela todo trabajo y discusión de red y BOINC hasta tener un fenómeno replicado en dos mapas? **Recomiendo** sí.
5. ¿El panel pasa a ser consultivo, y los cambios de rumbo y los resultados «firmes» los revisa una persona externa o, al menos, otro modelo sin el contexto del moderador? **Recomiendo** sí.
6. ¿Se integra en `main` ahora (H-int), antes de cualquier mundo nuevo? **Recomiendo** sí.
7. ¿Se hace copia de seguridad externa de `runs/` (94 GB)? **Recomiendo** sí, ya.
8. ¿Se paga una segunda GPU de alquiler para el determinismo entre máquinas? **Recomiendo** no todavía; solo antes de publicar.

## 8. Anexo: lo que no pude comprobar

- No leí personalmente la bitácora del 15-10 al 23-10, `p0_factores.md`, los ADR-005 a 023 ni los 20 informes del panel: los leyeron tres ayudantes (el mismo modelo que yo, con mis mismos sesgos); lo suyo va marcado [Va]. No recomprobé que P0 cumpla el criterio de silueta ni que `C_NEURON` no se haya variado.
- No ejecuté tests, ni nada en GPU: el determinismo y la «identidad bit a bit» los doy por lo que dicen los tests leídos, no por ejecución.
- La hipótesis del tope de w0 (H2) es inferencia: el tope y los pesos medios están verificados; que explique la maduración, no.
- No sé si «ingesta» en la sonda es neta del cobro del veneno; afecta a H3.2.
- No abrí los datos de la fase 1 (`runs/phase1`) ni `_bateria_quimica.jsonl`, `_hambre*.jsonl`, `_diag_signo*.jsonl`.
- No verifiqué la bibliografía ni la afirmación sobre Avida y POET.
- No vi el artículo divulgativo vivo.
- Soy un modelo de la misma familia que el panel y el moderador: esta auditoría no sustituye a un revisor humano del área.
