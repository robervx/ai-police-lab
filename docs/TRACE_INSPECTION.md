# Inspección de trazas interrumpidas — LAB-008

`inspect` permite consultar el prefijo estructuralmente válido de una instantánea
del archivo. No modifica, repara, reanuda ni acepta una sesión.

```sh
.venv/bin/python -m backend.app.cli inspect ruta/a/sesion.jsonl
.venv/bin/python -m backend.app.cli inspect ruta/a/sesion.jsonl --json
```

El diagnóstico incluye SHA256 de todos los bytes capturados, tamaño, eventos y
bytes del prefijo, bytes sin validar y primer error. La línea empieza en 1; el
offset empieza en 0 y señala **el comienzo de la línea**, no necesariamente el
byte exacto defectuoso. No imprime el contenido bruto de la línea dañada.

Se detiene en el primer fallo UTF-8, JSON, esquema, secuencia, identidad o ciclo
de sesión. No salta líneas para incorporar eventos posteriores. Un cierre seguido
de basura mantiene el archivo como inválido, aunque el prefijo contenga un cierre.
Archivo vacío o sin inicio de sesión: prefijo vacío y error.

LF, CRLF y CR se admiten conservando offsets en bytes. Un evento completo al final
sin salto de línea es válido: esa ausencia no demuestra por sí sola truncamiento.
Un carácter UTF-8 cortado al final no impide consultar los eventos anteriores.

## Tres operaciones diferentes

| Operación | Alcance |
|---|---|
| `replay` | Lectura estricta del archivo completo y cronología; rechaza corrupción |
| `summary` | Resumen de aceptación estructural; no calcula totales de una traza inválida |
| `inspect` | Diagnóstico y prefijo válido; no proporciona una aceptación ni conteos globales de la sesión dañada |

El `trace_status` de inspección es estructural: `complete` indica cierre presente,
`incomplete` indica ausencia de cierre, `invalid` indica fallo y `unreadable` indica
archivo no legible. El esquema permite payloads genéricos: una estructura válida
no certifica motivos de cierre, transiciones, autenticidad o coherencia semántica.
`summary` realiza sus comprobaciones adicionales independientemente.

Código de salida: 1 ante corrupción/ilegibilidad, 0 si la estructura capturada es
válida, incluso sin cierre. El código 0 nunca significa calidad policial ni MVP aceptado.

## Cortes y escritura

La escritura durable sigue siendo por evento, no una transacción de turno.
Un corte puede dejar eventos completos de un turno sin su resultado o una línea
parcial. Se conserva siempre el original. La inspección no recupera bytes que no
llegaron al disco ni habilita reanudar el motor. Un fallo de lectura/escritura se
debe investigar antes de nuevas ejecuciones; no sobrescribir la evidencia.

Si el archivo está creciendo, el informe corresponde solo a los bytes capturados
en esa lectura. No es un bloqueo del escritor ni una instantánea transaccional.
El hash identifica esa captura, no garantiza que coincida con el archivo posteriormente.

## Código por bloques

1. `event_store.iter_events()` comparte las reglas entre lectura estricta e inspección.
2. `trace_inspection.inspect_trace()` captura bytes, calcula hash y retiene el prefijo.
3. `cli.py` ofrece texto o JSON, escapando controles de terminal como en `replay`.
4. `test_trace_inspection.py` verifica cortes, offsets, preservación del original y errores.

No cambia escenario, prompts, condiciones de participación ni resultados de aceptación.
