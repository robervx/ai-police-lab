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

## Mantenimiento de fuentes

Para cada nueva afirmación: fuente primaria abierta, autor/año/título, enlace o
DOI verificado, versión, alcance de lectura, aporte concreto, límites y fecha.
Si solo se accede al resumen, declararlo. Profundizar lectura antes de basar una
decisión metodológica específica en el texto. Marcar correcciones/retractaciones
si se detectan; no usar popularidad de una cita como prueba de validez.

Esta selección cubre metodología general de evaluación y medición. No cubre
normativa, currículo formativo, validez ecológica de PL-001 ni efectos sobre personas.
