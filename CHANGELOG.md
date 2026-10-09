# Cambios

## 2026-10-10 — Repositorio público

- Visibilidad de `robervx/ai-police-lab` cambiada de privada a pública por petición
  expresa del usuario; verificada mediante GitHub CLI (`visibility: PUBLIC`).
- Actualizados estado, backlog y enlaces de aceptación. Las exclusiones de
  secretos, entornos y trazas privadas permanecen vigentes.

## 2026-10-10 — LAB-007: versionado, restauración y checks automáticos

- Inicializado Git local y preparadas exclusiones de claves, trazas y entornos.
- `.env.example` reducido a las cuatro variables M2; guía de VS Code actualizada.
- Python 3.14.4 y 36 dependencias exactas en `.python-version` y
  `requirements-dev.lock`, incluidos pip/setuptools/wheel y Ruff.
- Documentada instalación sin resolver dependencias ni backend fuera del lock.
- Configurado Ruff básico; corregido un import sin usar en `test_manifest.py`.
- Añadida CI Linux/macOS Intel con acciones oficiales fijadas a SHA, SDKs obligatorios,
  lint, pip check y pytest; sin claves de API. Primera CI superada en Linux/macOS,
  112 pruebas por plataforma. Ubuntu fijado a 24.04 tras aviso de migración del alias latest.
- Validación en entorno de trabajo: **112 passed**, Ruff y pip check correctos.
- Restauración en copia limpia macOS Intel/Python 3.14.4: versiones cotejadas con
  el lock, SDKs disponibles, pip check, Ruff y suite; evidencia en revisión LAB-007.
- Publicado en [robervx/ai-police-lab](https://github.com/robervx/ai-police-lab), privado;
  primer commit `8022df7`. [Primera CI superada](https://github.com/robervx/ai-police-lab/actions/runs/38002348512).
- Revisión sénior asesora y límites en [LAB-007](docs/governance/reviews/2026-10-10-lab007.md).
- Type-checking gradual pendiente en LAB-014. El piloto real M2 continúa pendiente.

## 2026-10-10 — LAB-003: manifiestos y condiciones previas

- Añadido `run_manifest.py` y protocolo operativo versionado `demo-m2-v1`.
- `run_comparison()` rechaza límites nominales distintos antes de crear ejecución;
  captura el prompt una vez y registra orden, ciudadano, semillas y política de fallos.
- `manifest.json` contiene hashes de fuentes/escenario/esquema/prompt, Git cuando
  exista y Python/plataforma/paquetes instalados. No registra variables de entorno.
- `manifest-outcomes.json` enlaza el hash inicial y registra IDs resueltos observados,
  trazas, cierres y participantes no iniciados; se intenta escribir ante interrupción.
- Fallos al escribir el informe final no ocultan la excepción original. La ausencia
  o corrupción del informe no acredita finalización. Sin transacción entre archivos.
- `run --dry-run` muestra vista previa sin archivos ni llamadas externas.
- Validación: **112 passed**; dry-run CLI comprobado con Git no inicializado,
  28 archivos fuente y 34 paquetes instalados en este entorno.
- Revisión sénior en lectura registrada en
  [revisión LAB-003](docs/governance/reviews/2026-10-10-lab003.md).
- LAB-007 sigue pendiente de versionado y restauración; LAB-013 recoge mejora futura
  de identificadores para varios modelos del mismo proveedor. M2 sigue sin piloto real.

## 2026-10-10 — LAB-002: resumen de aceptación de la demo

- Añadido resumen por sesión en `demo`, `run` (también al interrumpir) y `replay`,
  más `summary FILE [--json] [--review JSON]` sin llamadas de red.
- Separados cierre/motivo, conteo ASK/SPEAK, umbral de tres intercambios, integridad
  estructural y revisión humana; no se emiten puntuaciones ni aceptación automática.
- Trazas inválidas: totales no verificables; sin cierre: incompletas. Original intacto.
- Registro de revisión humana externo con autor, fecha, notas y hash exacto;
  declaración de autoría sin autenticación y fuera del contexto de participantes.
- Extraída validación compartida `parse_events` para resumir y calcular el hash
  sobre la misma captura de bytes, conservando reglas del replay.
- Validación: **95 pruebas pasadas**, incluida interrupción sin iniciar segundo
  proveedor; CLI `summary` comprobada con la traza local de la reanudación.
- Revisión sénior mediante subagente; límites y evidencia en
  [revisión LAB-002](docs/governance/reviews/2026-10-10-lab002.md).
- Piloto real y revisión humana de aceptación siguen pendientes.

## 2026-10-10 — Reanudación y comprobación de la base M2

- Reejecutada la suite: **72 passed** con `.venv/bin/python -m pytest -q --tb=short`.
- Ejecutada demo local: dos JSONL de 26 eventos, con cierre y lectura validada,
  en `results/private/1df410d1-8359-4256-96e7-a64323c9358a/`.
- Comprobado M2 `--dry-run` con IDs de ejemplo y cero llamadas de red.
- Confirmada ausencia de `.env`, claves/IDs en el entorno y repositorio Git.
- Invocado el perfil sénior en lectura; ficha de rol confirmada (LAB-012).
- Actualizado seguimiento: M2 sigue pendiente de piloto real y revisión humana;
  LAB-002 es el siguiente incremento autónomo recomendado. Sin cambios de backend.

## 2026-10-09 — Gestión del proyecto y cuatro roles

- Incorporada prioridad expresada por el usuario: demo funcional para explorar
  investigación y formación, sin decidir aún un producto o estudio formal.
- Añadido `PROJECT_STATUS.md` con fases, evidencias, criterios de salida y riesgos.
- Añadido `AGENTS.md` con el flujo de trabajo y responsabilidades persistentes.
- Añadidas fichas de Project Manager, Product Manager, sénior IA y director científico.
- Instalados cuatro perfiles de Codex en `.codex/agents/`, de lectura y con modelo
  heredado; TOML validado. Descubrimiento/invocación por nombre pendiente de verificar.
- Añadidos backlog LAB-001–012, registro de decisiones y revisión inicial REV-001.
- Primera revisión: coordinador en función PM y tres subagentes revisores de
  producto, comparabilidad y metodología. No constituye revisión humana independiente.
- Revisión final adicional por subagente PM: corregidos niveles de aceptación,
  orden/prioridades y distinción entre preparación, instalación e invocación de perfiles.
- Añadidos criterios de comparabilidad, borrador científico y seis fuentes primarias
  contrastadas, con alcance real de lectura y límites de aplicación.
- Documentadas capacidades parciales: M2 pendiente de servicios reales, catálogo
  ciudadano literal y reglas sociales sin activar en el recorrido de proveedores.
- Actualizados README, especificación y aceptación para enlazar el seguimiento.
- Sin cambios en backend, escenario o esquema. Las 72 pruebas citadas corresponden
  a M2; esta entrega verifica documentos/configuración, no vuelve a ejecutar pytest.
- Verificación de esta entrega: 21 documentos, 47 enlaces locales/anclas y cuatro
  perfiles TOML instalados comprobados correctamente.

## 2026-10-09 — M2: integración de proveedores y recorrido del código

- Añadido contrato común de adaptadores, configuración validada y respuestas normalizadas.
- Añadidos adaptadores OpenAI Responses y Anthropic Messages con SDKs opcionales,
  modelos configurables, timeout y control explícito de reintentos.
- Añadido prompt `police-json-v1`: mismo esquema y catálogo público para ambos proveedores.
- Añadido ciclo de sesiones con límite de llamadas, validación local de acciones,
  detección de respuestas incompletas, reintentos transitorios y cierres técnicos.
- Añadidos eventos de petición/respuesta/error con modelos, prompts, tokens,
  latencias, versiones de SDK y coste desconocido como null.
- Añadido JSONL incremental para `run`, con creación exclusiva, flush y fsync.
- Añadida ocultación de claves; no se guardan cuerpos de errores HTTP ni cabeceras.
- CLI `run` / `--dry-run`, carga de `.env` y opciones de modelos y presupuestos.
- Añadida guía `docs/M2_CODE_TOUR.md` con fragmentos y recorrido por archivos.
- El escenario y el JSON Schema de acciones se conservan sin modificaciones.

### Validación y límites

- SDKs instalados: OpenAI 3.27.0, Anthropic 0.125.0; Python 3.14.4.
- Pruebas con SDKs reales y transportes HTTP simulados; sin consumo de APIs.
- `.venv/bin/python -m pytest -q --tb=short`: **72 passed** (M0, M1 y M2).
- Comprobada la CLI `run --dry-run` con cero llamadas de red.
- No hay claves ni IDs reales configurados; la ejecución con servicios externos
  y la aceptación funcional con GPT/Claude quedan pendientes.
- Se solicita JSON por prompt y se valida localmente, sin salidas estructuradas nativas.
- El ciudadano sigue usando catálogo exacto de M1. No se incorpora ciudadano LLM.
- Las sesiones se ejecutan consecutivamente; sampling por defecto del proveedor,
  sin semilla de generación ni estimación monetaria. No se afirma equivalencia estadística.
- Durabilidad por evento, sin atomicidad de turno ni reanudación tras interrupción.

## 2026-10-09 — M1: CLI y trazas JSONL

- Añadidos `backend/app/cli.py`, `scripted_agent.py`, `citizen.py` y `event_store.py`.
- Actualizados `rules.py` y `session_manager.py` para registrar configuración e
  inicio de sesión incluso si la primera acción es rechazada.
- La demo ejecuta dos agentes locales con historiales separados, tres entrevistas
  por sesión y cierre en ocho turnos. El cierre separa observaciones y testimonios.
- Añadidas respuestas controladas por catálogo exacto y `knows`, sin modificar el YAML.
- Exportación JSONL exclusiva y replay cronológico con validación de secuencia.
- Documentados comandos y límites en README.md, docs/M1.md y docs/VS_CODE_START.md.
- Añadidas pruebas de integración, aislamiento conversacional, preguntas fuera de
  catálogo, protección frente a sobrescritura y rechazo de trazas corruptas.
- Verificación: `.venv/bin/python -m pytest -q --tb=short`: **42 passed**.
- Ejecutada la CLI real: dos sesiones cerradas en ocho turnos y dos JSONL generados.

### Límites de M1

- Persistencia al finalizar cada sesión; aún no hay escritura durable por evento.
- Replay de la cronología, sin reconstrucción ni reejecución del estado interno.
- Sin proveedores, comprensión semántica de preguntas, filtro LLM ni frontend.
- No se han modificado el escenario ni el esquema de acciones.

## 2026-10-09 — M0: núcleo determinista

- Añadida configuración Python, `.env.example` sin claves y `.gitignore`.
- Añadidos modelos Pydantic, carga YAML y SHA256 del archivo fuente.
- Añadidas sesiones con copias independientes del estado y escenario.
- Añadido motor con validación mediante el JSON Schema original, observaciones,
  comprobaciones, cierre estructurado, límite de turnos y reglas sociales etiquetadas.
- Añadidos eventos ordenados en memoria, devueltos como copias para proteger el registro.
- Añadidas pruebas de invariantes, aislamiento, acciones inválidas, revelaciones,
  ausencia de efectos materiales automáticos y determinismo de resultados.
- El escenario y el contrato JSON originales se conservan sin cambios.

### Límites y decisiones del incremento

- ASK/SPEAK usan exclusivamente saludos predefinidos; aún no responden semánticamente
  a las preguntas. La conversación controlada se desarrolla en M1.
- Persistencia, exportación y replay completo se difieren a M1; el test de orden
  verifica únicamente la secuencia de eventos en memoria.
- El fallback ante alucinaciones y su test corresponden a M3. No se simula un filtro
  LLM ni se marca ese criterio como superado en M0.
- No se conectan proveedores; sus errores, configuración, costes y prompts versionados
  se abordarán en M2. No hay pruebas de WebSocket o interfaz en este incremento.
- No se ha inicializado Git ni creado ningún commit.

### Verificación

- Python 3.14.4, Pydantic 2.14.0, PyYAML 6.0.3, jsonschema 4.26.0 y pytest 9.1.1.
- `.venv/bin/python -m pytest -q --tb=short`: 27 pruebas superadas.
- Corregida durante las pruebas la ruta de resolución de la raíz del proyecto.
