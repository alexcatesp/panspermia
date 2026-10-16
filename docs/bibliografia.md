# Evolución artificial hacia la IA: revisión bibliográfica

15-10-2026 · Alejandro Catalá Espí · Versión viva: https://claude.ai/code/artifact/1c2abcde-c54e-4ba1-93fa-3d9260b78b8f

† = identificador de memoria, no comprobado: verificar antes de citar. El resto se comprobó el 15-10-2026.

## Orden de lectura recomendado

1. Clune (2019), *AI-GAs*: el programa de investigación más cercano al objetivo del proyecto.
2. Soltoggio, Stanley y Risi (2018), *Born to Learn*: revisión de evolución + plasticidad.
3. Gupta et al. (2021), DERL: cuerpo + aprendizaje + evolución en 3D.
4. Lehman y Stanley (2011) y Wang et al. (2019), POET: cómo evitar el estancamiento.
5. Najarro y Risi (2020): reglas hebbianas evolucionadas, base del agente propuesto.
6. Herramientas (última sección) antes de programar la fase 0.

## Vida artificial digital

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Ray, T. S. (1991). *An approach to the synthesis of life*. Artificial Life II, 371–408 | Tierra: programas autorreplicantes; aparecen parásitos e hiperparásitos | Capítulo, sin DOI † |
| Lenski, R. E., Ofria, C., Pennock, R. T. y Adami, C. (2003). *The evolutionary origin of complex features*. Nature 423, 139–144 | Avida: una función lógica compleja (EQU) surge por pasos intermedios | 10.1038/nature01568 |
| Ofria, C. y Wilke, C. O. (2004). *Avida: a software platform for research in computational evolutionary biology*. Artificial Life 10(2), 191–229 | Plataforma Avida | 10.1162/106454604773563612 |
| Ray, T. S. (1995–1998). *Network Tierra*: «reserva de biodiversidad» para organismos digitales en ordenadores de voluntarios (~150 máquinas en 1995), con migración de genomas entre instalaciones | Precedente directo de la red P2P de islas. Resultado: un ancestro multicelular diseñado, con 2 tipos celulares, sobrevivió a la selección, pero **no aumentó el número de tipos celulares** (Ray 1998, según la revisión WebAL de 2014, arXiv:1407.5719). Título exacto del artículo de 1998 aún sin comprobar | Sin identificador; fuentes secundarias comprobadas el 16-10-2026 |
| Maynard Smith, J. y Szathmáry, E. (1995). *The Major Transitions in Evolution*. Oxford University Press | Las grandes transiciones de la evolución en la Tierra | Libro, sin DOI † |

## Neuroevolución

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Stanley, K. O. y Miikkulainen, R. (2002). *Evolving neural networks through augmenting topologies*. Evolutionary Computation 10(2), 99–127 | NEAT: topología y pesos desde lo mínimo; especiación | 10.1162/106365602320169811 |
| Stanley, K. O., D'Ambrosio, D. B. y Gauci, J. (2009). *A hypercube-based encoding for evolving large-scale neural networks*. Artificial Life 15(2), 185–212 | HyperNEAT: CPPN genera conectividad según la geometría | 10.1162/artl.2009.15.2.15202 |
| Salimans, T. et al. (2017). *Evolution strategies as a scalable alternative to reinforcement learning* | ES paralelas rivalizan con RL | arXiv:1703.03864 |

## Evolución + aprendizaje

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Hinton, G. E. y Nowlan, S. J. (1987). *How learning can guide evolution*. Complex Systems 1, 495–502 | Demostración mínima del efecto Baldwin (Fontanari y Santos 2017, arXiv:1702.08411, matizan que muestra la selección de la capacidad de aprender más que el efecto Baldwin) | Sin DOI; reimpreso en cs.toronto.edu/~hinton |
| Soltoggio, A., Stanley, K. O. y Risi, S. (2018). *Born to learn*. Neural Networks 108 | Revisión de redes plásticas evolucionadas (EPANN) | 10.1016/j.neunet.2018.07.013 |
| Najarro, E. y Risi, S. (2020). *Meta-learning through Hebbian plasticity in random networks*. NeurIPS 2020 | Se evolucionan solo reglas hebbianas por sinapsis | arXiv:2007.02686 |
| Gupta, A., Savarese, S., Ganguli, S. y Fei-Fei, L. (2021). *Embodied intelligence via learning and evolution*. Nature Communications 12, 5721 | DERL: evolución de morfologías + RL; efecto Baldwin | 10.1038/s41467-021-25874-z |

## Cuerpos y mundos 3D

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Sims, K. (1994). *Evolving virtual creatures*. SIGGRAPH '94, 15–22 | Morfología y control coevolucionados en 3D | 10.1145/192161.192167 |
| Yaeger, L. (1994). *PolyWorld: life in a new context*. Artificial Life III | Ecología con fitness implícita y redes hebbianas | Capítulo, sin DOI † |
| Lipson, H. y Pollack, J. B. (2000). *Automatic design and manufacture of robotic lifeforms*. Nature 406, 974–978 | GOLEM: cuerpos y controladores evolucionados en simulación y luego fabricados | 10.1038/35023115 |
| Kriegman, S., Blackiston, D., Levin, M. y Bongard, J. (2020). *A scalable pipeline for designing reconfigurable organisms*. PNAS 117(4), 1853–1859 | Xenobots: diseños evolucionados en simulación construidos con células vivas | 10.1073/pnas.1910837117 |

## Apertura evolutiva (open-endedness)

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Lehman, J. y Stanley, K. O. (2011). *Abandoning objectives*. Evolutionary Computation 19(2), 189–223 | Novelty search | 10.1162/EVCO_a_00025 |
| Mouret, J.-B. y Clune, J. (2015). *Illuminating search spaces by mapping elites* | MAP-Elites | arXiv:1504.04909 |
| Wang, R., Lehman, J., Clune, J. y Stanley, K. O. (2019). *POET* | Entornos y agentes coevolucionan | arXiv:1901.01753 |
| Clune, J. (2019). *AI-GAs: AI-generating algorithms* | Meta-aprender arquitecturas, algoritmos de aprendizaje y entornos | arXiv:1905.10985 |
| Hughes, E. et al. (2024). *Open-endedness is essential for artificial superhuman intelligence*. ICML 2024 | Definición formal de open-endedness | arXiv:2406.04268 |

## Sustratos alternativos

| Referencia | Aporte clave | Identificador |
| --- | --- | --- |
| Real, E., Liang, C., So, D. R. y Le, Q. V. (2020). *AutoML-Zero*. ICML 2020 | Redescubre retropropagación desde operaciones básicas | arXiv:2003.03384 |
| Chan, B. W.-C. (2019). *Lenia: biology of artificial life*. Complex Systems 28(3), 251–286 | Autómata celular continuo, >400 "especies" | 10.25088/ComplexSystems.28.3.251 |
| Kumar, A. et al. (2025). *Automating the search for artificial life with foundation models*. Artificial Life 31(3), 368–396 | ASAL: VLM como métrica de novedad | arXiv:2412.17799 |

## Herramientas GPU

| Herramienta | Uso | Referencia |
| --- | --- | --- |
| MuJoCo Playground (MJX) | Física 3D en GPU + render por lotes (Madrona) | Zakka et al. (2025), RSS XXI, 10.15607/RSS.2025.XXI.020; arXiv:2502.08844 |
| Brax | Física diferenciable en JAX | arXiv:2106.13281 |
| evosax | ES y GA vectorizados en JAX | arXiv:2212.04180 |
| EvoJAX | Neuroevolución acelerada por hardware | arXiv:2202.05008 |
