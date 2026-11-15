# Prompt de auditoría para Claude Fable 5.2

Uso: abrir una sesión nueva de Claude Code en la raíz del repositorio, con Fable 5.2, y pegar el bloque de abajo. La auditoría es de **solo lectura** (no lanza mundos ni toca la GPU, ni modifica código ni documentos del proyecto).

---

## Prompt (copiar desde aquí)

Eres un auditor científico independiente, con experiencia en vida artificial, evolución de sistemas con aprendizaje (efecto Baldwin, plasticidad hebbiana evolucionada, neuroevolución, *open-endedness*) y en método experimental y estadística. No has participado en el proyecto. Tu trabajo es decirnos, con evidencia y sin cortesías, **si vamos por el buen camino para conseguir nuestro objetivo**, y si no, qué cambiar.

### 1. El proyecto

Panspermia es un ecosistema evolutivo distribuido: agentes encarnados que evolucionan por selección ecológica (sin función de fitness explícita), aprenden en vida con plasticidad hebbiana evolucionada y, a largo plazo, migran entre islas P2P (visión tipo computación voluntaria BOINC). La meta de investigación declarada en `docs/spec.md` es **sostener la aparición de novedad conductual (apertura evolutiva) a escala creciente**. Hay además visiones a largo plazo (lenguaje emergente, mente colmena) que dependen de que exista aprendizaje individual.

Los principios innegociables están en `CLAUDE.md` y `docs/spec.md` (ninguna métrica decide la reproducción; genoma como datos; determinismo; todo vectorizado; sin retropropagación en el agente).

Desde octubre de 2026 el proyecto sigue una «escalera de complejidad» (P0 → P5 y variantes), un interruptor cada vez, con una pregunta de sí/no por peldaño prerregistrada en `docs/escalera/diseno.md`. Las decisiones de diseño las toma un panel de tres agentes (`docs/escalera/panel.md` y `docs/escalera/panel/`). El responsable humano decide lo que concierne a salvaguardas, principios y cambios de rumbo.

### 2. Qué debes leer (en este orden) y cómo

Lee de verdad, no hojees. Cita siempre archivo y sección/fecha cuando afirmes algo. Los documentos son largos: léelos por partes y apóyate en búsquedas, pero no saques conclusiones de un fragmento sin comprobar el contexto.

1. `CLAUDE.md` (estado vivo; ojo, es denso y cronológico).
2. `docs/spec.md` (objetivo, principios, arquitectura).
3. `docs/escalera/hoja_de_ruta.md` (criterios para abrir la red, hitos, regla de parada, plan B).
4. `docs/escalera/diseno.md` (preguntas y criterios prerregistrados por peldaño) y `docs/escalera/p0_factores.md` (resultados por factor).
5. `docs/caminos.md` y `docs/mapa.json` (qué se descartó, aparcó o está en estudio, y por qué).
6. `docs/decisiones.md` (ADR-005 en adelante; sobre todo ADR-010/011 falso positivo del anillo, ADR-014 escalera, ADR-021 examen contaminado, ADR-024–035).
7. `docs/bitacora.md` (cuaderno de laboratorio; contrasta números, fechas y conclusiones declaradas con los datos).
8. `docs/escalera/condiciones_aprendizaje.md`, `docs/bibliografia.md` y `docs/bibliografia/escalera/` (qué dice la literatura sobre cuándo evoluciona el aprendizaje).
9. Informes del panel en `docs/escalera/panel/01_…` a `10_…` (busca desacuerdos, supuestos compartidos y sesgos de grupo).
10. Cuando una conclusión clave te parezca frágil, abre los datos en `runs/` (p. ej. `runs/fase1d/_analisis_c.json`, `_sonda_*.jsonl`, `_madura*.jsonl`) y los scripts de medida (`scripts/escalera/`, `scratchpad/` si existe) y verifica que el análisis dice lo que el texto dice.

No ejecutes simulaciones en GPU (la máquina puede estar ocupada y Windows no tiene archivo de paginación). Puedes ejecutar análisis ligeros en CPU si los necesitas para verificar una cifra.

### 3. Preguntas que debes responder

**A. Alineación con el objetivo.**
- El objetivo declarado es apertura evolutiva; la escalera lleva semanas centrada en demostrar *aprendizaje asociativo en vida*. ¿Es ese un paso necesario del camino o una deriva de objetivo? ¿Qué evidencia hay de que el aprendizaje individual es condición previa de la apertura evolutiva en este sistema, y qué evidencia de lo contrario?
- ¿Las visiones a largo plazo (red P2P/BOINC, lenguaje, mente colmena) están condicionando decisiones de hoy de forma útil o prematura?

**B. Calidad del diagnóstico de los negativos.**
- Hay una larga serie de peldaños que «no pasan» (P2-buscar, P3-coste, P4-alga, tripa, freno, alga por bicho, manchas, P5-d…). ¿Tienen una causa común que el proyecto haya identificado correctamente, la haya pasado por alto o la haya identificado y no actuado? Candidatos que debes contrastar, sin darlos por buenos: el reflejo innato basta, el cerebro se vacía porque aprender no compensa, el mundo no presenta un problema que exija aprender, la plasticidad hebbiana modulada es insuficiente, el tamaño/duración de las ejecuciones, el mapa único.
- ¿Los diagnósticos «solo observan» (sonda mixta, trampa del alga invertida, maduración, hambre, comer) miden lo que dicen medir? ¿Los controles positivos y negativos (H-control, Cbar, ablación de δ) son suficientes?
- El único resultado positivo confirmado es «aprender qué comer con δ» (réplica C, semillas 10–19) y el hallazgo de que la ventaja de aprender es sobre todo maduración. ¿Está bien interpretado? ¿Es publicable tal cual? ¿Qué le falta?

**C. Rigor metodológico y estadístico.**
- Umbrales prerregistrados de 9/10, contador de comparaciones, uso de indicios no prerregistrados, regla de parada y «tres diseños». ¿Hay *forking paths*, cambios de criterio a posteriori, umbrales demasiado exigentes o laxos, falta de corrección por comparaciones múltiples o de tamaños de efecto con intervalos?
- ¿El «panel de tres agentes» introduce riesgo de consenso falso (mismos modelos, mismos sesgos)? ¿Dónde se necesita validación externa humana o un revisor realmente independiente?
- Reproducibilidad: determinismo, versionado del sustrato (2.x vs 3.x), 17 ramas sin integrar, deuda de integración. ¿Pone eso en riesgo la validez de los resultados o su publicación?

**D. Estrategia y alternativas.**
- Dado lo que se sabe, ¿qué hipótesis de mayor valor esperado no se ha probado? Considera, por ejemplo: entornos que exijan aprendizaje por ser no estacionarios de verdad (no solo saltos de comida), problemas en que el reflejo innato no es posible, plasticidad más expresiva (trazas, neuromodulación predictiva, redes recurrentes con memoria), selección sobre la capacidad de aprender (efecto Baldwin con coste de aprendizaje), co-evolución/competencia entre agentes, mundos más ricos antes que más peldaños, o métricas de novedad/apertura (MODES, actividad evolutiva de Bedau, etc.) medidas ya sobre las ejecuciones existentes.
- ¿Conviene seguir con la escalera de un interruptor cada vez, o el método se ha vuelto un óptimo local lento? Cuantifica coste (horas de GPU, tiempo) frente a información ganada por peldaño.
- La regla de parada contempla «publicar la maduración» como plan B. ¿Es un buen plan B o una forma de racionalizar? ¿Qué artículo(s) defendibles existen hoy con los datos actuales, y qué revisor los tumbaría y por qué?

**E. Riesgos no vigilados.**
- Técnicos (memoria de Windows/WSL, dependencia de una sola máquina y una sola GPU), de sustrato, de seguridad de la futura red P2P (genomas como datos, validación) y de proceso (documentación enorme, cronología en `CLAUDE.md`, riesgo de que el contexto se pierda).
- Puntos donde el proyecto da por hecho algo que nadie ha comprobado.

### 4. Cómo trabajar

- Distingue siempre entre: **hecho verificado** (lo has comprobado en datos o código), **afirmación del proyecto** (está escrita pero no la has verificado) e **inferencia tuya**. Marca el nivel de confianza.
- Contrasta al menos **cinco** cifras clave de la bitácora/ADR contra los archivos de datos o scripts. Informa de discrepancias, aunque sean pequeñas.
- Busca activamente evidencia en contra de la narrativa del proyecto («estamos cerca», «el indicio es fuerte»). Haz el mejor argumento posible de la postura contraria antes de descartarla.
- Si falta información para responder algo, dilo y propón la medida más barata que la resolvería (preferiblemente en CPU, sobre datos ya generados).
- No modifiques archivos del repositorio. Si quieres dejar tu informe en disco, escríbelo solo en `docs/auditoria_informe.md`.
- Puedes usar subagentes para leer en paralelo documentos largos, pero la síntesis y las conclusiones son tuyas.
- Escribe en español, con precisión técnica. El responsable pide además que cada mensaje incluya un bloque **«En palabras sencillas»** (nivel abuela o niño, sin jerga) con la conclusión principal.

### 5. Formato del informe

1. **Veredicto** (máximo 10 líneas): ¿buen camino, camino parcial o camino equivocado? Con tu confianza (alta/media/baja) y la razón principal.
2. **En palabras sencillas** (5–8 líneas).
3. **Hallazgos**, ordenados por importancia. Para cada uno: afirmación, evidencia (archivo:sección o fecha), nivel (verificado / afirmación del proyecto / inferencia), consecuencia y acción recomendada.
4. **Discrepancias de datos** encontradas al contrastar cifras (tabla: afirmación · fuente · lo que dicen los datos).
5. **Lo que está bien hecho** y conviene proteger (breve, concreto).
6. **Recomendaciones priorizadas**: las 5 acciones de mayor valor esperado, cada una con coste estimado (GPU/CPU/horas de persona), qué pregunta de sí/no responde y cómo se vería el fracaso. Indica qué aparcar o abandonar explícitamente.
7. **Decisiones que solo puede tomar el responsable** (salvaguardas, principios, rumbo), formuladas como preguntas cerradas con tu recomendación.
8. **Anexo**: lo que no pudiste comprobar y por qué.

Empieza leyendo `CLAUDE.md` y `docs/escalera/hoja_de_ruta.md`, enumera brevemente tu plan de lectura y de verificación, y después ejecútalo sin esperar confirmación.

---

## Notas para quien lance la auditoría

- Contexto grande: los documentos suman ~4.500 líneas y `bitacora.md` casi 2.000; conviene una sesión con contexto amplio o permitir subagentes de lectura.
- Si se quiere una segunda opinión, repetir con otro modelo y comparar los hallazgos coincidentes (más fiables) y los divergentes.
- Antes de lanzarla, comprobar que no hay barridos en GPU que dependan de ramas o worktrees (`panspermia-*`); la auditoría no debería necesitarlos.
