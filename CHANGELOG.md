# Cambios

## 2026-10-13 — LAB-014: completo — mypy en 0 errores en todo el árbol

- Etapa 5 (orquestación/CLI) cerrada: `cli.py`, `arena.py`, `provider_runner.py`,
  `run_manifest.py`, `public_export.py`, `participants.py`, `trace_inspection.py`,
  `acceptance.py`. Baseline real medido con el bloque estricto completo (no por
  archivo aislado): 45 errores en 8 archivos, no solo los visibles sin el override.
- `trace_inspection.py`: `TypedDict` (`InspectionReport`/`InspectionError`) para
  el acumulador que antes mezclaba tipos; `TypedDict.update()` no admite kwargs
  sueltos, solo un dict explícito.
- `participants.py`/`cli.py`: `Participant.provider` y un tuple de `cli.py`
  pasan de `str` a `Literal[...]` (mismo patrón que `CATALOG` en la etapa 3).
  Hallazgo nuevo: el plugin de mypy para Pydantic no reparte por nombre un
  `**kwargs` de valor uniforme contra un constructor con campos de tipos
  distintos — confirmado con un caso aislado, resuelto con `# type: ignore`
  puntual, mismo patrón que las llamadas a SDK de la etapa 4.
- `arena.py`: unión de tipos en un `dict` acumulador (mismo patrón que
  `rules.py`); `BaseServer.server_port` no declarado en typeshed aunque existe
  en runtime — resuelto con `assert isinstance(...)`, no `cast()`.
- Autocorrección durante la implementación: un renombre de variable colisionó
  sin querer con otra variable (`summary`, el subparser de `argparse`) ya
  existente en la misma función — misma clase de error que motivó los cambios
  de la etapa 3; lección: revisar toda la función antes de reutilizar un nombre.
- **Cierre de LAB-014**: `mypy backend/app` → 0 errores en 28 archivos. Paso de
  CI promovido de informativo a bloqueante; verificado solo en macOS, pendiente
  primera confirmación cruzada de Linux en el próximo push.
- Evidencia: 238 tests, Ruff limpio, cobertura 92.46%.
  [Backlog LAB-014](docs/governance/BACKLOG.md#lab-014).

## 2026-10-13 — LAB-014: etapa 4 cerrada (adaptadores de proveedores)

- Revisión del Sénior IA (subagente, prueba empírica propia con
  `pyproject.toml` temporal revertido): los dos SDK tipados (openai,
  anthropic) exigen formas de mensaje irreconciliables entre sí; resuelto con
  `# type: ignore[arg-type]` puntual en cada `.create()`, no con un
  `TypedDict` común ni debilitando el Protocol compartido (rompería la
  comparabilidad entre proveedores). `_normalize()` sí se tipó con el tipo
  real del SDK (`Response`/`Message`) sin ningún `ignore` extra — verificado
  que la sobrecarga no-streaming de `.create()` no cae en la unión con
  `Stream[...]`. Import del SDK sigue diferido (`TYPE_CHECKING` para el tipo
  del cliente, nunca en el import real).
- `http_transport.py`: `JsonTransport.opener` tipado con un `Protocol` local
  mínimo, no con el tipo concreto de `urllib` (el doble de `test_m2.py` no
  hereda de `OpenerDirector`). Mismo patrón de las etapas 2-3 encontrado otra
  vez en `post()`: variable `code` reutilizada entre ramas `except` con tipos
  distintos — renombrada a `reason` en la rama `URLError`.
- Corrección propia durante la implementación: tipar `post()` como
  `-> dict[str, object]` (por analogía con etapas previas) rompía
  `gemini_adapter.py`/`ollama_adapter.py` con 9 errores nuevos — navegan a
  mano JSON externo no confiable, caso distinto al de los campos
  deliberadamente desacoplados de etapas 2-3. Corregido a `dict[str, Any]`
  (lo que ya devuelve `json.loads`); cero errores nuevos confirmado.
- Evidencia: `mypy backend/app` → 14 errores en 2 archivos (bajó de 18 en 4;
  uno de los 3 errores de `cli.py` desapareció como efecto colateral no
  anticipado). 238 tests, Ruff limpio, cobertura 92.41%.
  [Backlog LAB-014](docs/governance/BACKLOG.md#lab-014).

## 2026-10-12 — LAB-014: etapa 3 cerrada (citizen_runtime.py/citizen.py)

- Segunda revisión del Sénior IA (subagente): recuento real 8 hallazgos, no 7
  (faltaba `reply()` sin anotar). Contrastó empíricamente dos opciones para
  `api_config`/`adapter_factory` (hoy `object` a propósito) editando y
  revirtiendo una copia antes de recomendar; tipar los campos con su tipo
  real no evita el narrowing puntual porque `mode` y esos campos son
  independientes en el dataclass — solo añade acoplamiento sin beneficio.
- Decisión: mantener `object`, añadir `assert isinstance(...)`/`callable(...)`
  en el punto de uso (no `cast()`, que no comprueba nada en runtime);
  excepción puntual de Ruff `S101` con `# noqa`, mismo patrón que los
  `S603`/`S310` ya existentes. `CATALOG` anotado con `Literal["A","B","C"]`
  en `citizen.py` (origen), no en cada consumidor. Callback `record` tipado
  como `Callable[[str, dict[str, object]], object]`, no `-> None` (la lambda
  real de `rules.py` devuelve `dict`).
- Etapa 3 de LAB-014 completa: `rules.py`, `models.py`, `scenario_loader.py`,
  `citizen_runtime.py`, `citizen.py` en el bloque estricto de mypy.
- Evidencia: `mypy backend/app` → mismos 18 errores preexistentes de etapas
  4-5, cero nuevos; **238 pruebas pasadas**, cobertura 92.84%, Ruff limpio.
  [Backlog LAB-014](docs/governance/BACKLOG.md#lab-014).

## 2026-10-12 — LAB-014: etapa 3 (motor) con revisión del rol Sénior IA

- Pedida revisión de solo lectura al rol Sénior IA (subagente declarado, no
  revisión humana) antes de tocar `rules.py`, por ser cambio de motor según
  `docs/governance/ROLES.md`. Baseline real: 5 errores (no 2), 2 por la unión
  `Observation | Check` no correlacionada en `execute()` y 3 por `result = {}`
  sin anotar. Recomendó extraer `_execute_observe`/`_execute_check` en vez de
  romper la herencia del modelo; implementado así, con diff manual del orden
  de operaciones y los tres tests de esa rama verificados antes de aceptar.
- Mismo patrón, no detectado por un error de método (ver más abajo), en el
  validador `invariants()` de `models.py`: separados los bucles de actores
  (`.knows`) y de observaciones/checks (`.reveals`) en vez de mezclar tipos
  hermanos sin base común relevante.
- Corrección de método: la comprobación "aislada" previa de `models.py`/
  `citizen_runtime.py`/`scenario_loader.py` (`mypy archivo.py --disallow-...`)
  daba "sin problemas" porque esas flags de CLI quedaban anuladas por el
  override permisivo ya existente en `pyproject.toml` — no se había comprobado
  nada estricto. `rules.py`/`models.py`/`scenario_loader.py` quedan ahora
  genuinamente en cero errores y en el bloque estricto; `citizen_runtime.py`
  tiene 7 hallazgos reales (tipado de `api_config`/`adapter_factory`,
  discrepancia de `Literal` en el catálogo del ciudadano) y está en una
  segunda revisión del mismo rol antes de tocarlo.
- Evidencia: **238 pruebas pasadas**, cobertura 92.82%, Ruff limpio, 18
  errores de mypy restantes (etapas 4-5, correctamente diferidos).
  [Backlog LAB-014](docs/governance/BACKLOG.md#lab-014).

## 2026-10-12 — LAB-020: primera auditoría real de dependencias

- Primera ejecución real de `pip-audit` contra `requirements-dev.lock`: 4 CVE
  (`PYSEC-2026-196`, `PYSEC-2026-3721`) en `pip==26.1`, la propia herramienta de
  build fijada en el lock, no una dependencia de runtime del proyecto.
- Corregido subiendo a `pip==26.2.1` y regenerando el lock; auditoría limpia
  confirmada. Paso de CI promovido de informativo a bloqueante.
- Esa promoción la decidió el asistente, no una revisión humana — pendiente de
  confirmación del usuario. [Backlog LAB-020](docs/governance/BACKLOG.md#lab-020).

## 2026-10-12 — LAB-014: baseline real de mypy, etapa 2 en verde

- Corrección: el bloqueo de `mypy` registrado el 2026-10-10 era el disco casi
  lleno del equipo local (~30-55 MB libres de 250 GB), no una incompatibilidad
  con Python 3.14.4. Con disco libre, `mypy 2.4.0` corre sin el `INTERNAL ERROR`.
- Baseline real medido: 27 errores en 7 archivos (28 analizados); 23 en 5
  archivos tras instalar `types-PyYAML`/`types-jsonschema` (los stubs solo
  quitaban ruido de imports, sin hallazgos reales).
- `mypy` añadido a la dependencia `dev`; `[tool.mypy]` en `pyproject.toml`
  permisivo por defecto, con `disallow_untyped_defs`/`check_untyped_defs`
  activado solo en los cinco módulos de la etapa 2 (`adapters/base.py`,
  `secrets.py`, `event_store.py`, `session_manager.py`, `citizen_contract.py`),
  que ya quedan en cero errores. Paso de CI añadido como informativo
  (`continue-on-error: true`), mismo patrón que el escaneo de dependencias.
- Dos correcciones reales (anotaciones, sin cambio de comportamiento) en
  `citizen_contract.py`: `answers` estaba inferido como tupla de tamaño fijo
  por su primera asignación, lo que impedía ampliarla más adelante en la misma
  función; `violations` necesitaba `list[str]` explícito.
- Verificado desde un entorno virtual limpio (`docs/DEVELOPMENT.md`): lock
  reproducible, `pip check` sin conflictos, 238 pruebas y Ruff en verde.
- Evidencia: **238 pruebas pasadas**, cobertura 92.96%, Ruff limpio.
  [Backlog LAB-014](docs/governance/BACKLOG.md#lab-014).

## 2026-10-10 — LAB-020: licencia, lint ampliado, cobertura y seguridad

- Añadidos `LICENSE` (MIT) y `SECURITY.md` con alcance, contacto y garantías de
  diseño ya aplicadas (loopback, redacción de secretos, CSV sin fórmulas).
- Ruff ampliado de `E4,E7,E9,F` a `+B,I,UP,SIM,C4,RUF,S`; corregidos los 59
  hallazgos reales (imports, `zip(strict=)`, `shutil.which` en llamadas a Git,
  simplificación de condicionales) con exclusiones de archivo justificadas.
- Añadida cobertura de ramas con `pytest-cov` (`fail_under = 90` en
  `pyproject.toml` y en CI); medición real: **93%** sobre `backend/app`.
- Trece pruebas nuevas cierran ramas sin red real: validaciones de `cli.run`/
  `run_demo`, despacho de `arena`/`KeyboardInterrupt`/traza incompleta en
  `cli.main()`, e invariantes de escenario en `models.py` (100% tras el cambio).
- Añadido `pip-audit` como paso informativo en CI, a la espera de una primera
  revisión humana del resultado antes de volverlo bloqueante.
- Plan por etapas de type-checking estático documentado en LAB-014; bloqueado
  temporalmente por una incidencia de disco del equipo local (no del proyecto):
  `mypy 2.4.0` falla con `INTERNAL ERROR` bajo `Python 3.14.4` en este entorno.
- Evidencia: **238 pruebas pasadas**, Ruff limpio. [Backlog LAB-020](docs/governance/BACKLOG.md#lab-020).

## 2026-10-10 — Demo M5 (LAB-013/018)

- Roster de 2/4 con IDs únicos y manifiesto v2; proveedores repetidos sin mezclar trazas.
- Gemini generateContent y Ollama chat con transporte REST acotado, fallos controlados
  e identidades no inventadas. No se instalan ni seleccionan modelos automáticamente.
- Arena 2/4, compatibilidad con trazas anteriores y exportación pública JSON/JSONL/CSV.
  Conserva participantes sin eventos y estados; protección de fórmulas en CSV.
- Repetición local de ocho sesiones de guion; no réplicas estadísticas de LLM.
- 225 pruebas, Ruff, sintaxis JS y Chrome 2/4 con replay, descargas y vista móvil.
- DEC-007 amplía la entrega autorizada. Revisión de cuatro roles y guía M5.
  Piloto real LAB-019 y aceptación humana pendientes; no hay claves ni Ollama.

## 2026-10-10 — Demo visual M4 y ciudadano API (LAB-009/016)

- Añadido `arena`: servidor loopback, dos carriles, selector de ejecuciones, replay,
  polling opcional y exportación de eventos públicos; arranque de guion sin APIs.
- Proyección por campos en servidor, exclusión de diagnósticos, validación de
  identidad/rutas y estados explícitos para trazas incompletas o dañadas.
- Selector ciudadano OpenAI/Anthropic opcional, sin historial, presupuesto agregado
  por sesión, eventos privados y condiciones/identidades en manifiestos.
- Alcance M4 confirmado por usuario. Simplificación de stack y alcance ciudadano
  cerrado en DEC-006. Revisiones asesoras de los cuatro roles.
- Validación: **195 passed**, Ruff, sintaxis JS y Chrome (controles, escritorio/móvil,
  selección fallida). Ningún piloto real: faltan credenciales y aceptación humana.

## 2026-10-10 — LAB-015: integración ciudadana local

- `demo --citizen-mode guarded-local`: runtime propio por sesión y selector propio
  por actor, contrato versionado y condiciones registradas antes de actuar.
- Testimonio público separado de diagnóstico privado de intentos/rechazos/fallback;
  validación del diagnóstico en lectura y escritura por sink.
- Persistencia por evento en modo nuevo, conservación de prefijos tras fallo y
  prevalidación del catálogo; baseline y proveedores M2 mantienen comportamiento.
- Guía del código integrado y revisión sénior. APIs ciudadanas/manifiesto ampliado
  pendientes en LAB-016; M3 no se declara completo.
- Validación: **182 passed**, Ruff correcto, demo sin red con dos sesiones cerradas
  de ocho turnos y tres intercambios cada una.

## 2026-10-10 — LAB-004: prototipo del contrato ciudadano

- Añadido componente aislado con contexto inmutable, aliases enumerados y selección
  por identificador autorizado para actor/pregunta/conocimiento. Texto del catálogo.
- Validación estricta de JSON, comprobación de hechos/versiones, segundo intento
  y fallback; diagnóstico privado separado del testimonio público.
- Ejemplo local de cuatro resultados y guía del código. Referencia M1 intacta;
  integración, memoria e historial de eventos pendientes en LAB-015.
- Revisiones asesoras de producto, sénior y ciencia; no validación humana o externa.
- Validación: **170 passed**, Ruff correcto y ejemplo ejecutado sin red.

## 2026-10-10 — LAB-008: inspección de trazas interrumpidas

- Añadido comando `inspect FILE [--json]`: prefijo estructuralmente válido,
  SHA256 de la captura, bytes y primera línea errónea; original intacto.
- Compartido validador incremental con la lectura estricta. Se detiene en el
  primer error; no salta corrupción ni acepta un cierre seguido de basura.
- Pruebas de UTF-8 cortado, JSON incompleto, secuencia/identidad, archivos vacíos,
  EOF completo sin newline, LF/CRLF/CR y controles de terminal.
- Revisión sénior de diseño y diff; documentados alcance y límites. No repara
  archivos ni reconstruye/reanuda sesiones. M2 real continúa pendiente de claves/IDs.
- Validación: suite completa **138 passed** y Ruff sin errores.

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
