# Protocolo operativo de la demo — demo-m2-v1

Versión de ejecución M2, no protocolo científico ni rúbrica de evaluación.

- Un escenario PL-001 y una semilla local por comparación; sesiones aisladas.
- Prompt `police-json-v1` capturado una vez por comparación; mismo texto para todos.
- Ciudadano determinista `controlled-citizen-v1`: catálogo literal ASK y saludos SPEAK.
- Ejecución secuencial según la lista de adaptadores (CLI: OpenAI, después Anthropic).
- Se comprueba igualdad de límites nominales de salida, llamadas, reintentos y timeout
  antes de crear la ejecución. Una diferencia rechaza la comparación sin llamadas.
  Proveedores e IDs de modelos pueden diferir. Un único participante se admite como
  recorrido técnico, sin acreditar una comparación entre sistemas.
- Presupuesto por sesión y máximo de turnos del escenario; los reintentos consumen
  llamadas. Muestreo por defecto de cada proveedor, sin semilla de generación.
- SDK con cero reintentos internos en los adaptadores de producción. Los errores
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
