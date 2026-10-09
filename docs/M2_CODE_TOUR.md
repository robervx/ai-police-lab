# M2 — leer el código parte por parte

Este recorrido sigue una petición desde la configuración hasta su registro.
Abre los archivos en este orden; cada bloque tiene una responsabilidad concreta.

## 1. El contrato entre el simulador y los modelos

Archivo: `backend/app/adapters/base.py`.

```python
class PoliceModelAdapter(Protocol):
    config: ProviderConfig

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply: ...

    def close(self) -> None: ...
```

`Protocol` describe lo que debe ofrecer cada adaptador. El resto de la aplicación
usa `generate()` sin conocer el SDK concreto. `ProviderConfig` valida el modelo,
el presupuesto de salida, el timeout y los límites de llamadas/reintentos.
No contiene claves. `ModelReply` reúne texto, modelo devuelto, ID de respuesta,
tokens y motivo de finalización. `ProviderError` contiene un código controlado.

## 2. Qué instrucciones recibe el modelo

Archivo: `backend/app/prompts.py`.

`police_instructions()` construye el mismo prompt para los dos proveedores.
Incluye el JSON Schema original y el catálogo público de preguntas admitidas.
No incluye las respuestas del catálogo, `knows`, hechos privados ni estado interno.
La versión es `police-json-v1`; la traza guarda también el texto y su SHA256.

Las preguntas exactas son una limitación deliberada del ciudadano de M1: un modelo
que las reformule puede recibir desconocimiento. M2 no cambia ese comportamiento.

## 3. Las llamadas de cada proveedor

Archivos: `backend/app/adapters/openai_adapter.py` y `anthropic_adapter.py`.

```python
response = self._client.responses.create(
    model=self.config.model_id,
    instructions=instructions,
    input=messages,
    max_output_tokens=self.config.max_output_tokens,
    store=False,
)
```

OpenAI usa Responses. Anthropic usa Messages y recibe `system`, `messages` y
`max_tokens`. Los adaptadores normalizan sus respuestas al mismo `ModelReply`.
Las claves se usan únicamente al construir los clientes; no se registran cabeceras.
Los endpoints están fijados a los proveedores oficiales.

El prompt pide JSON; M2 no usa salidas estructuradas nativas ni herramientas del
proveedor. El motor valida el JSON Schema localmente. Una respuesta puede ser
JSON inválido y se tratará como acción rechazada, sin cambiar el estado narrativo.

## 4. El ciclo de una sesión

Archivo: `backend/app/provider_runner.py`, función `run_session()`.

1. Crea el historial con el aviso público y el límite de turnos.
2. Registra `provider_request` antes de llamar a la API.
3. Llama a `adapter.generate()` y mide el tiempo de esa llamada.
4. Registra `provider_response`, modelo devuelto, uso de tokens y texto.
5. Descarta respuestas incompletas o rechazadas por el proveedor.
6. Envía una respuesta completa a `engine.execute()`.
7. Añade acción y resultado al historial de esa sesión.

```python
result = engine.execute(session, text)
messages.extend([
    {"role": "assistant", "content": text},
    {"role": "user", "content": json.dumps(result, ensure_ascii=False)},
])
```

Los errores transitorios admiten un reintento por defecto, visible en la traza.
Los SDK tienen sus reintentos automáticos desactivados para contar cada intento.
Los errores de autenticación no se reintentan. Una acción inválida se comunica al
modelo para que pueda corregirla. Todas las llamadas, incluso las fallidas,
cuentan para `max_calls`; los rechazos no consumen un turno del escenario.

## 5. Trazas mientras se ejecuta

Archivo: `backend/app/event_store.py`, clase `JsonlEventSink`.

```python
self._stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
self._stream.flush()
os.fsync(self._stream.fileno())
```

Se crea un archivo exclusivo por sesión. `RuleEngine._record()` envía el evento al
sink antes de añadirlo al historial en memoria. Un error al escribir detiene el
proceso; si ocurre al registrar una petición, no se llama a la API.

La durabilidad es por evento, no una transacción atómica de todo el turno. Un corte
abrupto puede dejar una sesión incompleta o una última línea parcial. El replay
rechaza esa línea; M2 no ofrece reanudación automática ni reparación del archivo.
Ctrl+C registra un cierre técnico cuando el proceso puede gestionarlo.

`backend/app/secrets.py` oculta las claves configuradas y cadenas con forma `sk-…`
antes de guardar texto o devolverlo al historial. Los cuerpos de errores HTTP no
se guardan. Esta protección no es un detector general de datos personales.

## 6. Cómo se inicia desde la terminal

Archivo: `backend/app/cli.py`, función `run_live()`.

Carga `.env` sin reemplazar las variables ya presentes en el entorno, valida la
configuración, comprueba ambas claves y crea los adaptadores. `--dry-run` imprime
solo configuración y no necesita claves ni inicia peticiones. Las sesiones reales
se ejecutan consecutivamente y sus SDK se cierran al finalizar.

```sh
.venv/bin/python -m backend.app.cli run \
  --openai-model modelo-openai \
  --anthropic-model modelo-anthropic \
  --dry-run
```

Los IDs anteriores son marcadores para revisar la configuración, no modelos reales.
Para una ejecución real, rellena los IDs accesibles en tu cuenta y las claves en
`.env`, y ejecuta `run` sin `--dry-run`. Nunca pegues claves en los argumentos.

## 7. Dónde comprobar cada garantía

Archivo: `backend/tests/test_m2.py`.

Las pruebas usan los SDK instalados sobre transportes HTTP en memoria: verifican
el JSON que se enviaría y procesan respuestas simuladas con los parsers reales.
Cubren los dos proveedores, tres entrevistas, aislamiento, timeouts, errores HTTP,
respuesta incompleta, JSON inválido, límite de llamadas, claves ocultas, escritura
antes de la llamada y conservación de la traza tras Ctrl+C.

No prueban disponibilidad de modelos, credenciales, facturación ni respuestas de
servicios reales. Esa validación requiere ejecutar `run` con configuración real.

## Referencias de implementación

- [OpenAI Responses](https://developers.openai.com/api/reference/python/resources/responses/methods/create)
- [SDK Python de OpenAI](https://developers.openai.com/api/reference/python)
- [Anthropic Messages](https://platform.claude.com/docs/en/api/messages/create)
- [SDK Python de Anthropic](https://platform.claude.com/docs/en/cli-sdks-libraries/sdks/python)
