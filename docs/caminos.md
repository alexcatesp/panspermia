# Caminos probados: descartados, aparcados y en estudio

Registro para podar el árbol de opciones sin perder lo que podría servir más adelante.

- **Descartado**: falla por un error de diseño o de medida que no depende de la fase. No se reabre.
- **Aparcado**: falla *en estas condiciones*, pero hay un motivo concreto para pensar que puede funcionar más adelante. Se anota la condición de reapertura.
- **En estudio**: funciona en parte y es objeto de experimentos.

Criterio: una idea biológica (veneno, cambio ambiental, depredación) no se descarta por fallar en un contexto concreto. Lo que es imposible desde cero puede volverse posible sobre lo ya conseguido. Solo se descarta lo que falla por un error de diseño o de medida.

| Camino | Estado | Evidencia | Condición de reapertura | Referencia |
| --- | --- | --- | --- | --- |
| Prueba del anillo en la batería de capacidad | Descartado | Avanzar recto sin cerebro saca 1,0 | — | ADR-010, ADR-011 |
| Valor del aprendizaje por supervivencia de la cohorte a una época | Descartado | Edad media ~140 pasos frente a épocas de 1.000: compara casi ceros | — (sustituido por la sonda emparejada a nivel de población) | ADR-010 |
| Instalación con `uv pip` | Descartado | Rechaza al azar ruedas NVIDIA válidas («Invalid Wheel-Version») | Nueva versión de uv que lo arregle | ADR-005 |
| Algas tóxicas plenas desde el paso 0 (sin rampa) | Aparcado | 505 de 512 muertos en la primera época; extinción en 2–3 épocas | Mundos sembrados con migrantes que ya distinguen algas (fase 4, flujo libre → granja) | ADR-008 (calibración) |
| Cambio global y simultáneo del tipo tóxico (1/400 o 1/1000 por paso) | Aparcado | Colapsos sincronizados; extinción en 2 de 5 semillas incluso con veneno a la mitad | Poblaciones que ya aprendan en vida (tras la 1d) o como catástrofe rara | ADR-008 (calibración) |
| `TOXIC_FACTOR = 1` (veneno pleno) | Aparcado | Extinción con franjas móviles en las semillas 0 y 2 | Condición de la 1d (intensidad del castigo) | ADR-008, ADR-012 |
| `RESOURCE_R = 2` | Aparcado | La población toca el tope (4.096), agota las algas y colapsa | Con un tope de población mayor (varios mundos por GPU o más memoria) | ADR-008 (calibración) |
| Mancha lejana a 150 unidades y 500 pasos (batería v2 inicial) | Descartado | Ni un buscador programado supera el 0,25: la alarma no sonaría nunca | — (sustituida por la mancha a 90 unidades y 1.000 pasos, con umbral 0,2) | ADR-011 |
| Química, rampa de 40 épocas, franjas móviles, `TOXIC_FACTOR = 0,5`, `RESOURCE_R = 1,5` (1b actual) | En estudio | Sobreviven 2 de 5 semillas; en una los cerebros crecen de 8 a 21 neuronas | — | ADR-008, ADR-012 (1d) |
| Varias islas a la vez en la GPU (`vmap` sobre islas) | Aparcado | Con B = 1, el lote ya no coincide bit a bit con la ejecución individual; con B = 2 y N = 4.096 se agota la VRAM (16 GB, 4,5 ocupados por el escritorio); con dos procesos a la vez cada época tarda casi el doble (la GPU ya va saturada) | Más VRAM, N más pequeño para barridos, o aceptar el lote como ejecución canónica (con su propio test de determinismo) | `scripts/bench_multi.py` (rama `multi-mundo`) |
