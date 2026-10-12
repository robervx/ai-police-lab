# LAB-015 — ciudadano controlado en dos sesiones locales

```sh
.venv/bin/python -m backend.app.cli demo --citizen-mode guarded-local
```

Ejecuta el guion de referencia con un selector determinista que elige la primera
respuesta autorizada. No llama a APIs ni genera conversación libre. Ambos
participantes usan el mismo modo, contrato y límites; sus instancias son distintas.
El modo predeterminado `baseline` conserva el ciudadano M1. `run` usa baseline por defecto; LAB-016 añade [modo ciudadano API](CITIZEN_API.md).

## Bloque 1: propiedad por sesión y actor

[citizen_runtime.py](../backend/app/citizen_runtime.py) crea un `LocalSelector`
para cada actor. [SessionManager](../backend/app/session_manager.py) crea un nuevo
runtime en cada sesión y valida previamente la compatibilidad con el catálogo.
El modo del runtime queda fijado; sus componentes internos son código de confianza,
no un aislamiento de procesos. `_selectors` es un diccionario mutable interno.
Los metadatos no prueban ausencia de manipulación posterior por código de confianza.

La política de memoria es `none`: no se acumula historial ciudadano. Las pruebas
sustituyen selectores por dobles con memoria para comprobar que una llamada a B
no llega a A, C ni al otro participante. Esto no valida todavía un adaptador LLM.

## Bloque 2: respuesta pública y diagnóstico privado

En [RuleEngine](../backend/app/rules.py):

```python
result, diagnostic = session.citizen.reply(scenario, action)
if diagnostic is not None:
    self._record(session, "citizen_diagnostic", {"turn": session.turn + 1, **diagnostic})
```

El motor registra después `citizen_utterance`, completa el turno y devuelve solo
el resultado público: `target`, `text`, `source`. `target` permite asociar el
testimonio al actor en el cierre del guion. Los hechos no se añaden a evidencia
verificada y el ciudadano no cambia estados sociales.

`citizen_diagnostic` contiene turno, actor, versión, respuesta seleccionada, hechos,
número de intentos, rechazos en orden, motivo y fallback. No conserva prosa rechazada
ni cuerpos de errores. Es un resumen por solicitud, no una traza de red por intento.

## Bloque 3: condiciones y persistencia

`session_started` registra `first-authorized-answer-v1`, versión del contrato,
modo, proveedor local, máximo de dos intentos, política de memoria y alcance de
instancias. Estos datos se guardan antes de las acciones. No hay modelo remoto,
prompt LLM, tokens o latencia de API que registrar en este modo.

[La CLI](../backend/app/cli.py) abre un JSONL exclusivo por sesión y utiliza
`JsonlEventSink` con flush/fsync por evento en guarded-local. Un fallo inesperado
deja el prefijo guardado; no se oculta como fallback normal ni se reanuda la sesión.
Un corte durante una escritura todavía puede dejar una última línea parcial.
Baseline conserva exportación al final. El modo local no genera manifiesto de
comparación M2; LAB-016 amplía ese manifiesto cuando se activa el ciudadano API.

## Bloque 4: inspección y pruebas

La demo imprime las rutas reales. Para una de ellas:

```sh
.venv/bin/python -m backend.app.cli replay RUTA.jsonl
.venv/bin/python -m backend.app.cli summary RUTA.jsonl
.venv/bin/python -m backend.app.cli inspect RUTA.jsonl
```

Sustituye `RUTA.jsonl` por la ruta impresa. **Demo, replay e inspect muestran datos
de inspección privada**, incluido el diagnóstico; su salida completa no debe usarse
como contexto de participantes ni emitirse en un visor público.

Se añade `citizen_diagnostic` al catálogo de eventos 0.1. El lector actual admite
trazas antiguas; un lector anterior puede rechazar el nuevo tipo. Valida campos,
tipos, códigos y coherencia de intentos/rechazos. El turno/actor relaciona el
diagnóstico con la solicitud; no se valida semánticamente todo el ciclo de turnos.
Replay reproduce registros sin ejecutar selectores. Summary cuenta testimonios,
sin sumar diagnósticos como intercambios adicionales.

[Pruebas de integración](../backend/tests/test_citizen_integration.py): dos sesiones,
separación con dobles con memoria, regeneración/fallback, preguntas desconocidas,
SPEAK, acciones inválidas, JSONL incompleto y diagnósticos manipulados.

LAB-015 valida este recorrido local. LAB-016 añade selector API y condiciones
de proveedor con HTTP simulado; su validación externa sigue pendiente. No acredita neutralidad, realismo humano ni
detección general de contradicciones en prosa.
