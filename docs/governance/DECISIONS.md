# Registro de decisiones

No sustituye al historial de código. Registrar contexto, decisión, responsable,
consecuencia y condición de revisión. Una propuesta no es una aprobación humana.

## DEC-001 — Demo funcional como prioridad

- Fecha: 2026-10-09.
- Estado: decisión explícita del usuario, mediante respuesta durante esta sesión.
- Decisión: desarrollar primero una demostración funcional para explorar
  investigación y formación; no seleccionar aún una vía como producto validado.
- Consecuencia: priorizar recorrido M2 y comprensión de resultados; preparar
  metodología sin exigir un estudio formal para mostrar la demo.
- Revisar: al disponer de una demo inspeccionable y feedback real (LAB-010).

## DEC-002 — Separar gestión y participantes

- Fecha: 2026-10-09.
- Estado: diseño aplicado dentro de la petición de cuatro roles.
- Decisión: PM, producto, sénior IA y ciencia revisan el desarrollo; no participan
  en la simulación ni envían notas de evaluación a los modelos comparados.
- Consecuencia: fichas persistentes, revisiones acotadas y coordinación central.
- Límite: múltiples revisores IA no equivalen a independencia humana o institucional.

## DEC-003 — Estado único por fases y evidencia

- Fecha: 2026-10-09.
- Estado: aplicado documentalmente por el coordinador.
- Decisión: `PROJECT_STATUS.md` es la entrada de estado; especificaciones describen
  intención, tests y trazas aportan evidencia, backlog contiene trabajo pendiente.
- Consecuencia: M2 no se declara aceptado por pruebas simuladas; separar MVP
  headless, visual de dos carriles y arena de cuatro.

## DEC-004 — Comparabilidad antes que ganador

- Fecha: 2026-10-09.
- Estado: recomendación técnica/científica adoptada como límite de comunicación,
  coherente con el alcance vigente que excluye rankings científicos.
- Decisión: describir la demo como observación comparada de sistemas configurados;
  no asignar ganador, empatía, legalidad o eficacia real a partir de esta evidencia.
- Consecuencia: conservar logs y dimensiones distintas; documentar asimetrías.
- Revisar: solo ante una nueva petición de estudio y protocolo adecuado.

## DEC-005 — Mantener explícitas las capacidades parciales

- Fecha: 2026-10-09.
- Estado: aplicado a la documentación; cambios funcionales aún pendientes.
- Hallazgo: `run_session()` no pasa etiquetas revisadas; el ciudadano tampoco
  utiliza tensión/cooperación para sus respuestas actuales.
- Decisión: registrar capacidad parcial, sin insertar automáticamente un juez
  semántico. Resolver el diseño en LAB-005 antes de atribuir efectos sociales.

## Plantilla para siguientes decisiones

```text
ID / fecha / estado (propuesta, decidida por usuario, aplicada, sustituida)
Problema y evidencia
Alternativas y efectos sobre demo, equidad y metodología
Decisión y quién la toma
Acciones de backlog y criterio de revisión
```
