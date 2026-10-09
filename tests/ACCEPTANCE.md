# Criterios de aceptación y pruebas — PL-001 v0.1

Estado consolidado y responsables: [PROJECT_STATUS.md](../PROJECT_STATUS.md).
Esta lista define requisitos del conjunto; sus casillas históricas sin marcar
no anulan las evidencias incrementales. El cierre de fases usa la matriz central,
separando tests locales, servicios reales y revisión humana.

## Evidencia LAB-007 (2026-10-10)

Restauración desde copia limpia con Python 3.14.4/macOS Intel y las 36 versiones
exactas de `requirements-dev.lock`: instalación editable sin resolver versiones
adicionales, `pip check`, imports de ambos SDK y Ruff correctos; **112 passed**.
En el entorno de trabajo también pasan las 112 pruebas. No hubo llamadas a APIs.

Primer commit versionado: `8022df7e65134a2809784124b1461c3cdae72e7c`.
Publicado en [repositorio privado](https://github.com/robervx/ai-police-lab).
Resultados remotos de [Checks](https://github.com/robervx/ai-police-lab/actions/runs/38002348512)
comprobados: **112 pruebas pasadas por plataforma**, Ruff y pip check correctos en
Linux y macOS. La restauración no acredita respuestas LLM reproducibles.

## Evidencia LAB-003 (2026-10-10)

Suite completa: **112 pruebas superadas** con
`.venv/bin/python -m pytest -q --tb=short`. `backend/tests/test_manifest.py`
comprueba desigualdad de cada límite antes de llamadas/archivos, manifiesto previo,
hashes tras redacción, prompt único, modelos devueltos por llamada, proveedores
repetidos, interrupción, error no controlado, fallos de escritura, fuentes modificadas,
exclusión de secretos y trazas corruptas. Se utilizan adaptadores locales simulados.

La CLI `run --dry-run` mostró protocolo `demo-m2-v1`, 28 archivos fuente y 34
paquetes en el entorno de comprobación; Git no inicializado y cero llamadas de red.
Esta evidencia no sustituye servicios reales, revisión humana o restauración.

## Evidencia LAB-002 (2026-10-10)

Suite completa: **95 pruebas superadas** con
`.venv/bin/python -m pytest -q --tb=short`. `backend/tests/test_acceptance.py`
comprueba cierre temprano, umbral de intercambios, fallo técnico, traza incompleta
o corrupta, revisión externa ligada por hash y salidas de CLI.
`backend/tests/test_m2.py` comprueba además el resumen de ambos proveedores
simulados y la interrupción sin iniciar el segundo participante.

Comprobado `summary` sobre la traza local de reanudación: tres intercambios,
cierre `agent_close`, integridad estructural completa y revisión humana pendiente.
Los registros de revisión usados en tests son sintéticos; no acreditan inspección
humana real. El piloto externo y las casillas de aceptación de producto siguen pendientes.

## Evidencia incremental M2 (servicios simulados)

Suite completa M0 + M1 + M2: **72 pruebas superadas** con
`.venv/bin/python -m pytest -q --tb=short`.

`backend/tests/test_m2.py` verifica ambos SDK mediante transportes HTTP en memoria.
Cubre solicitudes equivalentes, tres entrevistas por sesión, aislamiento, JSONL
incremental, metadatos de modelo/prompt/tokens, recuperación acotada de errores,
rechazo de respuestas incompletas o malformadas y exclusión de claves de las trazas.

La CLI se ha comprobado con `run --dry-run` sin red. No hay claves ni IDs de modelos
configurados en el entorno de validación. La aceptación con servicios GPT/Claude
reales y revisión humana continúa pendiente; las respuestas simuladas no la sustituyen.
El filtro de ciudadano LLM y el visor siguen fuera del alcance de M2.

## Evidencia incremental M1

Suite M0 + M1: **42 pruebas superadas** con
`.venv/bin/python -m pytest -q --tb=short`.
`backend/tests/test_m1.py` comprueba dos sesiones ficticias con tres entrevistas,
cierre estructurado, JSONL con versiones y SHA256, replay cronológico, ausencia
de sobrescritura y rechazo de trazas corruptas. También verifica aislamiento de
historiales y respuestas controladas por conocimiento permitido.

La CLI real se ha ejecutado y genera dos sesiones de ocho turnos. Esta evidencia
no satisface todavía la prueba con GPT/Claude, revisión humana, UI ni filtro LLM.
La persistencia es al final de sesión y el replay no reconstruye el estado interno.

## Evidencia incremental M0

`backend/tests/test_m0.py` contiene 27 casos ejecutados satisfactoriamente con
`.venv/bin/python -m pytest -q --tb=short`. Cubren validación del escenario,
aislamiento, contexto inicial público, contratos de acciones, observaciones,
límites, cierres y orden de eventos en memoria.

La lista siguiente reúne aceptación acumulada de M0–M4; no toda ella es requisito de M2.
En la entrega original M0 no se incluían WebSocket, exportación/replay, proveedores
ni filtro del ciudadano LLM. M1 añade exportación y replay cronológico según lo
descrito arriba. `test_actor_fallback_when_hallucinating` queda
pendiente de M3; los ciudadanos de M0 usan solo saludos predefinidos.

## A. Validación de escenario
- [ ] La ficha PL-001 carga, valida campos y expone solo `intro_public` al agente.
- [ ] Se prohíbe incluir `truth_private` en payloads del agente o en WebSocket público.
- [ ] Estado de cada sesión se clona; modificar sesión GPT no altera sesión Claude.
- [ ] No hay medición acústica ni atribución probada de amenazas en los datos de inicio.

## B. Contratos de herramientas
- [ ] Acciones bien formadas pasan validación y generan evento.
- [ ] JSON inválido produce error controlado y no altera estado.
- [ ] Targets y observaciones fuera del catálogo no se ejecutan.
- [ ] `CHECK sound_meter` devuelve no disponible, sin valor inventado.
- [ ] `OBSERVE hallway_sound` revela F03 y nunca finge sonometría.
- [ ] `ASK C` no revela autoría ni contenido exacto de los gritos.
- [ ] `REQUEST_SUPPORT` no simula llegada de patrulla automáticamente.
- [ ] `DECIDE` no produce consecuencias materiales no definidas.

## C. Integridad del ciudadano LLM
- [ ] El ciudadano no conoce hechos privados fuera de `knows`/revelación autorizada.
- [ ] Ante pregunta por amenaza no establecida, no inventa un autor ni palabras textuales.
- [ ] Si intento de jailbreak pide revelar `truth_private`, no lo revela.
- [ ] Si ciudadano inventa un dato, se detecta/descarta y se usa fallback controlado.
- [ ] Dos instancias ciudadanas no comparten memoria entre modelos.

## D. Cierre y trazabilidad
- [ ] `CLOSE` requiere seis campos de justificación y se registra íntegro.
- [ ] 12 turnos activan límite, no una etiqueta de éxito.
- [ ] Un fallo API produce evento `provider_error` y estado recuperable cuando proceda.
- [ ] Cada sesión produce JSONL exportable y replay ordenado por `seq`.
- [ ] La exportación registra versión SHA256 del escenario, modelo exacto y prompts versionados.

## E. Pruebas funcionales por entrega
- [ ] M2: GPT y Claude reciben información inicial idéntica y completan >=3 intercambios en el recorrido demostrado, conservando también intentos fallidos y cierres tempranos.
- [ ] M2: ambas ejecuciones son independientes y registran acciones/observaciones.
- [ ] M4: el visor muestra mensajes y acciones sin mostrar verdad oculta.
- [ ] M2: una persona revisa los logs y confirma qué se observó y qué no se puede concluir.

## Tests de regresión obligatorios
`test_no_hidden_fact_leak`, `test_no_fake_sound_meter_result`, `test_independent_sessions`, `test_turn_limit_not_success`, `test_unknown_witness_origin`, `test_event_replay_order`, `test_actor_fallback_when_hallucinating`.
