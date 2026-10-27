# Hoja de ruta hasta la red P2P (provisional)

**Decisión del panel 02 (25-10-2026, 22:28), por unanimidad en la segunda ronda**, a petición del responsable («¿hoja de ruta hasta un bicho lo bastante inteligente y un mundo lo bastante complejo para dar el paso al P2P?»). Informes en `docs/escalera/panel/02_*`. Se revisa con cada resultado; el responsable puede cambiarla.

## 1. La red: construir ya, conectar después

- **La fase 4a se construye ya, en paralelo y sin GPU.** Va en la rama `red`: identidad Ed25519, paquete firmado, validación en 6 pasos, cuotas, tracker, gRPC/TLS, archivo SQLite y revocación. Se prueba con genomas sintéticos y *fuzzing* en CPU. La spec ya lo permitía: solo depende del formato de genoma. ADR-012 queda matizado: se construye ahora y se conecta después.
- **No se conecta como ciencia** hasta cumplir los criterios del §2. La migración entrará como **peldaño propio** (P-migra, un solo cambio), con islas que difieran de verdad (otra alga buena u otro mapa). Si no difieren, la migración solo homogeneiza.
- **Memoria:** el *fuzzing*, la integración y el tracker nunca corren a la vez que un barrido en GPU (Windows sin archivo de paginación).

## 2. Criterios para abrir la red (solo observan; principio 1 intacto)

- **Bicho (aprendizaje asociativo, no maduración ni reflejo):** tienen que cumplirse a la vez:
  - la trampa del alga invertida con el examen barajado, E − X ≥ 0,05 en ≥ 9/10;
  - la selectividad de entrada E − X mayor que |E − E2|, el ruido de la segunda baraja;
  - **la réplica en un segundo mapa** (otro nodo distinto de `fase1d-w0`);
  - además, tamaños de efecto con intervalos.
- **Mundo:** al menos dos presiones independientes activas, viable 10/10 durante 300 épocas sin rampas ni cortes hechos a medida, y la batería limpia.
- **Plataforma:** la de la spec: 3 nodos 7 días sin intervención y 0 paquetes corruptos aceptados en 10⁵.

## 3. Hitos

| Hito | Qué añade | Pregunta | GPU | Si sí → | Si no → |
|---|---|---|---|---|---|
| **H-control** ✓ (26-10, 02:44: pasa; positivo 10/10, débil 9/10, negativo 10/10) | Control positivo y negativo de las medidas | ¿La trampa detecta un aprendizaje impuesto a mano (E − X > 0,05) y da ≈ 0 con los pesos barajados entre E y X? | 0 (CPU ligera) | Las medidas valen | Rehacer las medidas; las manchas quedan en suspenso |
| **H-red** (paralelo) | La fase 4a en CPU | ¿0 corruptos en 10⁵ y 3 nodos 7 días? | 0 | Infraestructura lista y apagada | Arreglar |
| **H-int** (paralelo) | Integrar las ramas de la escalera en una rama de integración; examen limpio (ADR-021) en `main`; formato de genoma congelado, versionado y firmado | ¿La suite pasa y P3-escaso se reproduce bit a bit antes y después? | Solo la suite, con la GPU libre | Sustrato 3.x congelado | Resolver antes de seguir |
| **H1** manchas ✗ (26-10, 06:22: 0/10, sin indicio) | Manchas lejanas de un solo tipo (ADR-027) | ¿E − X ≥ 0,05 en 9/10? | ~8 h | Réplica en otro mapa → P6 | H2 |
| **H2** P5-d ✗ (26-10, 21:52: diferido 0/10 e inmediato 0/10, sin indicio; H-control pasa; ADR-030) | **Veneno diferido**: el daño llega 20–50 pasos después de comerlo, con el veneno inmediato como contraste prerregistrado si cabe (10 semillas más) | ¿Aparece la discriminación cuando el reflejo de la tripa ya no basta? | ~6–12 h | Réplica → P6 | H3 |
| **H3** (saltado, panel 07, ADR-032) | Tercer diseño independiente | — | — | — | **Plan B** |
| **Plan B 1 · C** ◐ (27-10, 14:37: primaria 0/10; indicio fuerte en secundarias: ΔD +0,176 en 9/10 frente al barajado; ADR-033) | Modulación con signo de resultado: m + k·δ, δ = (bocado − cobro) − su media | ¿E − X ≥ 0,05 en 9/10 sobre P5-inmediato, y por encima del δ barajado? | ~14 h | C diferido → B + C | Publicar la maduración |
| P6 | Veneno que cambia, de uno en uno los demás ingredientes | ¿Persiste cuando cambia? | ~6 h por rama | Larga | Aparcar la rama |
| Larga | La mejor receta, 1.000–2.000 épocas, 10 semillas | ¿Se sostiene y crece? | ~60–100 h | P-migra | Volver a P6 |
| P-migra | 3 islas distintas conectadas frente a aisladas | ¿Mejora el aprendizaje o la diversidad (3 islas frente a 1 con N × 3)? | ~18 h | Granja «fuga» y 4a real | La red solo para diversidad |

## 4. Regla de parada y plan B

- **Tres diseños independientes desde hoy** (H1, H2 y H3). Cada uno cambia la estructura del mundo, no un parámetro. La **réplica en otro mapa no gasta un intento**, pero es obligatoria para confirmar cualquier positivo o indicio.
- Si ninguno pasa (≥ 9/10 con la selectividad a favor) ni da un indicio replicado, **se cambia de mecanismo sin lanzar más mundos**:
  1. **Plasticidad nueva:** trazas de elegibilidad en ABCD, para que el crédito llegue a lo que pasó antes (Soltoggio; Niv 2002), o una moduladora de recompensa predicha. Sustrato major, en rama propia.
  2. **Publicar la maduración** como resultado: «la ventaja de aprender en vida es de desarrollo, no asociativa», con la sonda mixta y la trampa como instrumentos. Ya es publicable, junto con los diagnósticos metodológicos.
  3. Lo social **no** sin aprendizaje individual: la cultura no tendría qué compartir.
- **Contador de comparaciones:** la bitácora lleva cuántas variantes se han probado con el umbral 9/10, y la interpretación lo tiene en cuenta (corrección por comparaciones múltiples, al menos declarada).

## 5. Riesgos que vigilar

1. **El reflejo basta.** Mientras la tripa resuelva el problema, aprender no compensa. Señal: M ≥ 0,9 con E − X ≈ 0.
2. **La medida no ve el aprendizaje.** Resuelto por H-control (26-10): frac_buena y sel_entrada lo ven; D_comer no sirve para un aprendizaje de acercarse y el primer contacto es poco sensible.
3. **Muchas comparaciones y un umbral exigente.** Con un efecto en una parte de los linajes (C8), 9/10 casi nunca pasa. Por eso hay tamaños de efecto, contador y regla del indicio.
4. **Mapa único.** Todo vale para `fase1d-w0` hasta la réplica.
5. **Deuda de ramas y deriva del sustrato.** 17 ramas sin integrar. Señal: más de 60 commits por delante de `main` → integrar (H-int).

## 6. La puerta BOINC: cuándo pedir cómputo a voluntarios

**Decisión del panel 03 (25-10-2026, 22:35), unánime en la segunda ronda.** El responsable concibe la red como un proyecto de computación voluntaria tipo BOINC. Informes en `docs/escalera/panel/03_*`.

**¿Estamos preparados? No.** Falta el fenómeno central (aprendizaje asociativo), una medida firme de crecimiento abierto y una curva de escalado. Estamos a unos tres hitos: un aprendizaje replicado, el crecimiento abierto medido en una ejecución larga y la curva de escalado.

**Paquete de pruebas**, completo y prerregistrado antes de pedir cómputo:
- **(a) Aprendizaje asociativo real:** el criterio del bicho (§2), con el control positivo y negativo, la ablación de la plasticidad (sin plasticidad, el efecto desaparece) y M por debajo del 50 % de la ventaja.
- **(b) Crecimiento abierto:** el archivo de novedad y la batería crecen en la mitad tardía de una ejecución larga más que en un nulo de deriva sin selección. La batería da ≈ 0 con la política fija y con genomas al azar.
- **(c) Escalado:** la capacidad C de (a) o (b), no una aproximación, frente al cómputo. Un eje cada vez (N, épocas, islas), al menos 3 puntos por eje, densidad fija y un nulo de escalado (genomas al azar con N pequeño y grande). Pendiente log-log con su IC95 y un **tamaño de efecto mínimo relevante prerregistrado**: 3 puntos con un IC que excluye 0 no se venden como «curva de escalado». **Si el doble de cómputo no da nada, no se pide cómputo.**
- **(d) Reproducibilidad entre máquinas:** la misma (versión, semilla, estado) en dos GPU distintas, bit a bit o con una tolerancia fijada antes de medir. Código y datos abiertos, para que un tercero lo reproduzca.
- **(e) Un resultado intermedio comprensible** para un donante, con un gráfico público de avance.

**Cómo plantearlo:** no decir «más relevante para la IA que los LLM». No es defendible y hundiría la credibilidad. Frase defendible: «Estudiamos si el aprendizaje puede emerger de la selección ecológica; tenemos herramientas de medida rigurosas y, todavía, ningún aprendizaje asociativo demostrado.» Es ciencia básica sobre el origen del aprendizaje, complementaria a los LLM. Los negativos documentados son la mejor credencial.

**Antecedentes** (de memoria; verificar y añadir a la bibliografía antes de citarlos):
- Network Tierra (Ray, años 90): sin una pregunta medible ni el fenómeno en una sola máquina, distribuir no añade nada.
- Avida convenció por una métrica clara con nulos.
- POET: la coevolución entre el entorno y el agente evita el estancamiento.
- Folding@home y BOINC: la gente dona por una pregunta concreta y un avance visible, con unidades de trabajo verificables por réplica (aquí el determinismo ayuda).

**Qué se hace ya y qué no:**
- **El escalado espera a tener una C válida.** Escalar hoy mediría maduración, un artefacto que costaría días de GPU.
- **(b0) hecho (26-10, 02:52; panel 04): la tasa de novedad no vale** (falla el control positivo: los mundos cambiantes no dan más novedad que los estables; P2 la infla con `repro_age` censurado). Para (b) hará falta otra medida con datos que hoy no se guardan. Diseño original: **(b0) ya, exploratorio:** validar una medida de crecimiento abierto contra nulos con los datos existentes (P2 a 600 épocas y la escalera a 300). El nulo y la ventana tardía se fijan antes de mirar, y se declara exploratorio porque esas ejecuciones ya se han visto. En CPU ligera.
- **(d0):** el determinismo entre dos GPU distintas, con la tolerancia fijada antes. **Pendiente:** solo hay una máquina (RTX 5070 Ti); la 5070 «de referencia» de la spec nunca ha existido (responsable, 25-10). Hará falta una segunda máquina, mejor de otra arquitectura, o una GPU alquilada, que es decisión del responsable porque cuesta dinero. No bloquea nada hasta la puerta BOINC.
- **El primer experimento de escalado, cuando exista C:** la escalera de N (1.024, 4.096 y 16.384, con la VRAM reservada) con densidad fija y su nulo, 5 semillas por punto y 10 si hay señal. Después, las épocas, y las islas con P-migra.
