# Demo M5 — cuatro participantes y exportaciones

Entrega técnica implementada y validada localmente el 2026-10-10. Incluye arena de
2 o 4 participantes, adaptadores OpenAI/Anthropic/Gemini/Ollama y exportaciones
públicas JSON, JSONL y CSV. Los modelos reales y la aceptación humana siguen
pendientes; la demo con guion no consume APIs ni acredita capacidad policial.

## Abrir y recorrer

```sh
.venv/bin/python -m backend.app.cli arena
```

Abre **http://127.0.0.1:8765**, selecciona 4 participantes y pulsa **Iniciar demo
local**. Reproducir, Pausa, Paso, Inicio y el deslizador recorren las trazas.
Los cuatro guiones son iguales por diseño; cada sesión tiene estado e identidad
propios. El paso avanza un evento por carril, no tiempo ni cómputo equivalentes.
En pantallas grandes se muestran cuatro columnas; en portátiles dos y en móvil una.
También puedes elegir dos participantes y abrir ejecuciones M4 anteriores.

La CLI conserva dos participantes por defecto. Para cuatro:

```sh
.venv/bin/python -m backend.app.cli demo --participants 4 --citizen-mode guarded-local
```

El servidor escucha solo en loopback y permite iniciar guiones locales. Las
llamadas de modelos se lanzan desde la CLI. No es un servicio multiusuario.
Las trazas privadas permanecen en `results/private/<run_id>/`; no se sirven como
archivos descargables. El visor recibe únicamente la proyección pública.

## Configurar modelos

Copia [participants.example.json](../config/participants.example.json) a un archivo
propio y sustituye los cuatro marcadores por modelos accesibles. Formato por entrada:

```json
{"id": "gemini-01", "provider": "gemini", "model_id": "ID_DEL_MODELO"}
```

La lista debe tener 2 o 4 entradas con IDs únicos. Se permite repetir proveedor o
modelo; el ID identifica al participante. No incluyas claves ni endpoints en ella.
Para Gemini usa el ID sin el prefijo `models/`. Los límites se aplican mediante las
opciones comunes de CLI, nunca por entrada. El orden del archivo es el de ejecución.

```sh
.venv/bin/python -m backend.app.cli run --participants config/participants.example.json --dry-run
```

Este ejemplo verifica el formato y muestra el manifiesto sin red; los marcadores
no son IDs utilizables. Con tu archivo ya configurado, quitar `--dry-run` ejecuta
los modelos secuencialmente y puede consumir tokens facturados. Instala el entorno
con extras `providers` según [Desarrollo](DEVELOPMENT.md). Configura las claves
necesarias en `.env` desde [.env.example](../.env.example): `OPENAI_API_KEY`,
`ANTHROPIC_API_KEY` y `GEMINI_API_KEY`. No se necesitan claves de proveedores ausentes.
Sin `--participants`, la CLI mantiene la pareja OpenAI/Anthropic y sus IDs del entorno.

Ollama requiere un servicio ya iniciado en `http://127.0.0.1:11434` y un modelo
previamente disponible. La aplicación no instala Ollama ni descarga modelos.
Loopback identifica el endpoint, no prueba dónde se ejecuta la inferencia: Ollama
admite modelos cloud. Para un piloto local, usar un modelo local y documentar
configuración, versión, hardware y cloud deshabilitado cuando corresponda.
[Documentación oficial sobre cloud](https://docs.ollama.com/cloud).

`--citizen-provider` y `--citizen-model` habilitan el selector ciudadano con cualquiera
de los cuatro proveedores. Requiere la clave correspondiente aunque ese proveedor
no figure entre los policías. Mantiene el [contrato cerrado](CITIZEN_API.md), sin
conversación libre ni historial ciudadano. La misma configuración se aplica a todas
las sesiones; esto no garantiza respuestas idénticas.

## Exportar la vista pública

Selecciona JSON, JSONL o CSV y pulsa **Exportar eventos públicos**. Se exporta la
proyección completa disponible, incluso si el cursor está al inicio. JSON conserva
la estructura de carriles; JSONL y CSV usan filas `run`, `participant` y `event`.
Cada participante tiene una fila aunque no haya empezado o no tenga eventos legibles.

También puedes exportar desde la terminal, sustituyendo `RUN_ID` por el UUID real:

```sh
.venv/bin/python -m backend.app.cli export RUN_ID --format csv --destination /tmp/arena.csv
.venv/bin/python -m backend.app.cli export RUN_ID --format jsonl --destination /tmp/arena.jsonl
```

La CLI rechaza sobrescribir archivos. Esquema `arena-public-v2`: identidad de
run/participante/sesión, proveedor, modelo solicitado, estado de traza, hashes de
traza/escenario, archivo fuente, secuencia, turno, tipo y `payload_json`. Este último
es una cadena JSON que debe decodificarse para acceder al objeto. Los hashes vinculan
archivos leídos, no autentican autores. Durante una ejecución la exportación es una
instantánea y puede mostrar sesiones incompletas o aún sin iniciar.

CSV antepone un apóstrofo a celdas que podrían interpretarse como fórmulas (`=`,
`+`, `-`, `@`, también tras espacios); conserva comillas y saltos mediante el módulo
CSV. JSONL preserva las cadenas originales. No retirar esa protección al abrir CSV
en una hoja de cálculo. Ninguno de estos formatos públicos sustituye al JSONL privado:
no contienen prompts completos, diagnóstico ciudadano, errores crudos ni metadatos
privados del proveedor y **no son entrada del comando `replay`**.

## Código por bloques

1. [participants.py](../backend/app/participants.py): valida el roster y resuelve IDs.
   `configs, ids = load_participants(path, **limits)` separa configuración e identidad.
2. [gemini_adapter.py](../backend/app/adapters/gemini_adapter.py) y
   [ollama_adapter.py](../backend/app/adapters/ollama_adapter.py): traducen el contrato
   común a las APIs nativas; normalizan texto, fin, identidad y uso sin inventar datos.
   [http_transport.py](../backend/app/adapters/http_transport.py) acota tamaños,
   rechaza redirecciones y convierte errores de red en códigos controlados.
3. [provider_runner.py](../backend/app/provider_runner.py) y
   [run_manifest.py](../backend/app/run_manifest.py): historial independiente,
   límites comunes, manifiesto previo e identidad comprobada al recoger resultados.
4. [arena.py](../backend/app/arena.py) y [app.js](../backend/app/web/app.js): proyectan
   campos permitidos y renderizan tantos carriles como participantes. Una traza vacía
   o dañada conserva su identidad declarada y su estado visible.
5. [public_export.py](../backend/app/public_export.py): `records(projection)` genera
   las mismas filas para CSV/JSONL; no lee eventos privados directamente.
6. [test_m5.py](../backend/tests/test_m5.py) y
   [test_m5_adapters.py](../backend/tests/test_m5_adapters.py): cuatro participantes,
   proveedor repetido, fallos, interrupción, identidad, exportación y transporte simulado.

## Evidencia y límites

**225 pruebas superadas**, Ruff y sintaxis JavaScript correctos. Chrome comprobó
2 y 4 carriles, replay, escritorio/móvil, descargas JSON/JSONL/CSV y selección fallida
sin contenido anterior. [Script reproducible](../scripts/check_arena_browser.mjs)
con Chrome temporal y puerto de depuración 9222; no se integra todavía en CI.
La prueba de repetición realiza dos demos de cuatro sesiones: ocho sesiones únicas
con el mismo recorrido semántico del guion. No son réplicas estadísticas de modelos.

Gemini/Ollama se prueban con respuestas HTTP en memoria, incluyendo truncamiento,
rechazo, formato inválido y conexión cortada. No había claves ni Ollama instalado en
el entorno de validación: ningún piloto real de cuatro modelos ni aceptación humana.
Límites nominales y prompts comunes no acreditan igual cómputo ni neutralidad.
[Comparabilidad](governance/COMPARABILITY.md), [revisión](governance/reviews/2026-10-10-m5.md)
y [estado y siguientes acciones](../PROJECT_STATUS.md).

Fuentes técnicas primarias consultadas el 2026-10-10:
[Gemini generateContent](https://ai.google.dev/api/generate-content),
[claves Gemini](https://ai.google.dev/gemini-api/docs/api-key),
[Ollama chat](https://docs.ollama.com/api/chat) y
[autenticación local](https://docs.ollama.com/api/authentication).
