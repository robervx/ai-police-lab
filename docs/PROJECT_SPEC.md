# PROJECT_SPEC — AI Police Lab v0.1

## Dirección y seguimiento vigentes

Decisión del usuario, 2026-10-09: priorizar una **demostración funcional** para
explorar investigación y formación antes de seleccionar una de esas vías.
El estado por fase y sus evidencias se mantienen en [PROJECT_STATUS.md](../PROJECT_STATUS.md).
Las responsabilidades del equipo están en [ROLES.md](governance/ROLES.md).
Los criterios científicos se preparan como borrador; no convierten la demo en
un estudio ni amplían automáticamente su alcance a rankings o eficacia formativa.

## Objetivo de producto
Ejecutar PL-001 en cuatro sesiones aisladas, una por modelo, mostrando su interacción con ciudadanos simulados y registrando eventos verificables. Construir primero versión headless con dos modelos y un ciudadano de respuesta controlada; habilitar un ciudadano LLM después de validar invariantes; añadir arena visual y otros dos modelos al final.

## Fuera de alcance v0.1
Diagnóstico psicológico del ciudadano, toma de decisiones policiales reales, rankings científicos, voz, vídeo, acceso a sistemas policiales, datos personales, guardias autónomos con acción externa, cálculo de eficacia operativa real.

## Stack recomendado
- Python 3.11+ / FastAPI / Pydantic v2 / pytest
- SQLite + SQLAlchemy o sqlite3 para el MVP
- React + TypeScript + Vite para cuatro visores
- WebSocket de backend a frontend con eventos persistidos antes de emitir
- APIs de OpenAI, Anthropic y Google en adaptadores separados; modelo abierto por Ollama si el hardware lo permite
- `.env` local fuera de Git; nunca guardar tokens de API en las trazas

## Arquitectura
`UI -> FastAPI Orchestrator -> SessionManager -> Policy/Rules Engine -> Scenario State Store`

Adaptadores separados:
- `PoliceModelAdapter`: recibe mensaje público, herramientas permitidas, estado conversacional del propio agente; devuelve UNA acción JSON válida, o un error controlado.
- `CitizenActorAdapter`: recibe hechos revelables para personaje seleccionado y su estado social; devuelve una intervención textual, sin autoridad sobre el estado.
- `RuleEngine`: valida autorización, aplica resultado objetivo, revela hechos, calcula transiciones y confirma evento.
- `EventStore`: append-only por sesión. Registro íntegro de acciones/resultados/timestamps/configuraciones.
- `ArenaBroadcaster`: transmite eventos confirmados, no genera cambios de estado.

## Equidad mínima
- Versión de escenario y semilla fijadas por ejecución.
- Idéntico prompt-base semántico, límites de turnos, catálogo de herramientas y presupuesto de salida.
- Historial independiente entre participantes. Ningún resultado de evaluación en contexto del agente.
- Registrar proveedor, `model_id` exacto, fecha, sampling settings, versión de los prompts, `max_output_tokens`, número de llamadas y tokens/coste si está disponible.
- **No equiparar** tiempo de red a calidad de razonamiento. Separar latencia wall-clock, turnos y tiempo narrativo simulado.
- Si el comportamiento del ciudadano es estocástico, registrar versión/modelo/semilla si hay soporte y repetir ensayos; si no la hay, declarar esta limitación.

## Camino incremental
M0: parser YAML + validación de invariantes y tests.
M1: sesión determinista de referencia en CLI, con acciones simuladas.
M2: conectar GPT + Claude y registrar eventos sin frontend.
M3: ciudadano LLM híbrido, validación de revelaciones y pruebas de consistencia.
M4: arena React 2 visores, streaming de eventos, reproducción.
M5: ampliar a 4 modelos, pruebas de repetición y exportación JSONL/CSV.

## Modelo de datos mínimo
`scenario_versions(id,version,sha256,body)`
`runs(id,scenario_id,scenario_version,status,started_at,ended_at,run_config_json)`
`participants(id,run_id,provider,model_id,settings_json)`
`sessions(id,participant_id,state_json,turn,status)`
`events(id,session_id,seq,type,actor,payload_json,wall_time,elapsed_ms)`

No registrar claves. Usar un `seq` monotónico por sesión y `run_id` correlativo para reconstruir el replay. Versionar estructura de eventos (`event_schema_version`).

## Datos visibles en arena
Cuatro carriles: mensaje ciudadano, respuesta policial, llamada de herramienta, observación, estado de sesión, turno y tiempo transcurrido. Panel lateral: texto del aviso, indicadores públicos, condiciones de cierre. No mostrar los hechos ocultos al competidor ni el evaluador durante carrera.

## Criterio de entrega MVP inicial
Dos sesiones aisladas completan >= 3 intercambios, sin filtración de hechos ocultos, con export de eventos que permita reconstruir secuencia, modelo y configuración exactos.

Este criterio corresponde al MVP inicial sin interfaz gráfica (M2 validado con
servicios reales). La demo visual de dos carriles corresponde a M4 y la arena de
cuatro a M5. «Reconstruir secuencia» significa replay cronológico en el alcance
actual, no reanudación ni regeneración idéntica de respuestas.
