# AI POLICE LAB — instrucciones del equipo

## Prioridad y fuentes de verdad

- Prioridad acordada el 2026-10-09: construir una **demostración funcional** para
  explorar después investigación y formación. No asumir aún que sea un estudio
  científico ni una herramienta de formación validada.
- Antes de una tarea sustancial, leer `PROJECT_STATUS.md` y el rol pertinente de
  `docs/governance/ROLES.md`. El alcance funcional sigue en `docs/PROJECT_SPEC.md`.
- Los agentes de gestión son asistentes del desarrollo. No son los modelos
  competidores ni los ciudadanos simulados; sus evaluaciones no entran en el
  contexto de los participantes.

## Uso de los cuatro roles

- `project_manager`: fases, dependencias, avance, evidencia, riesgos y próxima acción.
- `product_manager`: objetivo de la demo, utilidad, coherencia y control de alcance.
- `senior_ai_developer`: arquitectura, aislamiento, reglas y comparabilidad entre modelos.
- `scientific_director`: constructos, hipótesis, metodología, bibliografía y límites.
- Para una «revisión conjunta» o un cambio de fase, delegar revisiones acotadas a
  estos roles cuando haya capacidad. Respetar el límite de concurrencia; no es
  necesario ejecutar los cuatro a la vez ni para cambios triviales.
- Para cambios de comportamiento del motor o comparación, pedir revisión al
  sénior; para conclusiones o diseño experimental, al director científico; para
  cambios de objetivo o público, a producto. El coordinador integra el resultado.
- Si no pueden lanzarse subagentes, aplicar las fichas por separado y declarar
  que la revisión fue secuencial por un mismo asistente. No inventar revisores.
- Los revisores trabajan en lectura por defecto y entregan hallazgos. El agente
  principal mantiene los documentos compartidos para evitar escrituras en conflicto.

## Flujo de trabajo

1. Identificar fase, objetivo, criterio de salida y evidencia necesaria.
2. Ejecutar el trabajo autorizado en incrementos pequeños. Explicar al usuario
   cada bloque con fragmentos y enlaces al código, según su preferencia.
3. Validar de forma proporcionada. No confundir mocks, demo local, API real y
   revisión humana. Para código: `.venv/bin/python -m pytest -q --tb=short` con
   extras pertinentes. Para documentación: enlaces, consistencia y fuentes.
4. Registrar hallazgos con evidencia y convertir acciones en IDs del backlog.
5. Actualizar `PROJECT_STATUS.md`, `docs/governance/BACKLOG.md` y `CHANGELOG.md`
   cuando cambie el estado. Añadir decisiones/revisiones solo cuando aporten algo.
6. Informar de qué quedó hecho, qué se comprobó, límites y siguiente paso.

No repetir aprobaciones para trabajo ya autorizado. Un desacuerdo de revisión
produce una recomendación y su justificación, no un bloqueo automático de la demo.
Si exige cambiar el objetivo del usuario, explicar la decisión pendiente.

## Evidencia y neutralidad

- No modificar verdad del escenario sin versión y justificación.
- No exponer secretos, hechos ocultos, notas de revisión ni resultados de otros
  participantes a un agente competidor. Solo casos ficticios y datos sintéticos.
- No introducir puntuaciones de legalidad, empatía o eficacia policial sin una
  nueva definición de alcance y validación pertinente.
- Conservar cierre temprano, fallos y ejecuciones incompletas. No elegir solo
  resultados favorables ni retocar prompts por proveedor después de ver ganadores.
- Iguales límites numéricos no acreditan igual cómputo; mismo prompt no basta
  para afirmar neutralidad. Ver `docs/governance/COMPARABILITY.md`.
- Toda afirmación científica debe separar fuente verificada, evidencia local e
  hipótesis. No inventar citas, resultados, revisiones humanas ni credenciales.
- Los roles no constituyen supervisión continua, auditoría externa ni revisión
  científica independiente. Se activan durante tareas de este proyecto.
