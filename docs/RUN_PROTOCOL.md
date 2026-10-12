# Protocolo operativo de la demo — M2/M3/M5

Versión de ejecución M2, no protocolo científico ni rúbrica de evaluación.

- Un escenario PL-001 y una semilla local por comparación; sesiones aisladas.
- Prompt `police-json-v1` capturado una vez por comparación; mismo texto para todos.
- Ciudadano determinista `controlled-citizen-v1`: catálogo literal ASK y saludos SPEAK.
- Ejecución secuencial según la lista de adaptadores (CLI sin roster: OpenAI, después Anthropic; con roster: orden del archivo).
- Se comprueba igualdad de límites nominales de salida, llamadas, reintentos y timeout
  antes de crear la ejecución. Una diferencia rechaza la comparación sin llamadas.
  Proveedores e IDs de modelos pueden diferir. Un único participante se admite como
  recorrido técnico, sin acreditar una comparación entre sistemas.
- Presupuesto por sesión y máximo de turnos del escenario; los reintentos consumen
  llamadas. Muestreo por defecto de cada proveedor, sin semilla de generación.
- SDK o transporte HTTP con cero reintentos internos en los adaptadores de producción. Los errores
  recuperables reciben hasta `max_retries` reintentos por acción (esperas de 1 y 2
  segundos), sujetos a `max_calls`. El fallo no recuperado cierra esa sesión y
  permite iniciar el siguiente participante. Una respuesta incompleta/rechazada
  cierra la sesión; una acción inválida se registra y puede corregirse dentro del
  límite de llamadas. Ctrl+C u otro error no controlado detienen la comparación.
- Se conservan fallos, cierres tempranos y ejecuciones interrumpidas. Nunca se
  interpreta un cierre técnico como calidad policial o aceptación del MVP.

`manifest.json` se escribe antes de cualquier llamada. Contiene protocolo, fuentes
(hash por archivo y agregado), Git si existe, entorno instalado, hashes de escenario,
prompt y esquema, ciudadano, límites, participantes, orden y política de errores.
Solo se registran nombres/versiones de paquetes, no variables de entorno, URLs de
instalación ni rutas del intérprete. Las fuentes abarcan Python de `backend/`,
`pyproject.toml`, esquema, escenario y este documento. No son una copia restaurable.
No modificar fuentes mientras una ejecución esté activa: el hash describe archivos
en disco durante la comprobación, no verifica el código ya importado en memoria.

`manifest-outcomes.json` es un archivo separado, vinculado al hash exacto del
manifiesto inicial. Recoge modelos devueltos observados por llamada (pueden cambiar),
cierres y estados de las trazas; no sustituye al JSONL. Un participante sin respuesta
no tiene un modelo resuelto conocido. Tras una interrupción, los participantes que
no se intentaron figuran como `not_started`. `run_status=loop_completed` indica que
el bucle terminó, aunque alguna sesión cerrase con error; no indica aceptación.

El manifiesto inicial no se reescribe. La escritura es exclusiva con flush/fsync;
no hay transacción entre archivos ni garantía frente a cortes de proceso/disco.
Un archivo final ausente, parcial o ilegible no acredita finalización. Los JSONL
conservados siguen siendo evidencia, incluso cuando no se pudo escribir el informe.
Las trazas se validan estructuralmente, no se autentica toda su semántica.

Iguales límites numéricos no significan igual cómputo, coste ni muestreo. Registrar
el entorno en el manifiesto no acredita restauración; LAB-007 comprueba aparte
una copia limpia con el lock versionado. Replay no regenera respuestas. Los adaptadores
personalizados o clientes SDK inyectados no se autentican con esta comprobación.
Ni el manifiesto ni el informe final se envían a los participantes.

## Variante demo-m3-selector-v1 (LAB-016)

Se activa únicamente con proveedor/modelo ciudadano explícitos. Las reglas policiales
anteriores permanecen; el ciudadano usa selección cerrada y contexto sin historial.
Una configuración ciudadana común se registra en el manifiesto y cada inicio de
sesión. Dos intentos por solicitud, SDK sin retries y presupuesto ciudadano agregado
por sesión para A+B+C. Timeout/salida incompleta/selección inválida consumen intento;
agotamiento devuelve fallback y queda registrado, sin cerrar automáticamente al
policía. Errores inesperados o interrupción conservan trazas y detienen el recorrido.

Se registran peticiones ciudadanas y metadatos de respuesta/error privados, sin
texto bruto de propuestas ni cuerpos de excepción. El informe final añade llamadas
e identidades observadas ciudadanas. El conjunto de fuentes incluye también assets
HTML/CSS/JS de `backend/app/web`. [Contrato API](CITIZEN_API.md). No se acredita igual
respuesta ciudadana por usar la misma configuración ni neutralidad de comparación.

## Variante demo-m5-v1 y manifiesto v2

Se aplica a cuatro policías o a una lista que incluya Gemini/Ollama. Las listas de
CLI admiten 2/4 participantes; la API Python admite 1–4 para pruebas técnicas.
Las parejas OpenAI/Anthropic conservan `demo-m2-v1` o `demo-m3-selector-v1` según
el ciudadano. Todos los nuevos manifiestos usan `manifest_schema_version: "2"`, IDs únicos
y orden explícito. Lectores mantienen compatibilidad con identidades antiguas.

Proveedor, ID de participante, modelo solicitado y run se cotejan con el inicio
de cada traza al recoger resultados. Repetir proveedor no fusiona participantes.
Una identidad de modelo no devuelta se registra como desconocida, nunca se copia
el modelo solicitado para inventar una observación. Las rutas de trazas conservan
su índice y proveedor por compatibilidad; el ID se obtiene del manifiesto/evento.

Gemini usa generateContent REST y Ollama chat REST no streaming, con urllib de
Python. Se registra transporte y versión de Python en lugar de atribuir un SDK.
Sin redirecciones, proxies automáticos ni reintentos internos; respuestas acotadas
a 2 MB. El motor conserva la política común de reintentos y cierres. Cada proveedor
mantiene sus defaults; los presupuestos nativos no igualan cómputo ni razonamiento.

La demo con guion escribe también un manifiesto v2 con modo `local_demo`, fuentes,
escenario/semilla, ciudadano, participantes y orden, antes de iniciar las sesiones.
No genera informe de identidades remotas ni acredita llamadas a modelos.

Las exportaciones `arena-public-v2` son proyecciones con filas de run, participante
y evento. Conservan fallos y ausencias, pero no sustituyen las trazas privadas ni
sirven de entrada a replay. [Contrato de exportación y uso](M5_DEMO.md).
