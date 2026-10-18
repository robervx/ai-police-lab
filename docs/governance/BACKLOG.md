# Backlog de AI POLICE LAB

Actualizado: 2026-10-10. El orden protege la prioridad **demo funcional**.
«Responsable» identifica el rol que prepara/revisa la tarea; no acredita asignación
a una persona ni ejecución permanente. La escritura final la integra el coordinador.

Estados: pendiente → en curso → implementado → validado localmente → validado
externamente, cuando aplique → aceptado. «Bloqueado» exige una dependencia concreta.
Registrar evidencia al cambiar de estado. El estado y la evidencia de cada tarea
indican qué está implementado y qué sigue pendiente.

## LAB-001

**Piloto real M2** · prioridad 1 · PM + sénior IA · pendiente · dependencia:
claves/IDs locales y acceso a ambos proveedores.

Comprobación 2026-10-10: no existe `.env` ni están presentes las cuatro variables
requeridas en el entorno. Suite: 72 pruebas pasadas; `--dry-run` correcto con IDs
de ejemplo y cero llamadas. Esto no valida credenciales ni servicios reales.

Aceptación: seleccionar IDs concretos, registrar todas las sesiones del piloto,
demostrar ≥3 intercambios por modelo en el recorrido mínimo, revisar JSONL con
inicio/cierre y ausencia de filtraciones del motor, anotar qué se observó y qué no.
Conservar cierres tempranos y fallos; no repetir hasta «conseguir éxito» ocultando
intentos. Un humano debe registrar su revisión para cerrar la aceptación del MVP.
No convierte el piloto en ranking ni en estudio científico.

## LAB-002

**Resumen de aceptación de la demo** · prioridad 1 · producto + sénior IA · validado localmente (2026-10-10).

Implementado en `backend/app/acceptance.py`, CLI `summary` y resúmenes automáticos
en `demo`, `run` y `replay`. Revisión humana pendiente salvo declaración externa
validada y vinculada al SHA256 de la traza; no autentica autoría ni acepta el MVP.
Evidencia: suite completa **95 passed**, incluidos cierres tempranos, fallos,
interrupción, trazas corruptas y revisión de otra traza.
[Revisión técnica y límites](reviews/2026-10-10-lab002.md).

Aceptación: mostrar por sesión ejecución terminada, número de intercambios,
integridad de la traza y revisión humana pendiente/realizada. Separar esos campos
del código de salida y de cualquier juicio de calidad. Mantener cierre temprano
permitido y evitar etiquetas de «éxito policial».

## LAB-003

**Manifiesto y comprobación previa de condiciones** · prioridad 1 · sénior IA · validado localmente (2026-10-10).

Implementado en `backend/app/run_manifest.py`, `run_comparison()` y `run --dry-run`.
Manifiesto inicial exclusivo antes de llamadas; informe final vinculado a su hash,
con modelos observados y sesiones no iniciadas/incompletas. Diferencias de límites
rechazadas antes de crear archivos o ejecutar participantes. Protocolo `demo-m2-v1`
en `docs/RUN_PROTOCOL.md`. Suite **112 passed** y dry-run CLI sin red;
[revisión sénior](reviews/2026-10-10-lab003.md). No acredita neutralidad ni restauración.

Aceptación: registrar versión de protocolo/código/entorno, hashes de escenario y
prompt, modelos solicitados/resueltos, ciudadano, límites, orden y política de
fallos. Si no hay Git, hash del conjunto de fuentes, sin inventar commit. Comprobar
que `run_comparison()` detecta configuraciones distintas o las declara como
condiciones distintas antes de ejecutar. Declarar límites nominales, no igual cómputo.

## LAB-004

**Contrato del ciudadano M3** · prioridad 2 · producto + sénior IA · en curso; contrato y prototipo validados localmente (2026-10-10).

[Contrato](../CITIZEN_CONTRACT.md), ejemplo local y 32 casos nuevos; suite completa
**170 passed** y Ruff correcto. Producto, sénior y ciencia revisaron alcance/diseño.
[Revisión](reviews/2026-10-10-lab004.md). LAB-015 añade aislamiento por actor/sesión y registro integrado de violaciones.
La política local y API es sin memoria conversacional; LAB-016 la declara y valida
con contextos independientes. No se añade historial ciudadano a esta demo.
No se cierra M3.

Aceptación: conservar el ciudadano determinista como referencia; especificar
equivalencia de preguntas, conocimiento permitido, contradicciones, regeneración,
fallback y memoria por sesión; pruebas adversariales y registro de violaciones.
Dirección científica revisa qué nuevo constructo permite observar, sin certificar realismo humano.

## LAB-005

**Procedencia de etiquetas y estados sociales** · prioridad 2 · sénior IA + ciencia · pendiente.

Aceptación: decidir y documentar si tensión/cooperación son solo una mecánica de
juego o una variable futura; si se conectan, registrar etiquetas, autor/método,
versión, revisión y transición; mismo procedimiento para ambos participantes.
Mientras tanto, indicar que `run` no activa esas reglas y no mide empatía/desescalada.

## LAB-006

**Repeticiones y orden de ejecución** · prioridad 2 para estudio; no bloquea demo · sénior IA + ciencia · pendiente.

Aceptación: definir bloques de réplicas y un orden alternado/aleatorio registrado;
separar semilla local de generación de proveedor; conservar todos los intentos y
motivos de repetición. No presentar turnos como muestras independientes. El número
de réplicas se justifica para la pregunta elegida antes de un estudio confirmatorio.

## LAB-007

Actualización 2026-10-18 para sincronizar GitHub: 238 pruebas locales pasadas,
cobertura 92,46 %, Ruff correcto y mypy sin errores en 28 archivos. Incluye la
entrega M3–M5/LAB-014, documentación pendiente y recursos de marca; capturas
sueltas conservadas localmente. CI de esta entrega pendiente de comprobación.

**Versionado y entorno reproducible** · prioridad 1 · PM + sénior IA · validado localmente y checks remotos superados (2026-10-10).

Aceptación: disponer de fuente versionada y captura reproducible de dependencias
de una ejecución; excluir secretos/trazas privadas; verificar restauración del
entorno. Git inicializado localmente el 2026-10-10. El usuario autorizó además subir
el proyecto a GitHub en esta sesión; no publicar secretos ni trazas privadas.

Evidencia LAB-007: `.python-version`, `requirements-dev.lock` (36 paquetes),
`docs/DEVELOPMENT.md`, `.github/workflows/checks.yml`; instalación sin resolución
extra del proyecto, `pip check`, Ruff y 112 pruebas en copia limpia macOS Intel.
Publicado en [GitHub público](https://github.com/robervx/ai-police-lab);
[primera CI](https://github.com/robervx/ai-police-lab/actions/runs/38002348512) superada en Linux y macOS,
con 112 pruebas por plataforma, Ruff y pip check correctos. La restauración
local no acredita reproducción binaria ni todos los Python >=3.11.
[Revisión y evidencia](reviews/2026-10-10-lab007.md).

## LAB-008

**Trazas interrumpidas y replay** · prioridad 2 · sénior IA · validado localmente (2026-10-10).

Añadido `inspect FILE [--json]`, con captura/hash, prefijo estructuralmente válido,
primera incidencia y offsets en bytes. No modifica originales ni cambia `summary`
o la lectura estricta de `replay`. [Alcance](../TRACE_INSPECTION.md).
La presentación visual de incompletitud sigue siendo un requisito de M4.
Evidencia: **138 pruebas pasadas** y Ruff correcto. [Revisión sénior](reviews/2026-10-10-lab008.md).

Aceptación: especificar comportamiento ante última línea parcial/fallo de disco,
preservar el original y distinguir replay cronológico, reconstrucción y reanudación.
Antes de M4, el visor debe mostrar incompletitud de forma explícita. No prometer
atomicidad de turno por disponer de `fsync` en eventos individuales.

## LAB-009

**Demo visual de dos carriles M4** · prioridad 3 · producto + sénior IA · validado localmente (2026-10-10).

`arena` sirve interfaz local con dos carriles, replay y actualización periódica.
Proyección pública por campos, identidad de ejecución y estados de incompletitud.
Suite **195 passed**, Ruff y navegador Chrome correctos; [guía](../M4_DEMO.md),
[revisión de roles](reviews/2026-10-10-m4.md). Aceptación humana y piloto real pendientes.
Simplificación HTML/JS/HTTP registrada en DEC-006; sin React/WebSocket.

Dependencias: recorrido headless verificable y contrato público de eventos.
Aceptación: mostrar mensajes, acciones, resultados y cierre sin exponer verdad
privada; replay fiel; identificación visible de simulación y límites de la demo.
Mantener cuatro carriles para M5.

## LAB-010

**Elegir vía después de la demo** · prioridad 3 · producto + usuario · pendiente.

Aceptación: recoger revisión real de la demo y decidir investigación, formación o
continuación exploratoria. Registrar necesidades observadas, no beneficios supuestos.
Si se elige formación, definir objetivos pedagógicos y evaluación específica; si
se elige investigación, concretar pregunta y protocolo antes de conclusiones.

## LAB-011

**Rúbrica y protocolo de estudio** · condicionado a LAB-010 · ciencia + sénior IA · pendiente.

Aceptación: hipótesis, variable primaria, unidades, muestra/precisión, revisión
humana, exclusiones, análisis y limitaciones fijados antes de la recogida confirmatoria.
Bibliografía revisada más allá de resúmenes para las decisiones que dependan de ella.
Si se preregistra, conservar identificador, fecha y versión del registro real.
El borrador local actual no cumple ese requisito.

## LAB-012

**Comprobar disponibilidad de perfiles de equipo en Codex** · prioridad 1 · PM · perfiles instalados y TOML validado; cuatro nombres disponibles en esta sesión, invocación sénior comprobada.

Pasos separados: instalar los cuatro TOML; comprobar que el cliente los descubre;
invocar un perfil y verificar la ficha utilizada.
Instalación realizada el 2026-10-09 en `.codex/agents/`, con autorización para la
ruta protegida. No se han cambiado ajustes globales ni fijado modelos diferentes.
Aceptación: el cliente reconoce los cuatro nombres de `.codex/agents/` y una
revisión invocada cita la ficha correcta. Validar TOML no demuestra descubrimiento
en la interfaz. Si no se reconocen, usar las fichas vía `AGENTS.md` y registrar esa modalidad.

Comprobación 2026-10-10 (LAB-012): los cuatro nombres figuran en los roles
disponibles de la herramienta de delegación. Se invocó `senior_ai_developer`
como subagente `revision_reanudacion`, que confirmó la lectura de
`docs/governance/roles/senior_ai_developer.md` y entregó hallazgos de M2.
Criterio operativo de disponibilidad e invocación comprobado en esta sesión;
Además, en LAB-004 se invocaron `product_manager` (`citizen_product`) y
`scientific_director` (`citizen_scope_science`). En la entrega M4 se invocó además `project_manager` (`m4_pm`), con lectura de su
ficha y revisión entregada. Los cuatro perfiles están comprobados operativamente
en estas sesiones; otra interfaz del cliente no se ha verificado.

## LAB-013

**Identificador único de participante en exportaciones M5** · prioridad 3 · sénior IA · validado localmente (2026-10-10).

Resuelto SEN-003-05: roster de 2/4 con IDs únicos, propagados a sesiones,
manifiestos y proyección. Pruebas de proveedor repetido, intercambio de trazas,
identidad en archivos vacíos/dañados y conservación de participantes sin iniciar.
[test_m5.py](../../backend/tests/test_m5.py), suite acumulada 225 passed.
Los manifiestos antiguos conservan compatibilidad de lectura. No valida identidad
auténtica de servicios externos. [Revisión M5](reviews/2026-10-10-m5.md).

## LAB-014

**Análisis estático de tipos gradual** · prioridad 2 · sénior IA · **completo,
validado localmente (2026-10-13)**: `mypy backend/app` da 0 errores en los 28
archivos fuente; las seis etapas del plan están cerradas. Paso de CI promovido
de informativo a bloqueante (primera confirmación cruzada de SO pendiente del
próximo push).

Corrección (2026-10-12): el `INTERNAL ERROR` de `mypy 2.4.0` bajo `Python 3.14.4`
registrado el 2026-10-10 era causado por el disco casi lleno del equipo local
(`~30-55 MB` libres de 250 GB), no por una incompatibilidad mypy/3.14.4. Con disco
libre, `mypy 2.4.0` corre normalmente bajo 3.14.4; no hizo falta el entorno de
herramientas aparte previsto como plan B.

Baseline real medido (2026-10-12, `mypy backend/app`, 28 archivos fuente
analizados): **27 errores en 7 archivos** antes de instalar `types-PyYAML` y
`types-jsonschema` (23 tras instalarlos, en 5 archivos — ambos stubs solo
eliminaban ruido de `import-untyped`, cero hallazgos reales).

Ruff y pytest automatizados cubren lint básico y comportamiento. `mypy` añadido
como dependencia `dev` y como paso informativo en CI (`continue-on-error: true`,
[.github/workflows/checks.yml](../../.github/workflows/checks.yml)); `[tool.mypy]`
en `pyproject.toml` es permisivo por defecto en todo `backend.app.*`, con un
`[[tool.mypy.overrides]]` que activa `disallow_untyped_defs`/`check_untyped_defs`
solo en los módulos de la etapa 2. No declarar cobertura mypy total ni bloquear
el piloto por una conversión masiva de anotaciones.

Plan por etapas, apoyado en lo ya tipado por convención (dataclasses, Pydantic
`strict=True`, `Protocol` en adaptadores):

1. ~~**Entorno de la herramienta.**~~ Resuelto: no hacía falta un entorno de
   herramientas aparte; el bloqueo era el disco, no la versión de Python.
2. ~~**Núcleo ya tipado de forma estricta en runtime:**~~ **hecho y en verde.**
   `adapters/base.py`, `secrets.py`, `event_store.py`, `session_manager.py`,
   `citizen_contract.py` — cero errores con `disallow_untyped_defs=true`. Arreglos
   aplicados, todos anotaciones o tipos más precisos sin cambiar comportamiento
   (confirmado por los 238 tests y la cobertura sin variación): añadidas
   anotaciones de parámetro/retorno que faltaban (`Self` en los `model_validator`
   y en `__enter__`, `object` en los puntos genuinamente dinámicos como
   `Redactor.__call__` y `SessionManager`'s `citizen_config`/`citizen_factory`,
   `Iterator[dict]` en `iter_events`); y dos correcciones reales en
   `citizen_contract.py`: `answers` estaba inferido como tupla de longitud fija
   (`tuple[Answer]`) por su primera asignación, lo que impedía ampliarla a dos
   elementos más adelante en la misma función — anotado `tuple[Answer, ...]`;
   `violations` necesitaba `list[str]` explícito (sin esto `mypy` no podía
   verificar que `repair` ya no es `None` en el punto de cada `append`).
3. **Motor determinista:** `rules.py`, `models.py` y `scenario_loader.py` ya
   en cero errores y en el bloque estricto; `citizen_runtime.py` pendiente.

   Corrección de método (2026-10-12): la primera comprobación «aislada» de
   `models.py`/`citizen_runtime.py`/`scenario_loader.py` (`mypy archivo.py
   --disallow-untyped-defs --check-untyped-defs`) dio «sin problemas» de forma
   engañosa — esas flags de CLI quedaban anuladas por el override permisivo
   `backend.app.*` que ya existía en `pyproject.toml` (los overrides de
   configuración tienen prioridad sobre las flags de línea de comandos), así
   que en realidad no se comprobó nada estricto todavía. No declarar «cero
   errores» a partir de una comprobación aislada sin confirmar antes qué
   override de `pyproject.toml` aplica de verdad.

   `rules.py`: patrón `entry = (observations[...] if OBSERVE else
   checks[...])`, unión `Observation | Check` no correlacionada por `mypy`
   con la rama de `kind` — no era un bug (cortocircuito de `or` protegía el
   acceso en runtime). Revisado por el rol Sénior IA (subagente, 2026-10-12,
   [hallazgos íntegros citados abajo]); recomendó extraer `_execute_observe`/
   `_execute_check` (tipadas por `Observation`/`Check`) en vez de romper la
   herencia del modelo o de un enum discriminante, por menor radio de cambio
   sobre `models.py`/el YAML del escenario. Implementado exactamente así, más
   `result: dict[str, object]` en `execute()` (el baseline real eran 5
   errores, no 2: los otros 3 eran `dict-item` por `result = {}` sin anotar).
   Diff manual del orden de operaciones contra el bloque original + los tres
   tests que cubren la rama (`test_no_fake_sound_meter_result`,
   `test_observation_and_witness`, `test_turn_limit_not_success`) en verde
   antes de aceptar el cambio, como exigió el criterio de cierre del sénior.

   `models.py`: el mismo patrón, no detectado por la comprobación aislada
   defectuosa, apareció en el validador `invariants()` — itera
   `[*actors, *observations, *checks]` y accede a `.knows`/`.reveals` según
   `isinstance`; como `Actor` no comparte base relevante con `Observation`/
   `Check`, `mypy` infiere el tipo de la lista como el ancestro común `Model`
   (sin `.reveals`). Mismo criterio que en `rules.py`: separado en dos bucles
   (actores con `.knows`; observaciones+checks con `.reveals`, donde `Check`
   sí es subtipo válido de `Observation`) en vez de tocar la jerarquía de
   modelos — generalización directa del mismo hallazgo (H3) que motivó la
   recomendación del sénior en `rules.py`, sin pedir una pasada nueva porque
   el análisis ya cubría explícitamente esta línea.

   `citizen_runtime.py`/`citizen.py`: **hecho y en verde** (cerrado 2026-10-12,
   segunda revisión del Sénior IA, subagente). El recuento real era 8
   hallazgos, no 7 (faltaba `reply()` sin anotar en el recuento inicial). La
   revisión contrastó empíricamente (editando y revirtiendo una copia, no el
   árbol real) las dos opciones de diseño para `api_config`/`adapter_factory`:
   tipar los campos con su tipo real (`ProviderConfig`/una factoría) no evita
   el narrowing puntual — `mode` y esos campos son independientes dentro del
   dataclass, así que `mypy` no puede inferir `mode=="guarded-api" ⇒
   api_config is not None` entre campos distintos — solo añade acoplamiento
   sin evitar ese coste. Decisión: mantener `object` (desacoplo deliberado de
   un proveedor concreto) y añadir `assert isinstance(...)`/`callable(...)`
   en el punto de uso (`metadata()`, `reply()`), no `cast()` — el `assert`
   documenta y falla con mensaje claro si un futuro productor sin tipar
   (etapa 4/5) pasa algo incorrecto; `cast()` no comprueba nada en runtime.
   Esos dos `assert` necesitaron una excepción puntual de Ruff `S101` (no son
   una comprobación de seguridad, son *narrowing* ya validado en
   `__post_init__`), con `# noqa` igual que los `S603`/`S310` ya existentes
   en `run_manifest.py`/`http_transport.py`. `CATALOG` anotado con
   `Literal["A","B","C"]` en `citizen.py` (origen), no parcheado en cada
   consumidor (`citizen_runtime.validate_scenario`, `citizen_contract` también
   lo recorre). El callback `record` de `reply()` tipado como
   `Callable[[str, dict[str, object]], object] | None`, no `-> None`: la
   lambda real pasada desde `rules.py` (`RuleEngine._record`) devuelve `dict`,
   y `rules.py` ya está en el bloque estricto. Criterio de cierre confirmado:
   `mypy backend/app` → mismos 18 errores preexistentes de etapas 4-5, cero
   nuevos; 238 tests y Ruff en verde; revisión manual sin reordenar ninguna
   rama (solo anotaciones + 2 `assert`).

   Backlog nuevo, no bloqueante: test que instancie `CitizenRuntime` con un
   `api_config`/`adapter_factory` de tipo incorrecto y compruebe que el
   `assert` falla con un mensaje claro (hoy no hay ningún test que construya
   `CitizenRuntime` de forma aislada con un tipo erróneo). Al llegar a la
   etapa 5 (`provider_runner.py`/`cli.py`), revisar si entonces sí conviene
   tipar `citizen_config`/`citizen_factory` de extremo a extremo — hoy no
   hace falta porque fluyen como `Any` implícito sin romper nada.

   Valorar `TypedDict` para las formas de payload más estables antes de
   forzar strict en el resto (etapas 4-5).
4. **Adaptadores de proveedores:** **hecho y en verde** (cerrado 2026-10-12/13,
   revisión del Sénior IA, subagente con prueba empírica propia —
   `pyproject.toml` temporal, revertido, confirmado por diff byte a byte).
   `openai_adapter.py`/`anthropic_adapter.py`: el Protocol compartido
   (`PoliceModelAdapter.generate`) es deliberadamente genérico
   (`messages: list[dict]`), pero cada SDK exige una forma irreconciliable
   con la del otro (`Iterable[MessageParam]` de Anthropic vs. la unión de 28+
   TypedDicts de OpenAI) — ningún tipo común sin `Any` satisface ambos sin
   romper el Protocol compartido ni la comparabilidad entre proveedores.
   Resuelto con `# type: ignore[arg-type]` puntual en cada llamada a
   `.create()`, documentado inline (caso (c), ya anticipado). `_normalize()`
   sí se pudo tipar con el tipo real del SDK (`Response`/`Message`) sin
   ningún `ignore` adicional: verificado empíricamente que `.create()` no
   streaming resuelve por sobrecarga al tipo concreto, no a la unión con
   `Stream[...]`.

   Import diferido del SDK preservado (el paquete sigue siendo opcional):
   los tipos de cliente (`OpenAI`/`Anthropic`) se referencian solo bajo
   `if TYPE_CHECKING:`, nunca en un import de módulo real.

   `http_transport.py`: `JsonTransport.opener` tipado con un `Protocol` local
   mínimo (`_Opener`/`_Response`, solo `open()`/`close()`/`read()`), no con el
   tipo concreto de `urllib`, para no mentir sobre lo que el doble de
   `test_m2.py` implementa (no hereda de `OpenerDirector`). Mismo patrón que
   en `rules.py`/`models.py` (etapa 3) encontrado de nuevo en `post()`: la
   variable `code` se reutilizaba entre dos ramas `except` hermanas con tipos
   distintos (`int` en `HTTPError`, `str` en `URLError`) — renombrada a
   `reason` en la rama `URLError`, sin tocar la lógica.

   Corrección durante la implementación (no prevista por la revisión): tipar
   `JsonTransport.post()` como `-> dict[str, object]` (por analogía con
   `session_manager.py`/`citizen_runtime.py`) rompía `gemini_adapter.py`/
   `ollama_adapter.py` con 9 errores nuevos — esos dos adaptadores navegan a
   mano la respuesta JSON externa no confiable (`data.get(...)`, indexado,
   `len()`) validándola campo a campo con `isinstance`/`try-except`, un caso
   distinto al de los campos deliberadamente desacoplados de etapa 2-3.
   Corregido a `-> dict[str, Any]` (lo que ya devuelve `json.loads` para JSON
   arbitrario): cero errores nuevos, confirmado. Lección: una recomendación
   de tipado por analogía con un caso ya cerrado necesita su propia
   verificación empírica contra el consumidor real, no basta con el patrón.

   `NoRedirect.redirect_request()`: anotado `*args: object, **kwargs: object`
   en vez de replicar la firma exacta de `HTTPRedirectHandler` de typeshed,
   porque `test_m2.py` lo invoca con posicionales `None` que esa firma no
   admitiría — mantiene el test representativo de la anotación.

   Criterio de cierre confirmado: `mypy backend/app` → 14 errores en 2
   archivos (bajó de 18 en 4; como efecto colateral no anticipado por la
   revisión, uno de los 3 errores de `cli.py` también desapareció al quedar
   los adaptadores con firmas completas); 238 tests, Ruff y cobertura
   (92.41%, por encima del umbral) en verde.
5. **Orquestación y CLI:** **hecho y en verde** (cerrado 2026-10-13):
   `cli.py`, `arena.py`, `provider_runner.py`, `run_manifest.py`,
   `public_export.py`, `participants.py`, `trace_inspection.py`,
   `acceptance.py`. Baseline real medido con el bloque estricto completo
   (no por archivo aislado, por la lección de método de la etapa 3): **45
   errores en 8 archivos**, no solo los que ya aparecían sin el override.

   `trace_inspection.py` (13 errores): exactamente el `TypedDict` previsto —
   `InspectionReport`/`InspectionError` sustituyen el `dict` acumulador sin
   anotar. Efecto colateral real: `TypedDict.update()` no admite argumentos
   de palabra clave sueltos (`report.update(x=1, y=2)`), solo un
   dict/mapping explícito (`report.update({"x": 1, "y": 2})`) — corregido.

   `participants.py`/`cli.py`: mismo ensanchamiento de `Literal` que
   `CATALOG` en la etapa 3 — `Participant.provider` pasó de `str` a
   `Literal["openai","anthropic","gemini","ollama"]` (coincide con los
   cuatro proveedores ya documentados en M5_DEMO.md; rechaza antes un
   roster con un proveedor inválido, con `ValidationError` que sigue siendo
   `ValueError`, sin romper `test_invalid_rosters_fail_before_calls`); un
   tuple literal análogo en `cli.py` anotado con `Literal["openai",
   "anthropic"]`. Hallazgo nuevo no previsto: `ProviderConfig(provider=...,
   **limits)` con `**limits` tipado (`int | float`, no implícitamente `Any`)
   expone una limitación real del plugin de mypy para Pydantic — no reparte
   por nombre un `**kwargs` de valor uniforme contra un constructor con
   campos de tipos distintos (confirmado con un caso mínimo aislado:
   funciona con kwargs explícitos, falla solo con el spread). Resuelto con
   `# type: ignore[arg-type]` puntual y documentado, mismo patrón que las
   llamadas a los SDK en la etapa 4.

   `arena.py` (18 errores): unión de tipos en un `dict` acumulador
   (`public_payload`, mismo patrón que `rules.py`/etapa 3) y un `dict` con
   lista vacía + strings sin anotar (`placeholder`); y un hallazgo de
   `typeshed`, no del proyecto: `BaseServer` (la clase genérica de la que
   depende `self.server` en un `BaseHTTPRequestHandler`) no declara
   `server_port`, aunque `ThreadingHTTPServer` sí lo tiene en runtime —
   resuelto con `assert isinstance(self.server, HTTPServer)` puntual
   (mismo patrón ya usado en `citizen_runtime.py`, con su propio `# noqa:
   S101` justificado), no con un `cast()` que no comprobaría nada.

   `cli.py` (hallazgo adicional durante la implementación, no en el
   baseline inicial): renombrar una variable sin querer a un nombre ya usado
   en la misma función (`summary`, el subparser de `argparse`) reprodujo la
   misma clase de error de unificación de tipos entre ramas que motivó los
   cambios de la etapa 3 — lección repetida: revisar nombres de variables
   existentes en toda la función antes de reutilizarlos, no solo en la rama
   que se edita.

6. **Tests:** permisivos de forma permanente (`disallow_untyped_defs = false` vía
   override en `backend/tests/*`), igual que ya se excluyen `S101`/`S105` en Ruff.

Cierre de LAB-014 (2026-10-13): `mypy backend/app` → **0 errores en 28
archivos**. Paso de CI promovido de informativo a bloqueante (ver
[.github/workflows/checks.yml](../../.github/workflows/checks.yml)); verificado
localmente solo en macOS, pendiente la primera confirmación cruzada de Linux en
el próximo push de CI. 238 tests, Ruff y cobertura (92.46%) en verde.

## LAB-015

**Integrar ciudadano con modo versionado** · prioridad 2 · sénior IA + producto · validado localmente (2026-10-10).

Entregado: `demo --citizen-mode guarded-local`, condiciones en inicio de sesión,
selectores propios por actor/sesión, diagnósticos privados y persistencia por evento.
Política explícita sin memoria; prueba con dobles con historial acredita separación.
Suite **182 passed**, Ruff y demo de dos sesiones completos.
[Guía](../CITIZEN_INTEGRATION.md) y [revisión](reviews/2026-10-10-lab015.md).
Adaptador, metadatos de red y manifiesto ampliado entregados en LAB-016 con HTTP simulado.

Dependencia: contrato/prototipo LAB-004. Añadir modo explícito sin sustituir la
referencia M1; registrar versión y condiciones antes de comparar. Integrar intentos,
rechazos y fallback en eventos privados, con testimonio como única salida pública.
Definir propiedad de selector/historial por sesión y actor, sin compartir memoria
entre competidores; probar aislamiento de extremo a extremo. El motor conserva
la autoridad sobre estado. Misma configuración ciudadana para ambas partes;
proveedor ciudadano, prompt, límites, latencia y fallos identificados por separado.
Primero validar con selector local; adaptador real y validación externa después.
No aceptar M3 por pruebas del componente aislado ni atribuir efectos sociales.

## LAB-016

**Ciudadano selector mediante API y comparación trazable** · prioridad 2 · sénior IA + producto · validado localmente con HTTP simulado (2026-10-10).

CLI explícita, configuración compartida registrada antes de llamadas, presupuesto
ciudadano agregado por sesión, contexto sin historial y adaptadores por actor/sesión.
Eventos privados de petición/respuesta/error y resultados observados en manifiesto.
Pruebas con ambos SDK, timeout, incompletitud, reparación y aislamiento.
[Contrato API](../CITIZEN_API.md). Piloto real pendiente en LAB-017.

Depende de LAB-015. Definir proveedor/modelo/prompt y política de historial ciudadano
por actor y sesión; conservar el catálogo de respuestas autorizadas. Ampliar
manifiesto previo con idénticas condiciones ciudadanas para ambos participantes.
Registrar intentos, identidad resuelta, latencia, consumo, límites y fallos sin
filtrar diagnósticos al policía. Probar con transporte simulado antes de una API
real. Cualquier memoria enviada debe quedar limitada al propio actor/sesión.
No activar por defecto ni equiparar selección controlada con conversación libre.

## LAB-017

**Piloto ciudadano API y aceptación visual con modelos reales** · prioridad 1 tras demo local · sénior IA + usuario · pendiente.

Requiere credenciales/IDs accesibles y revisión humana. Ejecutar LAB-001 con modo
ciudadano explícitamente elegido; conservar manifiestos, todas las sesiones y
fallos. Verificar presupuestos/identidades ciudadanas en trazas privadas y proyectar
la ejecución en M4. Recoger observaciones humanas, sin declarar realismo, neutralidad
o calidad policial. No cerrar por HTTP simulado ni por revisión de agentes IA.

## LAB-018

**Entrega técnica M5: cuatro carriles, proveedores y exportación** · prioridad 1 · sénior IA + producto + PM · validado localmente (2026-10-10).

Autorización: continuar la fase posterior a M4 hasta completarla, DEC-007.
Entregado: roster 2/4, Gemini/Ollama, manifiesto v2, arena adaptable, exportación
JSON/JSONL/CSV con estados/hashes y protección de fórmulas CSV. Repetición de dos
demos de cuatro sesiones prueba el guion local, no réplicas de LLM.
Evidencia: 225 pruebas, Ruff, sintaxis JS; Chrome 2/4 con replay, descargas y móvil.
[Guía](../M5_DEMO.md) · [Revisión de cuatro roles](reviews/2026-10-10-m5.md).
Cierre técnico local; servicios reales LAB-019 y aceptación humana separados.

## LAB-020

**Rigor profesional del repositorio: licencia, lint ampliado, cobertura medida y
política de seguridad** · prioridad 2 · sénior IA · validado localmente (2026-10-10).

Añadidos `LICENSE` (MIT) y `SECURITY.md`. Ampliado `select` de Ruff de
`E4,E7,E9,F` a `+B,I,UP,SIM,C4,RUF,S`, con exclusiones justificadas por archivo
(`S101`/`S105`/`S310` en tests; `S603`/`S310` en código fuente con comentario
puntual). Añadido `pytest-cov` con cobertura de ramas en `pyproject.toml`
(`fail_under = 90`) y en CI; cobertura real medida: **93%** de líneas/ramas sobre
`backend/app`. Trece pruebas nuevas cierran ramas sin probar que no requerían red
real: validaciones de CLI (`run_demo` con recuento de participantes no soportado,
combinaciones de argumentos de `run`), despacho de `arena`/`KeyboardInterrupt`/
cierre de traza incompleta en `cli.main()`, e invariantes del escenario en
`models.py` (objetivos, estado previo, tensión/cooperación, catálogo de checks,
medidor de sonido, campos de cierre) — `models.py` queda al 100%.
Añadido escaneo de dependencias (`pip-audit`). Primera ejecución real
(2026-10-12): 4 CVE (`PYSEC-2026-196`, `PYSEC-2026-3721`) en `pip==26.1` —
la propia herramienta de instalación fijada en el lock, no una dependencia de
runtime del proyecto. Corregido subiendo a `pip==26.2.1` y regenerando el lock;
auditoría limpia confirmada, paso de CI promovido de informativo a bloqueante.
Aviso de trazabilidad: esa promoción la decidió el asistente (hallazgo acotado
y sin ambigüedad), no una revisión humana — pendiente de que el usuario la
confirme o la revierta si discrepa del criterio.

Ramas que **no** se cerraron, por diseño: la llamada real a proveedores en
`cli.run_live()` (líneas de ejecución tras `--dry-run`) solo se ejercita con
credenciales reales — cerrarla con dobles contradiría el principio de no declarar
piloto real por simulación (ver LAB-001/017/019); rutas de `ImportError` de
dependencias opcionales y errores de SDK específicos de cada proveedor quedan
como trabajo futuro de menor prioridad. Plan de type-checking estático detallado
en LAB-014; bloqueado temporalmente por una incidencia de disco del equipo local,
no del proyecto.

Pendiente de quien mantiene el repositorio: confirmar el tipo de licencia (MIT
aplicada por defecto, reversible) y decidir cuándo commitear estos cambios junto
con el trabajo de M4/M5 ya presente en el árbol de trabajo.

## LAB-019

**Piloto trazable de cuatro participantes** · prioridad 1 tras entrega M5 · sénior IA + PM + usuario · pendiente.

Dependencias: IDs concretos accesibles, claves locales para proveedores remotos,
Ollama disponible con modelo elegido y condiciones del equipo registradas. No hay
credenciales ni instalación Ollama en el entorno comprobado. No descargar modelos
ni asumir un presupuesto o proveedor/modelo elegido sin definición del piloto.

Aceptación externa: manifiesto previo, cuatro sesiones intentadas, trazas/errores
conservados, identidad devuelta cuando exista, transporte/versión, límites y orden
inspeccionados; revisión humana del recorrido y de exportaciones. Si se exige
inferencia local, comprobar configuración cloud, modelo, cuantización y hardware.
Registrar intentos fallidos/cierres tempranos, sin seleccionar solo recorridos
favorables. Coordinar con LAB-001 para la pareja original y LAB-017 si se activa
ciudadano API; no duplicar evidencias ni cerrar esas tareas por mocks. LAB-006/011
siguen separados para diseño de réplicas y conclusiones científicas.

## LAB-021

**Prácticas de evaluación para la vía de paper** · prioridad 3, no bloquea demo · ciencia + sénior IA · paquete documental cerrado (2026-10-13); resto pendiente.

Origen: lista de técnicas aportada por el usuario, sin fuentes. Valoración en
[EVALUATION_PRACTICES](../research/EVALUATION_PRACTICES.md): adoptar descriptivo
trayectorias, Q1 como detección por afirmación y pruebas adversariales del arnés;
juez LLM solo auxiliar; golden datasets solo para lo determinista y calibración de rúbrica;
RAG y online evals no aplican.
Aceptación: fuentes primarias abiertas y registradas en BIBLIOGRAPHY por técnica
adoptada; lista de pruebas adversariales del arnés revisada por el sénior; rúbrica
de Q1 piloteada con humanos antes de cualquier afirmación. Depende de LAB-006/011.

Estado 2026-10-13: hecho — valoración por técnica y ocho fuentes (S7–S14) con
resumen, relación y límites, leídas por extracción de texto (no lectura humana
íntegra; S14 solo resumen). Pendiente, sin bloquear la demo: lectura humana de las
fuentes que sustenten decisiones; fuentes de golden datasets/rúbricas; versión
publicada de preprints; lista de pruebas adversariales del arnés (sénior IA); rúbrica
Q1 pilotada con humanos. Se reabre al diseñar el estudio (LAB-006/011).

## LAB-022

**Marco experimental multiescenario con primer escenario elaborado (PL-002)** · prioridad por decidir · ciencia + sénior IA + producto · pendiente de confirmación del usuario (DEC-008, propuesta 2026-10-13).

Objetivo: cuatro modelos en paralelo sobre el mismo caso, con escenarios
intercambiables y diseño lo más cercano posible a un experimento. Fases propuestas:
1. Protocolo `experiments/<id>/` (hipótesis, variables, rúbrica, bloques, exclusiones,
   parada) y escenario PL-002 versionado, revisados por ciencia y sénior.
2. Esquema de escenario 0.2: constructos medidos, hechos con categoría epistémica
   (verificable / solo testimonial / desconocido), variantes de manipulación y puntos
   de decisión; validador y pruebas.
3. Ejecutor de diseño: modelos × condiciones × repeticiones, orden contrabalanceado con
   semilla registrada, todos los intentos conservados y enlazados.
4. Anotación humana ciega (solo lo que el modelo sabía; identidad del proveedor oculta).
5. Piloto exploratorio (amplía LAB-019) para estimar variación y costes; informe
   descriptivo con denominadores. Congelar protocolo antes de cualquier tanda confirmatoria.

Dependencias: confirmar tema, dimensión de sesgo y anotadores; LAB-006/011/021 para
diseño y rúbrica; LAB-019 para claves y Ollama. Límites: no ranking ni «mejor policía»;
sin extrapolar a trabajo policial real; un LLM no es la única fuente de anotación.

