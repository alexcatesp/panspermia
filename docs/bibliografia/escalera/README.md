# Bibliografía de la escalera: el sesgo de la mutación

Búsqueda del 18-10-2026. El primer mundo de la escalera (P0, sin selección) mostró que **los cerebros crecen solos**: de 8 a 29 neuronas ocultas en 300 épocas, sin que pensar sirva para nada. La pregunta del responsable fue: **¿por qué decidimos que la mutación haga eso, qué ocurre en la Tierra y le importa a una vida que algún día trabajará en la Tierra a través de robots?**

- `refs.bib`: BibTeX de todo lo citado. Todos los DOI se comprobaron en api.crossref.org el 18-10-2026.
- Nivel de lectura de cada ficha: **[resumen]** = resumen y fuentes secundarias. Ninguna se ha leído completa todavía.

## 1. De dónde viene nuestro sesgo

- La especificación del 15-10 copió la idea de NEAT (Stanley y Miikkulainen 2002): empezar con redes mínimas y **complejificar**, y que la selección pode lo que sobra. Por eso todos los operadores de la tabla de mutación suman más que restan:

  | Operador | Suma | Resta |
  |---|---|---|
  | Conexiones de la CPPN | 5 % | 2 % |
  | Nodos de la CPPN | 3 % | 1 % |
  | Neuronas | duplicar 1 % | — |

- El operador "expresar o silenciar" invierte **un hueco elegido al azar** de los 64. Con 8 encendidas, casi siempre enciende una: es un sesgo **entrópico**, que empuja hacia la mitad, como en un paseo al azar de Ehrenfest.
- **Equilibrio teórico:** de 0,03·(64 − k)/64 + 0,01 = 0,03·k/64 sale k ≈ 43 neuronas. Se llega con una constante de tiempo de unas 1.070 generaciones; con 700 generaciones se esperan unas 25. En P0 s0 se observan 28,7.
- **Nadie analizó este efecto al escribir la spec.** Lo destapó el control sin selección que pidió el responsable.

## 2. Qué pasa en la Tierra (síntesis)

1. **A pequeña escala, la mutación pierde más ADN del que gana.** En 17 grupos de los tres dominios de la vida, las deleciones superan a las inserciones en todos (Kuo y Ochman 2009):
   - en procariotas, por longitud, al menos 10 a 1;
   - en eucariotas, cerca de 1 a 1.

   Este sesgo, más que la selección, mantiene compactos los genomas bacterianos. Las bacterias simbiontes pierden los genes que ya no usan (Mira, Ochman y Moran 2001). **Nuestro sustrato hace lo contrario.**
2. **Duplicar genes es frecuente y casi siempre efímero:** unos 0,01 duplicados por gene y millón de años. La gran mayoría se silencia en pocos millones de años, y los que sobreviven quedan bajo selección purificadora (Lynch y Conery 2000). Nuestro "duplicar neurona" imita la duplicación, pero no su pérdida posterior.
3. **Aun así, la complejidad crece sin selección donde la selección es débil:**
   - Lynch y Conery (2003) y Lynch (2007) atribuyen gran parte de la complejidad de los genomas eucariotas (intrones, elementos móviles, duplicados) a procesos **no adaptativos**, posibles porque las poblaciones pequeñas tienen poca selección;
   - la "evolución neutral constructiva" (Stoltzfus 1999) explica cómo surgen complejidades sin ventaja;
   - McShea y Brandon (2010; versión cuantitativa en 2019) lo elevan a "ley de fuerza cero": sin selección ni restricciones, la diversidad y la complejidad, medidas como varianza, tienden a aumentar. Es discutido: Matthen la critica como ley.
4. **El sesgo de la mutación orienta la evolución, no solo añade ruido.** Si una variante aparece más a menudo, tiene más probabilidad de fijarse: "el primero que llega se queda" (Yampolsky y Stoltzfus 2001). En levadura, *E. coli* y *M. tuberculosis*, el espectro de mutaciones influye de forma proporcional en el de las adaptaciones que se fijan (Cano et al. 2022).
5. **El tejido nervioso es caro y se pierde cuando no se usa:**
   - en los peces de las cuevas, ver cuesta el 15 % del metabolismo en reposo de un juvenil de 1 g; perder ojos y techo óptico ahorra esa energía (Moran, Softley y Warrant 2015);
   - la hipótesis del tejido caro (Aiello y Wheeler 1995) liga el cerebro grande humano a un intestino más pequeño, aunque los datos comparativos posteriores son discutidos.
6. **El coste de las conexiones ordena las redes.** En redes evolucionadas, añadir un coste por conexión hace aparecer módulos, que además adaptan mejor; sin coste, nunca se forman (Clune, Mouret y Lipson 2013).

## 3. Lo mismo en la computación evolutiva

- **"Bloat":** en programación genética, los programas crecen sin mejorar. Una explicación es combinatoria: hay muchos más programas grandes que pequeños con la misma aptitud, así que la búsqueda deriva hacia lo grande (Langdon y Poli 1998). Otra es protectora: el código inútil amortigua las mutaciones dañinas (Banzhaf y Langdon 2002).
- **Nuestro crecimiento en P0 es de este tipo:** más formas de tener muchas neuronas que pocas.

## 4. ¿Le importa a una vida que trabajará en la Tierra?

- **La genética no tiene que copiar la terrestre para funcionar en la Tierra.** La robótica evolutiva consigue controladores para robots reales con codificaciones muy distintas: directas, NEAT, CPPN… (Doncieux et al. 2015).
- **El obstáculo real es el "salto de la realidad":** las soluciones simuladas aprovechan defectos del simulador. Se cruza premiando también la transferibilidad, comprobada con pocas pruebas en el robot real (Koos, Mouret y Doncieux 2013).
- **Lo que decide si un controlador sirve en la Tierra** es el mundo donde se selecciona (física, energía, sensores), no la química de la herencia.
- **Pero el sesgo de la mutación sí importa para el producto.** Orienta qué soluciones aparecen primero (punto 4 de la sección 2) y cuánto "equipaje" llevan.
- **Para un robot, cada neurona es cómputo y batería.** Un sustrato que infla los cerebros por defecto obliga a la selección a trabajar en contra; uno con sesgo a perder, como el terrestre, o sin sesgo, deja cerebros pequeños salvo que pensar compense.

## 5. Implicaciones de diseño

- **Medir siempre contra P0.** "El cerebro creció" no es prueba de que pensar compense.
- **Mantener el operador actual durante la escalera,** porque es otra variable: cambiarlo a mitad mezclaría dos efectos.
- **Probarlo como una rama de un solo cambio:**
  - P0′ y P1′ con un operador sin sesgo de tamaño: elegir con la misma probabilidad "encender una apagada" o "apagar una encendida", y equilibrar la duplicación con una deleción de la misma tasa;
  - o con sesgo terrestre: perder más que ganar.
- **El coste por conexión** (Clune et al. 2013) es un candidato para un peldaño futuro: hoy solo cuesta cada neurona, no cada sinapsis.

## 6. Pendiente

- Leer completos Kuo y Ochman (2009), Cano et al. (2022) y Clune et al. (2013).
- Buscar estudios sobre la reducción del cerebro en animales domésticos y en especies de islas.
