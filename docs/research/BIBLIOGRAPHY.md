# Bibliografía inicial contrastada

Consulta: **2026-10-09**. Selección metodológica para orientar la demo y una posible
investigación. No es revisión sistemática ni valida actuaciones policiales.
Las aplicaciones a AI POLICE LAB son propuestas del equipo, no resultados de los artículos.

## S1

**Liang, P., et al. (2023; preprint 2022). _Holistic Evaluation of Language Models_.
Transactions on Machine Learning Research.**
[Versión de autor y referencia editorial](https://arxiv.org/abs/2211.09110).
DOI del preprint: `10.48550/arXiv.2211.09110`; versión consultada: arXiv v2, 2023.

- Tipo: estudio empírico de evaluación de modelos, publicado en revista.
- Verificación: resumen y metadatos de arXiv; no lectura completa del artículo.
- Aporta: evaluación en varias dimensiones, condiciones estandarizadas y cobertura explícita.
- Aplicación propuesta: publicar límites de PL-001 y distinguir resultados en vez de una sola nota.
- No establece: que las métricas de HELM validen esta simulación ni una clasificación universal.

## S2

**Zheng, L., et al. (2023). _Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena_.
Advances in Neural Information Processing Systems 36, Datasets and Benchmarks.**
[Actas oficiales](https://proceedings.neurips.cc/paper_files/paper/2023/hash/91f18a1287b398d378ef22505bf41832-Abstract-Datasets_and_Benchmarks.html).
DOI verificado en actas: `10.52202/075280-2020`.

- Tipo: artículo empírico en conferencia.
- Verificación: resumen y metadatos de las actas; no lectura completa.
- Aporta: examina sesgos de posición, verbosidad y autopreferencia en jueces LLM.
- Aplicación propuesta: validar cualquier futuro juez contra humanos y probar orden y longitud.
- No establece: que el acuerdo observado en sus tareas se transfiera a PL-001 ni que otro proveedor sea un juez neutral.

## S3

**Jacobs, A. Z., y Wallach, H. (2021; preprint 2019). _Measurement and Fairness_.
FAccT ’21.** [Versión de autor](https://arxiv.org/abs/1912.05511).
DOI editorial enlazado en los metadatos: `10.1145/3442188.3445901`.

- Tipo: trabajo metodológico/conceptual publicado en conferencia.
- Verificación: resumen y metadatos de arXiv; no lectura completa.
- Aporta: necesidad de explicitar constructos y su relación con las mediciones.
- Aplicación propuesta: no usar tensión, número de turnos o formato JSON como sustitutos automáticos de empatía o calidad.
- No establece: una definición universal de equidad ni validez de nuestras variables.

## S4

**Pineau, J., et al. (2021). _Improving Reproducibility in Machine Learning Research
(A Report from the NeurIPS 2019 Reproducibility Program)_. JMLR, 22(164), 1–20.**
[Página editorial](https://www.jmlr.org/papers/v22/20-303.html).
No se consigna DOI: la página consultada no lo proporciona.

- Tipo: informe metodológico publicado en revista.
- Verificación: resumen y metadatos editoriales; no lectura completa.
- Aporta: prácticas y materiales para facilitar comprobación y reproducción.
- Aplicación propuesta: manifiesto de código/entorno, parámetros, versiones y trazas.
- No establece: que una API externa regenere exactamente las mismas respuestas ni que pasar tests valide el constructo.

## S5

**Mizrahi, M., Kaplan, G., Malkin, D., Dror, R., Shahaf, D., y Stanovsky, G. (2024).
_State of What Art? A Call for Multi-Prompt LLM Evaluation_. TACL, 12, 933–949.**
[ACL Anthology](https://aclanthology.org/2024.tacl-1.52/).
DOI: `10.1162/tacl_a_00681`.

- Tipo: estudio empírico publicado en revista.
- Verificación: resumen y metadatos editoriales; no lectura completa.
- Aporta: variación de resultados absolutos y relativos ante distintas formulaciones de prompt.
- Aplicación propuesta: estudiar paráfrasis declaradas antes del ensayo si las conclusiones dependen del prompt.
- No establece: cuántas variantes necesita este proyecto ni la causa de diferencias todavía no observadas aquí.

## S6

**Nosek, B. A., Ebersole, C. R., DeHaven, A. C., y Mellor, D. T. (2018).
_The preregistration revolution_. PNAS, 115(11), 2600–2606.**
DOI: `10.1073/pnas.1708274114`.
[Artículo original en copia universitaria](https://psychologicalsciences.unimelb.edu.au/__data/assets/pdf_file/0007/2888098/The-preregistration-revolution.pdf).

- Tipo: artículo metodológico de coloquio publicado en revista.
- Verificación: metadatos, resumen, introducción y apartados iniciales del PDF;
  no lectura íntegra. Se usó copia de la Universidad de Melbourne ante limitaciones
  de acceso a la página editorial.
- Aporta: distinción entre exploración y confirmación y fijación previa del plan.
- Aplicación propuesta: etiquetar el protocolo actual como borrador; si se hace
  un estudio confirmatorio, registrar preguntas y análisis antes de los resultados.
- No establece: obligación de preregistrar una demo ni que este repositorio sea un registro externo.

## Ampliación 2026-10-13 (LAB-021): evaluación de agentes, fidelidad, jueces y acuerdo

Consulta: **2026-10-13**. Siete fuentes abiertas para las técnicas valoradas en
[EVALUATION_PRACTICES](EVALUATION_PRACTICES.md). «Verificación» distingue lo leído:
*metadatos y resumen* de la página de arXiv/actas, y *texto* = versión HTML (ar5iv)
del artículo consultada mediante una herramienta de extracción que contestó a
preguntas concretas; no es lectura íntegra por una persona. Todas las aplicaciones
son propuestas del equipo. Los arXiv sin sede editorial en su página se etiquetan
**preprint** (puede existir versión publicada que no se comprobó).

### S7

**Yao, S., Shinn, N., Razavi, P., y Narasimhan, K. (2024). _τ-bench: A Benchmark for
Tool-Agent-User Interaction in Real-World Domains_. Preprint arXiv:2406.12045 (v1).**
[arXiv](https://arxiv.org/abs/2406.12045) · DOI `10.48550/arXiv.2406.12045`.

- Tipo: preprint, benchmark empírico.
- Verificación: metadatos, resumen y texto (secciones de recompensa, simulador y limitaciones).
- Resumen: simula conversaciones entre un usuario simulado por LLM (gpt-4-0613) y un
  agente con herramientas y políticas del dominio. Compara el estado final de la base
  de datos con un estado objetivo anotado y propone *pass^k* (probabilidad de que
  *k* intentos independientes de una tarea tengan éxito todos). Reporta que agentes
  de última generación resuelven <50 % y son poco consistentes entre intentos.
- Relación comprobada: sí, es la fuente más cercana al diseño de AI POLICE LAB
  (agente + ciudadano simulado por LLM + herramientas + reglas). Aporta (i) la
  práctica de reportar fiabilidad en repetición y no un único intento, relevante para
  LAB-006; (ii) límites declarados del usuario simulado (puede carecer de memoria o
  razonamiento, o desviarse de su instrucción), aplicables a Q3/H1.
- No establece / diferencia: τ-bench tiene un estado objetivo único y correcto por
  tarea; PL-001 **no** tiene «actuación correcta», así que no se puede copiar su
  recompensa ni *pass^k* como medida de calidad policial; solo como estabilidad de un
  resultado definido de antemano. Los autores avisan de que éxito final no garantiza
  cumplir la política (p. ej. acciones sin confirmación pueden pasar).

### S8

**Ma, C., et al. (2024). _AgentBoard: An Analytical Evaluation Board of Multi-turn LLM
Agents_. Preprint arXiv:2401.13178 (v2); comentario de autor: NeurIPS 2024 (Oral).**
[arXiv](https://arxiv.org/abs/2401.13178) · DOI `10.48550/arXiv.2401.13178`.

- Tipo: benchmark y marco de evaluación; el campo de comentarios de arXiv indica
  NeurIPS 2024, no verificado en actas.
- Verificación: metadatos, resumen y texto (progreso, anotación, limitaciones).
- Resumen: sostiene que reportar solo tasa de éxito final oculta el proceso. Propone
  una *tasa de progreso* que puntúa avances intermedios (subobjetivos anotados a
  mano, o comparación de estado) y un conjunto de herramientas para analizar
  trayectorias por paso, junto con éxito final. Un estudio humano (60 trayectorias
  por tarea) reporta correlaciones >0,95 con la métrica.
- Relación comprobada: respalda **evaluar trayectorias y no solo el cierre**
  (EVALUATION_PRACTICES, fila «trajectory»), y el uso de anotación humana en
  varias rondas para fijar subobjetivos.
- No establece / diferencia: la tasa de progreso exige subobjetivos con estado
  correcto; en PL-001 solo valdría para **hitos factuales** definidos antes
  (p. ej. «consultó la evidencia X»), no para juzgar la actuación. Los propios
  autores señalan que anotar subobjetivos es costoso y que los entornos son simulados.

### S9

**Min, S., et al. (2023). _FActScore: Fine-grained Atomic Evaluation of Factual
Precision in Long Form Text Generation_. EMNLP 2023 (artículo principal); arXiv:2305.14251 (v2).**
[arXiv](https://arxiv.org/abs/2305.14251) · DOI `10.48550/arXiv.2305.14251`.

- Tipo: artículo empírico en conferencia (sede según la página de arXiv).
- Verificación: metadatos, resumen y texto (anotación, fuente de conocimiento, límites).
- Resumen: descompone un texto largo en *hechos atómicos* y mide la proporción
  respaldada por una fuente de conocimiento fiable. Anotadores humanos etiquetan cada
  hecho como respaldado, no respaldado o irrelevante (acuerdo reportado entre 88 % y
  96 % según modelo en el 10 % doble anotado) y construyen un estimador automático.
- Relación comprobada: respalda la unidad de análisis de Q1 (**afirmación atómica
  del cierre frente a una fuente de referencia**) y el etiquetado de tres estados.
- No establece / diferencia: su fuente es Wikipedia y solo biografías; aquí la
  fuente sería la **evidencia accesible al participante en cada turno** más la
  verdad sintética, lo cual es un diseño nuevo no validado. Los autores distinguen
  «no respaldado» de «falso» (puede faltar evidencia en la fuente) y miden precisión,
  no exhaustividad: no penaliza omitir.

### S10

**Wang, P., et al. (2023). _Large Language Models are not Fair Evaluators_.
Preprint arXiv:2305.17926 (v2).**
[arXiv](https://arxiv.org/abs/2305.17926) · DOI `10.48550/arXiv.2305.17926`.

- Tipo: preprint, estudio empírico de sesgo de jueces.
- Verificación: metadatos, resumen y texto (medición y calibración).
- Resumen: muestra que el veredicto de un LLM comparando dos respuestas cambia al
  alterar su orden (tasa de conflicto 46,3 % en GPT-4 y 82,5 % en ChatGPT en uno de
  los emparejamientos) y propone calibración: evidencia múltiple, promedio con orden
  intercambiado y revisión humana de los casos más inciertos.
- Relación comprobada: concreta la «prueba de orden» que ya exige PROTOCOL para un
  juez LLM. Aplicación: intercambiar el orden y medir conflicto antes de usar un juez.
- No establece / diferencia: dos modelos de OpenAI, un benchmark de 80 preguntas y
  etiquetas humanas de tres autores del propio artículo. Cifras no transferibles a PL-001.

### S11

**Panickssery, A., Bowman, S. R., y Feng, S. (2024). _LLM Evaluators Recognize and
Favor Their Own Generations_. Preprint arXiv:2404.13076 (v1).**
[arXiv](https://arxiv.org/abs/2404.13076) · DOI `10.48550/arXiv.2404.13076`.

- Tipo: preprint, estudio empírico.
- Verificación: metadatos, resumen y texto (tareas, modelos, límites).
- Resumen: en resumen de noticias, GPT-4, GPT-3.5 y Llama 2 reconocen sus propios
  textos por encima del azar y puntúan mejor los suyos; tras ajuste fino, la
  capacidad de auto-reconocimiento correlaciona linealmente con la autopreferencia,
  y los controles (longitud, legibilidad, etc.) no explican la tendencia.
- Relación comprobada: justifica **no usar como juez a un modelo que también
  compite** o, si se hace, medir el efecto; refuerza la objeción a «un modelo más
  potente» del texto pegado.
- No establece / diferencia: solo resumen, tres modelos y un diseño de prompt;
  los autores admiten que la causalidad no está plenamente validada. No prueba que
  ocurra con las salidas de PL-001.

### S12

**Greshake, K., Abdelnabi, S., Mishra, S., Endres, C., Holz, T., y Fritz, M. (2023).
_Not what you've signed up for: Compromising Real-World LLM-Integrated Applications
with Indirect Prompt Injection_. Preprint arXiv:2302.12173 (v2).**
[arXiv](https://arxiv.org/abs/2302.12173) · DOI `10.48550/arXiv.2302.12173`.

- Tipo: preprint, taxonomía de amenazas y demostraciones.
- Verificación: metadatos, resumen y texto (definición, canales, límites).
- Resumen: define la *inyección indirecta*: instrucciones plantadas en datos que el
  modelo recupera, de modo que la línea entre datos e instrucciones se difumina;
  presenta una taxonomía de impactos y demostraciones en aplicaciones sintéticas y en
  Bing Chat. Concluye que faltan mitigaciones efectivas.
- Relación comprobada, **por analogía**: el texto del ciudadano (LLM) es contenido
  no confiable que llega al participante; justifica tratarlo como datos y probar
  que no altera reglas ni herramientas.
- No establece / diferencia: **no** analiza inyección desde otro LLM o usuario
  simulado (solo lo menciona como trabajo futuro, §5.3); no cuantifica tasas de
  éxito y su reproducibilidad es limitada. La extrapolación a PL-001 es hipótesis del equipo.

### S13

**Debenedetti, E., et al. (2024). _AgentDojo: A Dynamic Environment to Evaluate Prompt
Injection Attacks and Defenses for LLM Agents_. Preprint arXiv:2406.13352 (v3).**
[arXiv](https://arxiv.org/abs/2406.13352) · DOI `10.48550/arXiv.2406.13352`.

- Tipo: preprint, entorno de evaluación.
- Verificación: metadatos, resumen y texto (métricas, amenaza, límites).
- Resumen: 97 tareas y 629 casos de seguridad donde un agente con herramientas lee
  datos no confiables; mide utilidad sin ataque, utilidad bajo ataque y éxito del
  ataque con **funciones deterministas sobre el estado del entorno**, no con juez LLM
  (porque la inyección podría secuestrar al evaluador).
- Relación comprobada: modelo metodológico para las pruebas adversariales del arnés:
  separar utilidad de seguridad y comprobar por estado, no por opinión de un LLM.
- No establece / diferencia: tareas de correo/banca/viajes con datos ficticios; los
  autores señalan que ataques y defensas son simples y las comprobaciones manuales.

### S14

**Artstein, R., y Poesio, M. (2008). _Survey Article: Inter-Coder Agreement for
Computational Linguistics_. Computational Linguistics, 34(4), 555–596.**
[ACL Anthology](https://aclanthology.org/J08-4004/) · DOI `10.1162/coli.07-034-R2`.

- Tipo: artículo de revisión en revista.
- Verificación: metadatos de ACL Anthology y **resumen** en el repositorio de la
  Universidad de Essex (consultado 2026-10-13; la primera frase literal es «a survey
  of methods for measuring agreement among corpus annotators»). **Texto no leído**:
  PDF sin extractor local y página editorial bloqueada (403). No citar detalles
  (umbrales, fórmulas) sin leerlo.
- Resumen (nivel resumen): revisa coeficientes de acuerdo entre
  codificadores (kappa, pi, alfa de Krippendorff) y sostiene que las medidas
  ponderadas tipo alfa pueden convenir a muchas tareas de anotación.
- Relación: apoya la frase de PROTOCOL «elegir la medida de acuerdo según la escala»
  para la rúbrica humana de Q1–Q3. Según el resumen, las medidas ponderadas tipo alfa
  pueden convenir más que las tipo kappa, a costa de interpretar peor el valor.

## Mantenimiento de fuentes

Para cada nueva afirmación: fuente primaria abierta, autor/año/título, enlace o
DOI verificado, versión, alcance de lectura, aporte concreto, límites y fecha.
Si solo se accede al resumen, declararlo. Profundizar lectura antes de basar una
decisión metodológica específica en el texto. Marcar correcciones/retractaciones
si se detectan; no usar popularidad de una cita como prueba de validez.

Esta selección (S1–S14) cubre metodología general de evaluación y medición. No cubre
normativa, currículo formativo, validez ecológica de PL-001 ni efectos sobre personas.
