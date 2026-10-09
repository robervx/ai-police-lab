# AI POLICE LAB — estado del proyecto

**Actualización:** 2026-10-10 · **Responsable de mantenimiento:** Project Manager,
integrado por el agente coordinador · **Revisión:** [REV-001](docs/governance/reviews/2026-10-09.md).

## Dónde estamos

**Estamos en M2: integración construida y validada con servicios simulados;
pendiente de comprobación con OpenAI y Anthropic reales.**

La prioridad elegida por el usuario es una **demo funcional para explorar después
investigación y formación**. Aún no se elige una de esas dos vías como producto final.
El código permite observar acciones y trazas; no demuestra qué modelo es «mejor policía».

- Evidencia renovada el 2026-10-10: **112 pruebas pasadas** con
  `.venv/bin/python -m pytest -q --tb=short`; demo M1 con dos trazas de 26 eventos,
  ambas con cierre y leídas mediante `read_events`; M2 `--dry-run` sin red.
  Ejecución local: `results/private/1df410d1-8359-4256-96e7-a64323c9358a/`.
- Configuración externa comprobada el 2026-10-10: no existe `.env` ni están
  presentes las dos claves y los dos IDs requeridos en el entorno. Solo se
  comprobó su presencia, sin mostrar valores. El piloto real sigue pendiente.
- LAB-002 validado localmente: resumen automático y comando `summary`, con cierre,
  intercambios, integridad estructural y revisión humana externa vinculada por hash.
  [Revisión técnica y evidencia](docs/governance/reviews/2026-10-10-lab002.md).
- LAB-003 validado localmente: manifiesto previo, comprobación de límites y
  resultados observados vinculados por hash.
  [Revisión técnica y evidencia](docs/governance/reviews/2026-10-10-lab003.md).
- LAB-007: Git local inicializado, Python 3.14.4 y 36 paquetes fijados; restauración
  en copia limpia con 112 pruebas y lint correctos. [Desarrollo](docs/DEVELOPMENT.md).
  CI Linux/macOS preparada; publicación y primera ejecución remota en comprobación.
  Siguiente prioridad funcional: preparar el piloto LAB-001.
- Próximo resultado útil: dos sesiones reales inspeccionables y un resumen que
  distinga ejecución, intercambios y revisión de la traza.
- No hay tareas automáticas en segundo plano. Este estado se mantiene al trabajar
  en el proyecto; una fecha antigua indica que debe revisarse.

## Fases y criterios de salida

| Fase | Entrega | Estado verificable | Evidencia existente | Falta para salir de la fase |
|---|---|---|---|---|
| M0 | Escenario, validación, motor y aislamiento | Validado localmente | `backend/tests/test_m0.py`; 27 casos en entrega original | Sin pendientes del alcance local conocido; no acredita validez científica |
| M1 | Dos agentes ficticios, CLI y JSONL | Validado localmente | `backend/tests/test_m1.py`; demo ejecutada; [M1](docs/M1.md) | Sin pendientes del alcance local conocido; no incluye modelos reales |
| M2 | OpenAI + Anthropic, errores y trazas | Validado localmente; validación externa pendiente | `backend/tests/test_m2.py`; `run --dry-run`; 112 casos acumulados | Piloto con IDs concretos, ≥3 intercambios por participante en el recorrido demostrado, traza completa, inspección humana y límites documentados; conservar también intentos fallidos/cierres tempranos |
| M3 | Ciudadano híbrido y control de hechos | Pendiente | Contrato y referencia determinista M1 | Conocimiento permitido, reformulaciones controladas, detección de contradicciones, regeneración/fallback, aislamiento y regresión |
| M4 | Dos carriles visuales y replay | Pendiente | Especificación | Vista de mensajes/acciones fiel al log, separación público/privado, estados de error y replay verificable |
| M5 | Cuatro modelos y exportaciones ampliadas | Pendiente | Hoja de ruta | Configuraciones trazables, pruebas de repetición y exportaciones verificadas; no implica ranking científico |

**Niveles de entrega:** MVP inicial *sin interfaz gráfica* = M2 validado en vivo;
MVP visual de dos carriles = M4; arena de cuatro modelos = M5. Las pruebas de
integración no sustituyen la aceptación del producto con sus usuarios.

La madurez científica es una dimensión separada: **protocolo borrador y fuentes
iniciales**, sin estudio ejecutado, rúbrica validada ni evidencia de eficacia formativa.
Prepararla no bloquea la demo. [Plan científico](docs/research/PROTOCOL.md).

## Próximas acciones por orden

| Orden sugerido | Acción | Responsable | Estado / dependencia |
|---|---|---|---|
| 1 | [LAB-001](docs/governance/BACKLOG.md#lab-001) Validar el recorrido M2 real | Sénior IA + PM | Pendiente; requiere configuración local y revisión de trazas |
| 2 | [LAB-002](docs/governance/BACKLOG.md#lab-002) Resumen de aceptación de la demo | Producto + sénior IA | Validado localmente el 2026-10-10; 95 pruebas acumuladas |
| 3 | [LAB-003](docs/governance/BACKLOG.md#lab-003) Manifiesto y comprobación de condiciones | Sénior IA | Validado localmente el 2026-10-10; manifiestos y comprobación previa |
| 4 | [LAB-004](docs/governance/BACKLOG.md#lab-004) Definir comportamiento ciudadano M3 | Producto + sénior IA | Pendiente; conservar referencia M1 |

Tareas transversales de prioridad 1: [LAB-007](docs/governance/BACKLOG.md#lab-007)
(versionado/entorno: validado localmente; CI remota por comprobar) y [LAB-012](docs/governance/BACKLOG.md#lab-012)
(completar comprobación de perfiles; sénior invocado el 2026-10-10). La tabla ordena resultados funcionales;
las prioridades del backlog indican urgencia, no números de secuencia.

## Riesgos visibles

| ID | Riesgo observado | Consecuencia | Tratamiento |
|---|---|---|---|
| R-01 | M2 solo probado con HTTP simulado | No sabemos si el recorrido real cumple el MVP | LAB-001; no declarar validación externa |
| R-02 | Preguntas exactas y saludos predefinidos | La demo no mide entrevista libre | Etiquetar alcance; LAB-004 |
| R-03 | `run_session()` no proporciona `reviewed_tags` | Tensión/cooperación no cambian por el discurso de los modelos | LAB-005; no atribuir desescalada al resultado |
| R-04 | Defaults de proveedores, orden fijo, sin réplicas | Resultados no bastan para una clasificación neutral | LAB-003 registra condiciones y comprueba límites; LAB-006 y protocolo de estudio pendientes |
| R-05 | Entorno fijado y restaurado en macOS/Python 3.14.4; otras plataformas por comprobar | No acredita reproducción binaria ni de respuestas LLM | LAB-007 y CI; conservar lock y versión de Python junto al código |
| R-06 | JSONL durable por evento, sin atomicidad ni reanudación | Un corte puede dejar un turno/archivo incompleto | LAB-008; conservar el log y declarar incompletitud |

## Cómo mantener este estado

Una tarea pasa a «implementada» con artefacto; a «validada localmente» con ejecución
y evidencia; a «validada externamente» con servicio real; a «aceptada» con el criterio
de salida cubierto y revisión registrada. Anotar fecha, responsable y enlace.
No estimar porcentajes ni fechas de entrega sin base. Los asuntos no comprobados
son pendientes, nunca aprobaciones implícitas.

Documentos de trabajo: [roles](docs/governance/ROLES.md) ·
[backlog](docs/governance/BACKLOG.md) · [decisiones](docs/governance/DECISIONS.md) ·
[neutralidad](docs/governance/COMPARABILITY.md) · [bibliografía](docs/research/BIBLIOGRAPHY.md).
