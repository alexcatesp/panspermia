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

## 7. Recombinar dentro de la receta del cerebro (B1, ADR-018)

Pregunta del responsable (19-10-2026): ¿heredar la receta del cerebro entera de un solo progenitor es "incorrecto" biológicamente?

- **En la Tierra lo normal es recombinar dentro de cada cromosoma.** En la meiosis, los cromosomas de los dos progenitores se emparejan por **homología** (la misma secuencia en el mismo sitio) y se entrecruzan. El hijo recibe trozos de los dos dentro de un mismo cromosoma. El emparejamiento funciona porque el ADN es lineal y cada gen ocupa su locus. Nuestros índices de la CPPN no tienen esa homología (ADR-018); las marcas históricas de NEAT son su equivalente artificial (stanley2002neat).
- **Pero heredar un bloque entero también existe en la Tierra.** Es el **ligamiento completo**:
  - el ADN de mitocondrias y cloroplastos se hereda casi siempre de un solo progenitor (birky1995uniparental);
  - la parte del cromosoma Y que no recombina (charlesworth2000ydegeneration);
  - los **supergenes**: bloques de genes que no se separan porque una inversión impide el entrecruzamiento, como los patrones de alas de *Heliconius numata* o el cromosoma social de la hormiga de fuego (thompson2014supergenes).
- **Precio del ligamiento completo:** dentro del bloque se pierden las ventajas del sexo.
  - Las mejoras de la receta no se pueden combinar: compiten (interferencia de Hill-Robertson, hill1966linkage).
  - Las mutaciones dañinas se acumulan como en un asexual (trinquete de Muller, muller1964ratchet). El cromosoma Y degenera precisamente por eso (charlesworth2000ydegeneration).
- **Ventaja:** conserva intacta una combinación que funciona junta. Por eso, en la Tierra, la selección favorece suprimir la recombinación entre genes que cooperan (thompson2014supergenes).
- **Para Panspermia:**
  - la corrección de ADR-018 es un caso biológico real (la receta como supergén), no un error;
  - pero deja la parte más importante del genoma sin las ventajas del sexo;
  - recombinar dentro de la receta exige **homología**, es decir, marcas históricas. Eso cambia el formato del genoma, y conviene decidirlo en P0 si se quiere.

## 8. Dónde nace el hijo (D1)

- **Aislamiento por distancia** (wright1943isolation): si las crías nacen cerca de sus padres, los vecinos son parientes y la población se divide en vecindarios genéticos.
- **Poblaciones viscosas** (taylor1992viscous; west2002kincompetition): ese parentesco local favorece ayudar al vecino (selección de parentesco), pero los parientes también compiten por lo mismo, y en el caso más sencillo los dos efectos se anulan. Lo que decide es si la competencia es local o global.
- **En P0** no hay interacción entre bichos ni selección: dónde nace el hijo no puede cambiar la genética, solo quién vive al lado de quién. El resultado (genética idéntica bit a bit; parentesco local 22–62 veces el global junto al padre y ≈ 1 vez al azar) lo confirma.
- **Implicación de diseño:** nacer junto al padre es lo terrestre y no cuesta nada en P0; el modo «al azar» queda como interruptor de control para los peldaños sociales (señal, ataque), donde permite saber si una conducta depende del parentesco.

## 9. ¿Mundos mucho más grandes para tener más variedad? (C1, pregunta del responsable)

- **La variedad neutral crece con N** (ohta1973nearlyneutral; charlesworth2009ne): es lo que mide C1 (32–100 clados con 1.024, 540–740 con 4.096). Pero en P0 es variedad sin uso: nadie la selecciona.
- **Lo que importa es la variedad útil y la eficacia de la selección.** Con N grande, la selección distingue ventajas menores (s > ~1/N). Pero en una población asexual, a partir de cierto tamaño, las mejoras compiten entre sí en vez de sumarse (interferencia clonal, gerrish1998clonal), y crecer más rinde cada vez menos. El sexo (B1) es lo que deja aprovechar las poblaciones grandes (colegrave2002sex).
- **Más grande no es siempre más complejo.** En organismos digitales asexuales, las poblaciones pequeñas y las grandes, pero no las intermedias, hicieron crecer el genoma: las pequeñas por deriva (fijando inserciones algo dañinas) y las grandes por selección (labar2016populations). En la Tierra, la complejidad de los genomas eucariotas pudo crecer precisamente gracias a poblaciones pequeñas (lynch2003origins).
- **Alternativa de la Tierra: muchos mundos con algo de migración** (wright1943isolation). Varias poblaciones medianas, poco conectadas, conservan más variedad total que una sola grande del mismo tamaño, porque cada una deriva hacia soluciones distintas. Es el diseño original de Panspermia (islas P2P, fase 4a) y lo apoya D1 (vecindarios de parientes).

## 10. ¿Tasa de mutación como gen o constante? (A3 con selección)

- **En un mundo que no cambia, la selección baja la tasa de mutación.** Casi toda mutación es dañina, así que los linajes que mutan menos dejan hijos más sanos. La tasa baja hasta que la ventaja de bajarla más es menor que el ruido de la deriva (barrera de la deriva, lynch2016driftbarrier). Es lo que se ve en P1: σ cae 10 veces y la tasa estructural de 8 a 20 veces en 300 épocas.
- **En un mundo con algo por descubrir, mutar más puede ganar.** Los mutadores viajan junto a las mejoras que producen (autostop genético) y llegan a dominar poblaciones que se adaptan (taddei1997mutator; en *E. coli*, sniegowski1997mutators). Por eso la tasa como gen solo se puede juzgar en un peldaño con ganancias (P2 o después).
- **En evolución artificial**, la autoadaptación de σ (beyer2002es) ajusta el tamaño del paso al progreso posible: cerca de un óptimo, σ se reduce y la búsqueda se vuelve local.

## 11. ¿Qué física para la receta del cerebro (CPPN)? (A2, pregunta del responsable)

- **Que un genoma crezca sin ganar nada es un fallo conocido** en la evolución artificial (inflado o *bloat*: langdon1998bloat, banzhaf2002bloat). Una de sus causas son los propios operadores: si añadir y quitar no se compensan, el tamaño deriva solo (sesgo de eliminación, soule1998removal). Es lo que pasa con la CPPN de siempre (como en NEAT, stanley2002neat, que solo crece y lo compensa empezando por lo mínimo).
- **Hay tres remedios clásicos:**
  1. un coste por tamaño (presión de parsimonia, soule1998parsimony). En la vida real, cada gen cuesta energía, pero tan poca que solo importa en poblaciones enormes (lynch2015bioenergetic);
  2. operadores que no cambian el tamaño esperado (cruces de tamaño justo, langdon2000sizefair);
  3. controlar directamente la distribución de tamaños (igualación de operadores, dignum2008equalisation). Este no sirve aquí, porque sería una métrica externa decidiendo (principio 1).
- **Para Panspermia apunta al remedio 2:** operadores equilibrados, de modo que el tamaño de la receta solo cambie por deriva o porque la selección lo pida. Es la misma hipótesis nula que se eligió para las neuronas (A1). El remedio 1 sería añadir una ley física nueva (pagar por la receta) y cambiaría lo que mide P1; queda como opción si en P2 la receta se hinchara sin motivo.
- **En la Tierra no hay una dirección única** (kuo2009deletional frente a lynch2003origins). Por eso conviene el punto neutro, y la variante terrestre queda para la prueba de robustez final.

## 12. Sexo con selección: por qué en P1 purga peor (B1)

- **Con sexo, la tasa de mutación casi no baja.** En un asexual, el gen que sube la tasa viaja siempre con las mutaciones malas que causa, y la selección lo elimina con ellas. Con cruce, se separa de ellas en pocas generaciones, y la selección apenas lo ve (johnson1999mutation; lynch2010mutationrate: los organismos sexuales toleran tasas mayores). En P1, σ baja 10 veces sin sexo y solo de 1,5 a 3 con sexo.
- **La ventaja de limpiar mutaciones malas** (kondrashov1988deleterious) necesita que los daños se potencien entre sí (epistasia sinérgica) y muchas mutaciones por hijo. En P1 no se ve: cada neurona cuesta lo mismo, se sume a otras o no.
- **La ventaja principal del sexo es juntar mejoras** que aparecen en bichos distintos (hill1966linkage, felsenstein1974recombination, colegrave2002sex). Sin nada que ganar (P1) no puede aparecer; hay que probarla en P2.

## 13. ¿Cómo rebrota la comida? (P2, pregunta del responsable)

- **Lo que hace el código** (spec §mundo, ADR de la fase 0): en cada casilla, crecimiento logístico `r·R·(1 − R/K)`, con r = 1,5 y K, la capacidad de la casilla, repartida en manchas (suma de 8 ondas en el toro; media 4, picos de 12–13 y un 10 % del mundo sin comida). Se añade un goteo mínimo (0,002) para que una casilla rapada vuelva a brotar. En P2 las manchas no se mueven.
- **De dónde viene:**
  - es la ecuación logística de Verhulst (1838; historia en bacaer2011verhulst), popularizada por pearl1920growth;
  - es el modelo estándar del recurso que se regenera en los modelos de consumidor y recurso (rosenzweig1963predator: presa logística y consumidor);
  - en vida artificial, Sugarscape (epstein1996sugarscape) usa una regla parecida: el azúcar vuelve a crecer hasta la capacidad de cada casilla, en un paisaje de dos montañas.
- **Lo que no viene de la bibliografía:** los números (r, K, el contraste de las manchas y el goteo) se calibraron en la fase 1 para que las poblaciones sobrevivan (ADR-008). El goteo es necesario porque la logística pura deja una casilla a cero para siempre.
- **Qué implica para P2:** una casilla a medio comer rebrota deprisa (lo máximo, a media carga), y una rapada tarda unos 50 pasos en recuperar la mitad. Comer en la mancha sin rapar compensa más que vaciarla.

## 14. Comida dispersa: ¿obliga a buscar? (D2, P2-buscar, pregunta del responsable)

- **Hueco:** en P2 la comida cubre el 87 % del suelo y casi siempre está a la vista; basta un reflejo (seguir lo que se ve). Para que buscar compense, la comida tiene que estar más lejos de lo que alcanzan los sentidos.
- **Búsqueda aleatoria óptima** (viswanathan1999random, viswanathan2008levy): cuando los objetivos son escasos y están fuera del alcance de los sentidos, la estrategia de movimiento importa. Una búsqueda con tramos largos de vez en cuando (tipo Lévy) encuentra más que un paseo al azar y no necesita memoria. Predicción para P2-buscar: puede evolucionar una búsqueda innata (reflejo más un patrón de movimiento), sin cerebro grande ni aprendizaje.
- **Teorema del valor marginal** (charnov1976optimal): cuándo dejar una mancha que se agota para ir a otra. Con manchas separadas, se mide indirectamente en el éxito del examen y en la ingesta.
