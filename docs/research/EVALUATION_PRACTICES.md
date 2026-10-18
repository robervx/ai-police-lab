# Prácticas de evaluación de LLM — valoración para AI POLICE LAB

Fecha: 2026-10-13 · rol: director científico, **revisión secuencial por el asistente
principal** (no subagente, no revisión humana) · estado: valoración interna, no protocolo.

## Procedencia y límite de esta nota

La lista de siete técnicas llegó como texto pegado por el usuario, **sin autoría,
fecha ni fuentes**. Es un resumen divulgativo, no una fuente verificada. Sirve como
checklist de ideas; ninguna afirmación de un artículo o paper puede apoyarse en él.
Cada técnica que se adopte necesita fuente primaria abierta (ver «Fuentes pendientes»).

## Valoración técnica a técnica

| Técnica (texto pegado) | Encaje en el proyecto | Decisión | Condición |
|---|---|---|---|
| Golden dataset | No existe «acción policial correcta» de referencia; PL-001 es sintético. Sí aplica a lo determinista: reglas, contrato del ciudadano, aislamiento, exportaciones. | **Adoptar parcial** | Ya cubierto por pruebas/`tests/ACCEPTANCE.md`. Para constructos (Q1–Q3): «trazas ancladas» anotadas por humanos, usadas solo para calibrar la rúbrica, no como respuesta correcta. |
| LLM-as-a-Judge | Ya en [PROTOCOL](PROTOCOL.md#revisión-humana-y-posible-juez-llm) y [S2](BIBLIOGRAPHY.md#s2). El texto dice «modelo más potente»: **no es criterio válido** aquí (sesgo de autopreferencia, participantes son modelos de proveedores). | **Mantener auxiliar** | Validación local frente a humanos, orden/longitud, juez fuera de los participantes o su efecto medido. Rúbrica congelada antes de ver resultados. |
| RAG evaluation | No hay recuperación de documentos. | **No aplica** | Si se añadiera memoria/recuperación, reabrir. |
| Hallucination detection | Análogo directo a Q1: afirmaciones del cierre frente a la evidencia **accesible en ese momento**. Cuidado: «no respaldada» ≠ «falsa» y el modelo no conoce la verdad oculta. | **Adoptar como Q1** | Verificación por afirmación con rúbrica humana; separar verdad sintética de información accesible (ya en protocolo). |
| Trajectory evaluation | Alto encaje: hay trazas por turno ([TRACE_INSPECTION](../TRACE_INSPECTION.md)). | **Adoptar descriptivo** | Métricas de proceso (acciones inválidas, herramientas, orden, causa de cierre) **sin signo de calidad** ni nota total (AGENTS.md; PROTOCOL: «menos turnos… no tienen signo universal»). |
| Adversarial testing | Dos sentidos. (a) Robustez del *arnés*: fuga de hechos ocultos, inyección vía respuestas del ciudadano-LLM al participante, JSON hostil, fórmulas CSV. Alto encaje. (b) Jailbreak de modelos como objeto de estudio: fuera de alcance. | **Adoptar (a)** | Entrada del sénior IA; resultados de seguridad ≠ resultados de comportamiento. Ya hay trabajo parcial (BACKLOG línea «pruebas adversariales»). |
| Online evals + feedback | No hay producción ni usuarios. Pulgares arriba/abajo no miden constructo alguno. Revisión humana muestreada sí. | **Solo revisión humana muestreada** | A/B de prompts solo con variantes declaradas antes (H2); no retocar tras ver ganadores. |

## Lectura para un paper

Estas técnicas son **infraestructura de calidad**, no un diseño de estudio. Convertir
el proyecto en paper exige además lo que ya está pendiente: pregunta primaria,
réplicas y orden (LAB-006), conclusiones (LAB-011), preregistro externo si se
pretende confirmatorio y piloto real (LAB-019). Sin eso el límite sigue siendo
«demo técnica con evidencia local»; encajaría como informe exploratorio o de
sistema/benchmark-piloto, no como resultado sobre capacidad policial.

## Fuentes registradas (2026-10-13)

Detalle, resumen, verificación y límites en [BIBLIOGRAPHY](BIBLIOGRAPHY.md#s7).

| Técnica | Fuentes | Estado |
|---|---|---|
| Trayectorias de agentes | S7 τ-bench, S8 AgentBoard | Texto leído por extracción; ambas exigen estado/subobjetivos correctos que PL-001 no tiene |
| Detección por afirmación (Q1) | S9 FActScore | Unidad de análisis respaldada; fuente de referencia propia por diseñar |
| Juez LLM | S2, S10, S11 | Sesgo de orden y autopreferencia documentados; S2 sigue en nivel resumen |
| Adversarial del arnés | S12 Greshake, S13 AgentDojo | S12 por analogía (no trata LLM→LLM); S13 modelo de comprobación por estado |
| Acuerdo entre anotadores | S14 Artstein y Poesio | Metadatos y resumen; texto sin leer |

No se buscaron fuentes para golden datasets/calibración de rúbricas: fuera del alcance
cerrado hoy; se retoman al diseñar la rúbrica de Q1 (LAB-021, resto).

Pendiente: lectura íntegra por una persona de las fuentes en que se base una decisión
metodológica; fuentes de golden datasets/calibración de rúbricas; revisar si los
preprints tienen versión publicada. Cierre de LAB-021 no implica validar nada de PL-001.
