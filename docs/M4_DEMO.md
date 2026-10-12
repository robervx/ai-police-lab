# Demo visual M4 — uso y recorrido del código

Documento histórico de la entrega M4 (195 pruebas). La interfaz y capacidades
actuales se describen en [M5_DEMO.md](M5_DEMO.md); el selector permite 2 o 4 participantes.

La demo visual local está implementada y comprobada en Chrome. Puedes explorar
dos sesiones, sus acciones, testimonios, resultados y cierres. La conexión de
modelos reales está implementada, pero su piloto sigue pendiente de credenciales.
No se ha realizado aceptación humana ni evaluación científica.

## Abrir el laboratorio

Desde la raíz del proyecto, con el entorno instalado según [Desarrollo](DEVELOPMENT.md):

```sh
.venv/bin/python -m backend.app.cli arena
```

Abre **http://127.0.0.1:8765** y pulsa **Iniciar demo local**. Se guardan dos
sesiones nuevas del guion de referencia con ciudadano controlado, sin APIs. Pulsa
Reproducir, Pausa, Paso o mueve el deslizador. Inicio vuelve al principio. Los
carriles usan instancias separadas aunque este guion produzca el mismo recorrido.

El selector recupera ejecuciones de `results/private/`. Actualizar vuelve a leer
la lista y la selección. «Actualizar cada 2 s» sigue la traza seleccionada mediante
peticiones periódicas; no presupone que haya un proceso activo. Exportar eventos
públicos descarga toda la proyección de la ejecución, no solo lo ya reproducido.

El servidor solo escucha en loopback. `--port 8766` cambia el puerto;
`--output RUTA` cambia la carpeta de ejecuciones. Ctrl+C lo detiene. No sirve archivos
arbitrarios, claves ni JSONL privados. No es un servidor de producción multiusuario.

## Ver ejecuciones de modelos reales

Configura `.env` desde `.env.example` con las dos claves y los dos IDs de modelos.
En otra terminal, manteniendo la misma carpeta de salida del visor:

```sh
.venv/bin/python -m backend.app.cli run --dry-run
.venv/bin/python -m backend.app.cli run
```

El primer comando no llama a APIs; el segundo consume tokens. Pulsa Actualizar en
el visor, elige la ejecución y activa la actualización periódica. El runner ejecuta
OpenAI y Anthropic **secuencialmente**. El segundo carril puede figurar sin traza
hasta que le llegue el turno. No se lanzan llamadas pagadas desde el navegador.

Para seleccionar respuestas ciudadanas mediante una API, añade explícitamente:

```sh
.venv/bin/python -m backend.app.cli run \
  --citizen-provider openai --citizen-model ID_CIUDADANO \
  --citizen-max-calls 24 --citizen-max-output-tokens 256 --dry-run
```

`ID_CIUDADANO` es un marcador: sustitúyelo por un modelo accesible en tu cuenta.
Quitar `--dry-run` habilita llamadas del policía y del ciudadano. También se admite
`--citizen-provider anthropic`. Se reutiliza la clave del proveedor elegido.
[Detalles del contrato API](CITIZEN_API.md).

## Interpretar lo que muestra

| Elemento | Significado |
|---|---|
| Demo local con guion | Agente ficticio; no respuesta de un modelo remoto |
| Identificador solicitado | Modelo configurado; identidades devueltas se conservan en la traza privada |
| Testimonio | Declaración ciudadana; no equivale a observación verificada |
| Traza completa | Estructura válida con cierre; no indica éxito policial |
| Incompleta | Sin cierre registrado; puede estar activa o interrumpida |
| Dañada | Se muestra solo el prefijo válido; nunca se omite el error silenciosamente |
| No legible | No se pudo cargar o no corresponde a la ejecución seleccionada |
| Paso | Un evento público por carril, no tiempo ni cómputo equivalentes |

El visor no incorpora declaraciones externas de revisión humana. El comando
`summary --review` sigue siendo el lugar para asociarlas por hash. Un aviso señala
escenarios con hashes distintos; ninguna ausencia de aviso certifica neutralidad.

## Código, bloque por bloque

1. [cli.py](../backend/app/cli.py) inicia `arena` y conserva comandos de ejecución.
2. [arena.py](../backend/app/arena.py), `ArenaStore`, localiza ejecuciones por UUID;
   verifica identidad y rechaza enlaces simbólicos. `project_trace` usa el mismo
   inspector de trazas y mantiene orden `seq` del prefijo validado.
3. `public_payload` proyecta por **tipo de evento y campo hoja**. No serializa
   eventos de proveedores, diagnóstico ciudadano, hechos privados ni estado social.
   El navegador nunca recibe estos objetos para ocultarlos posteriormente.
4. [index.html](../backend/app/web/index.html) define controles y dos carriles;
   [style.css](../backend/app/web/style.css) adapta escritorio y móvil.
5. [app.js](../backend/app/web/app.js) administra selección, cursor, reproducción
   y actualización. Usa `textContent` para mensajes; un texto con HTML no se ejecuta.
   Cambiar de ejecución vacía los datos anteriores incluso si la nueva carga falla.
6. [test_arena.py](../backend/tests/test_arena.py) prueba proyección, corrupción,
   identidad, rutas, Host/Origin y servidor local. [Prueba de Chrome](../scripts/check_arena_browser.mjs)
   comprueba los controles y tamaños de pantalla mediante un navegador temporal.

## Validación y límites

Suite completa: **195 pruebas superadas**, Ruff y sintaxis JavaScript correctos.
Chrome: demo nueva, dos carriles, paso, reproducción/pausa, desplazamiento del cursor,
inicio, escritorio/móvil sin desbordamiento horizontal y selección fallida sin datos
anteriores. Esta prueba de navegador es local, no forma parte todavía del workflow CI.

La implementación usa servidor HTTP de Python, HTML/CSS/JS y actualización periódica,
según [DEC-006](governance/DECISIONS.md#dec-006--entrega-local-m4-y-alcance-del-ciudadano).
No incorpora React, WebSocket ni una base de datos. Lee trazas de hasta 16 MiB por
archivo y muestra dos carriles; más participantes corresponden a M5. Validación
estructural e identidad no autentican autores ni comprueban toda la semántica del log.
Las claves están ausentes en el entorno usado: no se ha ejecutado el piloto real.
