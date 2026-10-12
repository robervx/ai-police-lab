# Política de seguridad

Este es un laboratorio de simulación ficticia para investigación y formación.
No es un sistema de apoyo policial real; no procesa datos personales reales ni
se conecta a sistemas operativos reservados. Aun así, ejecuta un servidor HTTP
local y realiza llamadas a APIs externas con credenciales del usuario
(`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`), por lo que sigue
una política de reporte responsable.

## Alcance

Cubre el código de este repositorio: motor determinista, adaptadores de
proveedores (`backend/app/adapters/`), el servidor local `arena`
(`backend/app/arena.py`) y las exportaciones públicas (`backend/app/public_export.py`).

No cubre vulnerabilidades de los propios proveedores (OpenAI, Anthropic,
Google, Ollama) ni del entorno del usuario (sistema operativo, red, claves
filtradas fuera de este código).

## Reportar una vulnerabilidad

Abre un [issue de seguridad privado](https://github.com/robervx/ai-police-lab/security/advisories/new)
en el repositorio, o contacta directamente con el mantenedor. No abras un
issue público con detalles de explotación hasta que exista una corrección.

Incluye: pasos de reproducción, versión/commit afectado, impacto esperado
(por ejemplo, filtración de hechos ocultos del escenario, fuga de claves,
bypass del servidor loopback o inyección en las exportaciones CSV/JSONL) y,
si es posible, una prueba de concepto mínima con datos ficticios.

## Qué esperar

Se confirma la recepción y se evalúa el alcance con prioridad proporcional al
riesgo (filtración de secretos o de hechos privados del escenario > denegación
de servicio local > hallazgos de estilo/lint). No se garantiza un plazo fijo de
respuesta: es un proyecto de un solo mantenedor con roles de revisión asistidos
por IA, no un equipo de seguridad dedicado.

## Garantías de diseño ya aplicadas

Documentadas para que un reporte pueda centrarse en lo que realmente falta:

- El servidor `arena` solo escucha en `127.0.0.1` y valida la cabecera `Host`
  frente a DNS rebinding; no acepta conexiones externas.
- El transporte HTTP hacia proveedores (`http_transport.py`) deshabilita
  redirecciones y el proxy del entorno, y limita el tamaño de la respuesta.
- Las claves configuradas se redactan (`secrets.py`) antes de escribirse en
  manifiestos, trazas o salida de terminal.
- Las exportaciones CSV escapan celdas que empiezan por `=`, `+`, `-` o `@`
  para evitar inyección de fórmulas en hojas de cálculo.
- Las trazas son de solo-apéndice (`event_store.py`) y se validan con un
  esquema estricto tanto al escribir como al leer.
