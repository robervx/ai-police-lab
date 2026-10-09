# AI Police Lab — starter de especificaciones v0.1

MVP de simulación híbrida de intervenciones policiales ficticias. **No es un sistema de apoyo policial real ni una evaluación científica validada.**

## Seguimiento y equipo

**Empieza por [PROJECT_STATUS.md](PROJECT_STATUS.md):** fases, dónde estamos,
evidencias, riesgos y próximos pasos. La prioridad acordada es una **demo funcional
para explorar investigación y formación**. M2 está validado con servicios simulados;
su aceptación con proveedores reales sigue pendiente.

El proyecto dispone de cuatro roles de gestión y revisión: Project Manager,
Product Manager, desarrollador sénior de IA y director científico. Sus
[responsabilidades y forma de invocarlos](docs/governance/ROLES.md) quedan en
fichas persistentes y `AGENTS.md`. Se activan al trabajar en el proyecto;
no son procesos de vigilancia continua ni participantes de la simulación.

- [Backlog priorizado](docs/governance/BACKLOG.md) y [decisiones](docs/governance/DECISIONS.md).
- [Revisión inicial del equipo](docs/governance/reviews/2026-10-09.md).
- [Condiciones de comparabilidad](docs/governance/COMPARABILITY.md).
- [Borrador científico](docs/research/PROTOCOL.md) y [bibliografía anotada](docs/research/BIBLIOGRAPHY.md).

## Documentos

- `docs/PROJECT_SPEC.md`: alcance, arquitectura, módulos, hitos y decisiones técnicas.
- `scenarios/PL-001.yaml`: verdad sintética, información conocida/oculta, actores, estado inicial, observaciones y cierres.
- `schemas/action.schema.json`: contrato JSON Schema de la acción solicitada por el agente.
- `docs/SIMULATOR_CONTRACT.md`: ciclo de turnos, simulador ciudadano híbrido, controles y trazabilidad.
- `tests/ACCEPTANCE.md`: pruebas de aceptación, casos extremos y criterios de salida.
- `docs/VS_CODE_START.md`: guía de implementación por incrementos para trabajar con Codex o Claude Code en VS Code.
- [Recorrido del código M2, parte por parte](docs/M2_CODE_TOUR.md).

## Entorno de desarrollo

Para restaurar las versiones verificadas, sigue [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md):
Python fijado en `.python-version`, dependencias en `requirements-dev.lock`, Ruff
y suite completa. El workflow de GitHub ejecuta lint y pruebas simuladas en cada
push o pull request. Los comandos de instalación flexible que siguen son una
alternativa de desarrollo; no reproducen necesariamente las versiones del lock.

## Desarrollo incremental: M0 + M1 + integración M2

El primer incremento incorpora carga YAML con Pydantic v2, validación de acciones
contra el JSON Schema existente, sesiones aisladas y motor determinista con eventos
en memoria. M1 añade CLI, diálogo controlado y exportación JSONL.
M2 incorpora adaptadores de OpenAI/Anthropic y trazas por evento. Su integración
está probada con los SDK y respuestas HTTP simuladas; falta verificar cuentas y modelos reales.
Requiere Python 3.11+; trabajar desde la raíz del repositorio.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

### Ejecutar la demo M1

```sh
.venv/bin/python -m backend.app.cli demo
```

Ejecuta dos agentes ficticios con el mismo guion, en sesiones independientes.
Cada sesión completa tres entrevistas, comprobaciones y un cierre estructurado
en ocho turnos. La terminal muestra la cronología y la ruta de cada JSONL dentro de
`results/private/<run_id>/`. No requiere claves ni conexión a proveedores.

Para reproducir la cronología, usa una de las rutas indicadas por la demo:

```sh
.venv/bin/python -m backend.app.cli replay results/private/<run_id>/ficticio-1.jsonl
```

Sustituye `<run_id>` por el identificador real. `demo` admite `--seed 42` y
`--output otra/carpeta`. La semilla queda registrada; este guion no usa aleatoriedad.
Cada ejecución crea una carpeta nueva y la exportación rechaza sobrescribir archivos.
El replay valida estructura, secuencia e identidad de sesión; muestra eventos,
sin volver a ejecutar acciones ni reconstruir el estado interno del motor.

Ejemplo de uso del núcleo desde Python:

```python
from backend.app.scenario_loader import load_scenario
from backend.app.session_manager import SessionManager
from backend.app.rules import RuleEngine

scenario, sha256 = load_scenario()
manager = SessionManager(scenario, sha256, scene_seed=42)
session = manager.create("agente-ficticio-1")
engine = RuleEngine()
print(session.public_context())
print(engine.execute(session, {
    "action": "OBSERVE", "observation_id": "hallway_sound"
}))
```

### Revisar y ejecutar M2

Para seguir la implementación en el editor, abre
[docs/M2_CODE_TOUR.md](docs/M2_CODE_TOUR.md): contrato, prompt, adaptadores,
ciclo de turnos, persistencia, CLI y pruebas, en ese orden.

Instala las dependencias de proveedores y ejecuta toda la suite:

```sh
.venv/bin/python -m pip install -e '.[test,providers]'
.venv/bin/python -m pytest -q
```

Puedes revisar la configuración sin claves ni llamadas de red:

```sh
.venv/bin/python -m backend.app.cli run \
  --openai-model modelo-openai \
  --anthropic-model modelo-anthropic \
  --dry-run
```

Estos nombres son marcadores de ejemplo. Para ejecutar los proveedores, crea `.env`
a partir de `.env.example` y configura `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
`OPENAI_MODEL_ID` y `ANTHROPIC_MODEL_ID` con los valores de tus cuentas.
El código no selecciona un modelo automáticamente ni muestra las claves.

```sh
.venv/bin/python -m backend.app.cli run
```

`run` realiza llamadas de API y consume tokens. Por defecto limita cada sesión a
16 llamadas, 1500 tokens de salida por llamada y 12 turnos válidos; admite un
reintento por error transitorio. Los tokens de entrada también se facturan según
el proveedor: estos límites no son un presupuesto monetario. Puedes configurar
`--max-calls`, `--max-output-tokens`, `--max-retries` y `--timeout`.

La terminal muestra la ruta del JSONL al iniciar cada proveedor. El archivo se
actualiza durante la ejecución y se puede abrir en VS Code o leer con `replay`.
La traza incluye prompt, historial enviado, modelo solicitado/devuelto, versión
del SDK, latencia, tokens y errores controlados. El coste queda como `null` al
no disponer de tarifas configuradas. La semilla identifica el escenario local;
no garantiza que los proveedores produzcan la misma respuesta al repetir.

`run` devuelve código 1 ante un cierre por fallo de proveedor o límite de llamadas,
y 130 ante Ctrl+C. Un cierre normal o por 12 turnos devuelve 0, sin indicar calidad
ni éxito policial. La comparación es secuencial y mantiene historiales independientes.

`Scenario`, `Session.state` y los eventos son objetos internos del servidor;
el contexto inicial del agente se obtiene exclusivamente con `public_context()`.
Los eventos contienen las acciones recibidas y no deben exponerse como un canal
público sin la revisión prevista para fases posteriores.

ASK responde mediante un catálogo versionado de preguntas exactas y comprueba
el conocimiento permitido del personaje. Las preguntas no reconocidas reciben
una respuesta de desconocimiento; C conserva su declaración prudente inicial.
SPEAK devuelve el saludo del personaje. Esto no es comprensión de lenguaje natural.
Los testimonios no se añaden a las observaciones verificadas. Las reglas
sociales solo se aplican con `reviewed_tags` proporcionadas por código de confianza;
el texto del agente no genera etiquetas. `demo` exporta al finalizar cada sesión;
`run` escribe cada evento con `flush` y `fsync`. No hay transacción atómica de
turno ni reanudación desde la traza: un corte abrupto puede dejarla incompleta.
El ciudadano sigue siendo controlado; no hay filtro de alucinaciones LLM ni frontend.

Las reglas sociales existen en el motor, pero el recorrido actual de `run` no
proporciona `reviewed_tags` y el ciudadano no usa tensión/cooperación para responder.
Por tanto, esta demo no mide efectos de empatía ni desescalada (LAB-005 del backlog).

Pendiente para validar M2 en vivo: configurar ambas cuentas y modelos, ejecutar
`run` y revisar los logs. Después, M3 incorpora ciudadano LLM; M4, interfaz visual.

### Resumen por sesión (LAB-002)

`demo`, `run` y `replay` muestran un resumen con cierre registrado y motivo,
intercambios con el ciudadano, integridad estructural de la traza y revisión humana.
Puedes consultar una traza por separado, sin red ni claves:

```sh
.venv/bin/python -m backend.app.cli summary results/private/<run_id>/1-openai.jsonl
.venv/bin/python -m backend.app.cli summary results/private/<run_id>/1-openai.jsonl --json
```

Sustituye la ruta por un archivo existente. Cada `citizen_utterance` cuenta como un
intercambio ASK/SPEAK, incluidos saludos y respuestas de desconocimiento. Alcanzar
tres intercambios no acredita calidad de entrevista ni aceptación del MVP. Un cierre
por `provider_error`, `call_limit` o `interrupted` también termina una ejecución;
su motivo permanece visible.

La integridad comprueba formato, secuencia, identidad de sesión y ciclo de eventos,
con las mismas reglas del replay; además, el resumen exige un motivo de cierre
conocido. No autentica la traza ni valida completamente la semántica de sus payloads.
Una traza sin cierre figura como incompleta. Si está corrupta o truncada, cierre y
conteos quedan como no verificables (`null` en JSON); el archivo original se conserva.
El resumen describe una captura de los bytes leídos; no reanuda ni repara la sesión.

La revisión humana aparece como **pendiente** por defecto. Después de inspeccionar
una traza, una persona puede escribir un JSON externo con estos campos:

```json
{
  "reviewer_type": "human",
  "reviewer": "Nombre del revisor",
  "reviewed_at": "FECHA_ISO_8601_CON_ZONA_HORARIA",
  "notes": "Qué se observó y qué no puede concluirse",
  "trace_sha256": "SHA256_DE_LA_TRAZA_REVISADA"
}
```

Es una plantilla, no una revisión realizada. Sustituye los marcadores por la fecha
real (por ejemplo, formato `2026-10-10T12:00:00+02:00`) y el `trace_sha256` que muestra
`summary --json`. Guarda el registro fuera del JSONL y pásalo explícitamente:

```sh
.venv/bin/python -m backend.app.cli summary results/private/<run_id>/1-openai.jsonl \
  --review ruta/revision.json
```

El registro debe declarar autor humano, fecha con zona horaria, notas y hash exacto.
La CLI lo muestra como revisión realizada según declaración externa; no autentica
la identidad ni convierte las notas en aprobación automática. Revisar una traza
inválida no la repara. Si los bytes cambian o el registro no es válido, se rechaza
su asociación. No se envían estos registros a los modelos ni se modifica la traza.

`summary` devuelve 1 si la traza es inválida/no legible o el registro de revisión
aportado no es válido; devuelve 0 si pudo resumirla, incluso sin cierre o con menos
de tres intercambios. Los códigos de salida de `run` conservan su significado técnico.
Ningún código de salida indica aceptación del MVP ni calidad policial.

### Condiciones y manifiestos de ejecución (LAB-003)

Antes de iniciar una comparación, `run_comparison()` comprueba que los participantes
comparten límites nominales de salida, llamadas, reintentos y timeout. Si difieren,
rechaza la ejecución antes de crear su carpeta o llamar a los modelos. Los IDs y
proveedores pueden ser diferentes. Esto no acredita igual cómputo, coste o muestreo.

Cada `run` guarda en su carpeta privada:

- `manifest.json`: condiciones capturadas antes de las llamadas; versión/hash del
  [protocolo operativo](docs/RUN_PROTOCOL.md), hashes de fuentes, escenario, esquema
  y prompt, estado Git cuando exista, Python/plataforma/paquetes instalados,
  ciudadano, semilla local, modelos solicitados, límites, orden y política de fallos.
- `manifest-outcomes.json`: informe final enlazado al SHA256 del manifiesto inicial,
  con los IDs de modelo realmente devueltos por llamada, hashes/estado de las trazas
  y motivos de cierre. Se intenta guardar también tras errores o Ctrl+C; los
  participantes no intentados figuran como `not_started`.

El manifiesto inicial se conserva sin reescribir. `run_status=loop_completed` solo
indica que terminó el bucle, aunque hubiera fallos de proveedor. Los modelos sin
respuesta no reciben un ID resuelto inventado. Si una traza está corrupta, el informe
no calcula sus modelos resueltos: conserva el original para inspección posterior.
Si el proceso muere o falla el disco, el informe final puede faltar o quedar parcial;
su ausencia no permite concluir que la ejecución terminase.

`run --dry-run` muestra una vista previa del manifiesto, sin archivos ni red. No
valida credenciales, acceso a modelos ni respuestas. El prompt se captura una vez
por comparación. No modifiques las fuentes mientras se ejecuta: sus hashes describen
archivos en disco, no una verificación del código ya importado. Sin Git se registra
`commit: null` y se conserva el hash agregado; no se inventa una revisión.

Solo se guardan nombres/versiones de paquetes, no variables de entorno ni URLs de
instalación. Las claves configuradas se ocultan en los documentos. Estos registros
no se envían a los competidores. La restauración utiliza por separado el lock y
las instrucciones de [desarrollo](docs/DEVELOPMENT.md); el manifiesto no la verifica automáticamente. La demo ficticia `demo` conserva su
recorrido M1; los nuevos manifiestos pertenecen a `run`.

## Principios

1. Cada agente recibe el mismo caso inicial; ninguna instancia comparte información con otra.
2. La verdad del caso y el estado los conserva un motor determinista, no el LLM que interpreta a un ciudadano.
3. La respuesta textual de un LLM no produce por sí sola acciones policiales ni altera hechos del mundo.
4. Toda decisión, mensaje, herramienta, latencia, configuración y transición se registra.
5. La primera meta es una sesión reproducible con dos proveedores; la arena de cuatro visores llega después.

## Seguridad y límites

Solo casos ficticios y datos sintéticos. No introducir datos personales reales, expedientes ni operativa reservada. El entorno no instruye actuaciones policiales reales; cualquier criterio normativo se validará por expertos y jurisdicción antes del estudio formal.
