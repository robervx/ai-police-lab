# LAB-016 — selector ciudadano mediante API

Implementado y validado con SDKs y transportes HTTP simulados. Servicios reales
pendientes. El modelo elige un ID dentro de las opciones autorizadas; el servidor
produce el texto fijo correspondiente. No es conversación libre ni un filtro
general de contradicciones. El contrato cerrado continúa en [CITIZEN_CONTRACT](CITIZEN_CONTRACT.md).

## Activación y condiciones

`run --citizen-provider openai --citizen-model ID` habilita el modo `guarded-api`.
Se admiten también `anthropic`, `gemini` y `ollama` desde M5. Ambas opciones deben aparecer juntas; sin ellas se
mantiene baseline. `--dry-run` muestra condiciones sin crear clientes ni llamar a red.

La misma configuración ciudadana se aplica a todos los participantes. El manifiesto
previo usa protocolo `demo-m3-selector-v1`; registra proveedor/modelo solicitado,
versión/hash del prompt, política sin memoria, límites y defaults de muestreo. No
equivale a respuestas idénticas, igual cómputo ni neutralidad. El modo baseline
mantiene `demo-m2-v1` en la pareja antigua. Con cuatro policías o un policía
Gemini/Ollama se usa `demo-m5-v1`, conservando las condiciones ciudadanas. `session_started` repite las condiciones ciudadanas.

## Flujo de código

[citizen_api.py](../backend/app/citizen_api.py) implementa `ApiSelector.propose` sobre
el método `generate` de los adaptadores existentes. Cada llamada envía una única
entrada con actor, pregunta canónica, opciones autorizadas y código de reparación.
No envía historial, estado social, otros actores ni respuesta rechazada. No usa
identificadores de conversación remota. La política de memoria es explícitamente `none`.

[citizen_runtime.py](../backend/app/citizen_runtime.py) crea selectores/adaptadores
propios por actor y sesión. Todos los actores de una sesión comparten `CitizenBudget`.
`--citizen-max-calls` (24 por defecto) limita la suma A+B+C, incluidos fallos y
regeneraciones. Cada solicitud admite hasta dos intentos; SDK/adaptadores no añaden
reintentos. Agotado el presupuesto, se registra `call_limit` sin enviar otra petición
y se aplica desconocimiento. El policía conserva su presupuesto independiente.

`--citizen-max-output-tokens` limita cada respuesta (256 por defecto); `--timeout`
también se aplica a estas llamadas. No son un presupuesto monetario: hay tokens
de entrada y posibles diferencias de proveedor/modelo. Una salida incompleta o
rechazada no se acepta aunque contenga un ID válido. Errores esperados se convierten
en diagnóstico controlado; errores de programación o Ctrl+C conservan el prefijo.

La CLI cierra todos los clientes mediante `ExitStack`, incluso al fallar. La función
Python `run_comparison` recibe una fábrica cuyo llamador es responsable de cerrar
sus adaptadores; la implementación CLI lo hace. Código y objetos internos son de
confianza; estas fronteras no aíslan código Python hostil en otro proceso.

## Registro privado

Por intento de red se guardan `citizen_provider_request`, `citizen_provider_response`
o `citizen_provider_error`, con turno/actor y número de llamada cuando se envió.
Se registran prompt/contexto autorizado, versión SDK o transporte HTTP, modelo devuelto, uso y latencia
disponibles. No se registra texto bruto de la propuesta ni cuerpos de error. Los
códigos de fallo usan una allowlist; el coste sigue desconocido (`null`). El resultado
final conserva intentos, violaciones y fallback en `citizen_diagnostic`.

`manifest-outcomes.json` incluye identidades ciudadanas observadas y llamadas de
red por sesión. Las respuestas sin identidad observada no se inventan. Solo el
testimonio (`target`, `text`, `source`) entra en el retorno al policía; la proyección
del visor excluye todos los eventos de proveedores y diagnósticos.

## Evidencia y fuente técnica

[test_citizen_api.py](../backend/tests/test_citizen_api.py) usa ambos SDK con HTTP
simulado: reparación sin reenvío de propuesta, aislamiento, presupuesto compartido,
timeout/salida incompleta, manifiesto, dry-run y ausencia de diagnósticos en el
contexto del policía. Ninguna de estas pruebas valida acceso real a cuentas/modelos.

OpenAI conserva el adaptador existente: `instructions`, lista de mensajes en `input`
y `store=False`; referencia oficial consultada el 2026-10-10:
[Responses API](https://developers.openai.com/api/docs/guides/migrate-to-responses).
Esto no debe confundirse con una garantía general de retención cero. No se cambian
los SDK ni los IDs de modelo del usuario.

M5 reutiliza este contrato para Gemini/Ollama. Sus adaptadores policiales tienen
pruebas HTTP simuladas propias; esto no equivale a un piloto ciudadano real con
esos proveedores. Ver [guía M5](M5_DEMO.md).
