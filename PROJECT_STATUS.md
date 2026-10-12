# AI POLICE LAB — estado del proyecto

**Actualización:** 2026-10-13 · **Responsable de mantenimiento:** Project Manager,
integrado por el agente coordinador · **Revisión actual:** [M5](docs/governance/reviews/2026-10-10-m5.md).

## Dónde estamos

**Demo M5 implementada y validada localmente: 2/4 participantes, cuatro proveedores
admitidos y exportaciones públicas JSON/JSONL/CSV. Pilotos reales y aceptación
humana pendientes; no se ha realizado un estudio científico.**

La prioridad elegida por el usuario es una **demo funcional para explorar después
investigación y formación**. Aún no se elige una de esas dos vías como producto final.
El código permite observar acciones y trazas; no demuestra qué modelo es «mejor policía».

- Última validación local (LAB-013/018, 2026-10-10): **225 pruebas pasadas**, Ruff
  y sintaxis JavaScript correctos. Chrome: 2/4 carriles, replay, escritorio/móvil,
  descargas JSON/JSONL/CSV y selección fallida sin datos anteriores.
  [Guía M5](docs/M5_DEMO.md) · [Revisión de cierre](docs/governance/reviews/2026-10-10-m5.md).
- Evidencia anterior de M2/LAB-007 del 2026-10-10: **112 pruebas pasadas** con
  `.venv/bin/python -m pytest -q --tb=short`; demo M1 con dos trazas de 26 eventos,
  ambas con cierre y leídas mediante `read_events`; M2 `--dry-run` sin red.
  Ejecución local: `results/private/1df410d1-8359-4256-96e7-a64323c9358a/`.
- Configuración externa comprobada el 2026-10-10: sin `.env`, claves OpenAI,
  Anthropic o Gemini en el entorno, ni binario Ollama disponible. Se comprobó
  presencia sin mostrar valores. No hay evidencia de cuatro modelos reales.
- LAB-002 validado localmente: resumen automático y comando `summary`, con cierre,
  intercambios, integridad estructural y revisión humana externa vinculada por hash.
  [Revisión técnica y evidencia](docs/governance/reviews/2026-10-10-lab002.md).
- LAB-003 validado localmente: manifiesto previo, comprobación de límites y
  resultados observados vinculados por hash.
  [Revisión técnica y evidencia](docs/governance/reviews/2026-10-10-lab003.md).
- LAB-007: Git local inicializado, Python 3.14.4 y 36 paquetes fijados; restauración
  en copia limpia con 112 pruebas y lint correctos. [Desarrollo](docs/DEVELOPMENT.md).
  [Repositorio público](https://github.com/robervx/ai-police-lab) publicado en `main`.
  [Primera CI Linux/macOS superada](https://github.com/robervx/ai-police-lab/actions/runs/38002348512); 112 pruebas por plataforma.
  Esa CI corresponde a la entrega de 112 pruebas; M5 se ha validado localmente.
- Próximo resultado útil: revisar la demo M5 y preparar un piloto configurado
  que conserve todos los intentos y permita inspección humana.
- LAB-008 validado localmente: inspección de prefijos de trazas dañadas en lectura,
  con hash y ubicación del primer error. [Guía](docs/TRACE_INSPECTION.md).
- LAB-004/015: contrato e integración local en `demo --citizen-mode guarded-local`,
  con selectores propios por sesión/actor y diagnóstico privado persistido.
  [Recorrido integrado](docs/CITIZEN_INTEGRATION.md). LAB-016 incorpora selector API con pruebas HTTP simuladas.
- LAB-009: visor local disponible mediante `arena`, con proyección pública, replay y
  actualización cada dos segundos. [Revisión de los cuatro roles](docs/governance/reviews/2026-10-10-m4.md).
- Alcance vigente: tras M4, el usuario pide completar la siguiente fase M5.
  [DEC-007](docs/governance/DECISIONS.md#dec-007--ampliación-m5-autorizada) actualiza
  el límite de DEC-006 sin cambiar el ciudadano cerrado ni introducir puntuaciones.
- GitHub Actions ejecuta checks en cada push/PR. No hay agentes de gestión en
  segundo plano; este estado se mantiene al trabajar en el proyecto.

## Dirección propuesta (2026-10-13, pendiente de confirmar)

El usuario quiere cuatro modelos en paralelo sobre una situación concreta, con
situaciones intercambiables, para observar decisiones, estructura, sesgos y mejoras,
**lo más cercano posible a un experimento científico**, empezando por un escenario
elaborado y dejando el marco listo para más. Propuesta en
[DEC-008](docs/governance/DECISIONS.md#dec-008--dirección-experimental-con-escenario-único-elaborado-propuesta)
y [LAB-022](docs/governance/BACKLOG.md#lab-022). No se ha implementado nada de esto;
hoy solo existe PL-001 y la demo M5. Se retoma en la siguiente sesión.

**Para retomar, el usuario debe decidir:** (1) tema del escenario (recomendado:
versiones contradictorias con riesgo ambiguo); (2) dimensión de sesgo a manipular,
una sola con dos condiciones; (3) quién anota (revisión humana ciega).
Si no hay preferencia se avanza con la recomendación como decisión revisable.

## Fases y criterios de salida

| Fase | Entrega | Estado verificable | Evidencia existente | Falta para salir de la fase |
|---|---|---|---|---|
| M0 | Escenario, validación, motor y aislamiento | Validado localmente | `backend/tests/test_m0.py`; 27 casos en entrega original | Sin pendientes del alcance local conocido; no acredita validez científica |
| M1 | Dos agentes ficticios, CLI y JSONL | Validado localmente | `backend/tests/test_m1.py`; demo ejecutada; [M1](docs/M1.md) | Sin pendientes del alcance local conocido; no incluye modelos reales |
| M2 | OpenAI + Anthropic, errores y trazas | Validado localmente; validación externa pendiente | `backend/tests/test_m2.py`; `run --dry-run`; pruebas HTTP simuladas | Piloto con IDs concretos, ≥3 intercambios por participante en el recorrido demostrado, traza completa, inspección humana y límites documentados; conservar también intentos fallidos/cierres tempranos |
| M3 | Ciudadano con selección cerrada para esta demo | API implementada; validación HTTP simulada | [Contrato](docs/CITIZEN_CONTRACT.md), [API](docs/CITIZEN_API.md), pruebas de aislamiento/presupuesto/fallback | Piloto real LAB-017; conversación libre y detección general de contradicciones del diseño original no implementadas |
| M4 | Dos carriles visuales y replay | Validado localmente | Servidor loopback, proyección por campos, pruebas HTTP y navegador Chrome; [guía](docs/M4_DEMO.md) | Aceptación humana pendiente; piloto real M2/M3 sigue separado |
| M5 | 2/4 participantes, cuatro proveedores y exportaciones | Validado localmente | 225 pruebas acumuladas, repetición de guion, Chrome 2/4 y descargas; [guía](docs/M5_DEMO.md) | Entrega técnica local cerrada; piloto de cuatro modelos LAB-019 y aceptación humana pendientes |

**Niveles de entrega:** MVP inicial *sin interfaz gráfica* = M2 validado en vivo;
MVP visual de dos carriles = M4; arena de cuatro modelos = M5. Las pruebas de
integración no sustituyen la aceptación del producto con sus usuarios.

La madurez científica es una dimensión separada: **protocolo borrador y fuentes
iniciales**, sin estudio ejecutado, rúbrica validada ni evidencia de eficacia formativa.
Prepararla no bloquea la demo. [Plan científico](docs/research/PROTOCOL.md). Desde 2026-10-13 hay además una
[valoración de prácticas de evaluación](docs/research/EVALUATION_PRACTICES.md) y 14
fuentes registradas (S1–S14, lectura por resumen o extracción, no revisión humana);
seguimiento en [LAB-021](docs/governance/BACKLOG.md#lab-021), prioridad 3.

## Próximas acciones por orden

| Orden sugerido | Acción | Responsable | Estado / dependencia |
|---|---|---|---|
| 0 | Confirmar [DEC-008](docs/governance/DECISIONS.md#dec-008--dirección-experimental-con-escenario-único-elaborado-propuesta) y arrancar [LAB-022](docs/governance/BACKLOG.md#lab-022) (protocolo + PL-002) | Usuario + ciencia + sénior IA | Esperando las tres decisiones de arriba |
| 1 | Revisar la [demo visual M5](docs/M5_DEMO.md) | Usuario + producto | Entrega técnica local lista; aceptación humana pendiente |
| 2 | [LAB-019](docs/governance/BACKLOG.md#lab-019) Piloto de cuatro participantes, coordinado con LAB-001 | Sénior IA + PM | Requiere claves/IDs, Ollama/modelo y condiciones de hardware |
| 3 | [LAB-017](docs/governance/BACKLOG.md#lab-017) Piloto ciudadano API y revisión visual real | Sénior IA + usuario | Requiere configuración ciudadana y revisión de trazas |
| 4 | [LAB-021](docs/governance/BACKLOG.md#lab-021) Resto de la vía de paper: lectura humana de fuentes, rúbrica Q1, pruebas adversariales | Ciencia + sénior IA | Prioridad 3; depende de LAB-006/011 y de elegir vía |
| 5 | [LAB-010](docs/governance/BACKLOG.md#lab-010) Elegir vía tras observar la demo | Usuario + producto | Decisión posterior; investigación/formación no validadas |

Siguiente acción de usuario: abrir la demo y revisar el recorrido; para validación
externa, configurar claves/IDs localmente y ejecutar LAB-019/017. No se solicitan
secretos en el chat. La entrega técnica local no equivale a aceptación humana.

Tareas transversales de prioridad 1: [LAB-007](docs/governance/BACKLOG.md#lab-007)
(versionado/entorno: restaurado localmente y checks remotos superados) y [LAB-012](docs/governance/BACKLOG.md#lab-012)
(cuatro perfiles invocados y fichas revisadas el 2026-10-10). La tabla ordena resultados funcionales;
las prioridades del backlog indican urgencia, no números de secuencia.

## Riesgos visibles

| ID | Riesgo observado | Consecuencia | Tratamiento |
|---|---|---|---|
| R-01 | Adaptadores solo probados con HTTP simulado | No sabemos si el recorrido real cumple el MVP | LAB-001/019; no declarar validación externa |
| R-02 | Preguntas exactas y saludos predefinidos | La demo no mide entrevista libre | Etiquetar alcance; LAB-004 |
| R-03 | `run_session()` no proporciona `reviewed_tags` | Tensión/cooperación no cambian por el discurso de los modelos | LAB-005; no atribuir desescalada al resultado |
| R-04 | Defaults de proveedores, orden fijo, sin réplicas | Resultados no bastan para una clasificación neutral | LAB-003 registra condiciones y comprueba límites; LAB-006 y protocolo de estudio pendientes |
| R-05 | Entorno fijado, restaurado localmente y probado en CI Linux/macOS con Python 3.14.4 | No acredita reproducción binaria ni de respuestas LLM | LAB-007 y CI; conservar lock y versión de Python junto al código |
| R-06 | JSONL durable por evento, sin atomicidad ni reanudación | Un corte puede dejar un turno/archivo incompleto | LAB-008 permite inspeccionar el prefijo sin reparar ni aceptar la traza; conservar el original |

## Cómo mantener este estado

Una tarea pasa a «implementada» con artefacto; a «validada localmente» con ejecución
y evidencia; a «validada externamente» con servicio real; a «aceptada» con el criterio
de salida cubierto y revisión registrada. Anotar fecha, responsable y enlace.
No estimar porcentajes ni fechas de entrega sin base. Los asuntos no comprobados
son pendientes, nunca aprobaciones implícitas.

Documentos de trabajo: [roles](docs/governance/ROLES.md) ·
[backlog](docs/governance/BACKLOG.md) · [decisiones](docs/governance/DECISIONS.md) ·
[neutralidad](docs/governance/COMPARABILITY.md) · [bibliografía](docs/research/BIBLIOGRAPHY.md).
