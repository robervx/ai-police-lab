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

**Contrato del ciudadano M3** · prioridad 2 · producto + sénior IA · pendiente.

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

**Trazas interrumpidas y replay** · prioridad 2 · sénior IA · pendiente.

Aceptación: especificar comportamiento ante última línea parcial/fallo de disco,
preservar el original y distinguir replay cronológico, reconstrucción y reanudación.
Antes de M4, el visor debe mostrar incompletitud de forma explícita. No prometer
atomicidad de turno por disponer de `fsync` en eventos individuales.

## LAB-009

**Demo visual de dos carriles M4** · prioridad 3 · producto + sénior IA · pendiente.

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
no se han invocado los otros tres perfiles ni verificado otra interfaz del cliente.

## LAB-013

**Identificador único de participante en exportaciones M5** · prioridad 3 · sénior IA · pendiente.

Origen: SEN-003-05, revisión LAB-003. Actualmente `participant_id` es el proveedor;
las sesiones se distinguen por `session_id`, orden y ruta, incluso al repetir
proveedor. Antes de ampliar exportaciones, asignar un identificador único por
participante y probar modelos del mismo proveedor sin mezclar trazas. No bloquea M2.

## LAB-014

**Análisis estático de tipos gradual** · prioridad 2 · sénior IA · pendiente.

Ruff y pytest automatizados cubren lint básico y comportamiento. Añadir type-checking
por módulos cuando se delimiten contratos y exclusiones; no declarar cobertura mypy
actual ni bloquear el piloto por una conversión masiva de anotaciones.
