# AI Police Lab — brief del proyecto para diseño

> Brief histórico anterior a M3–M5, conservado como referencia de diseño.
> El estado vigente está en [PROJECT_STATUS.md](PROJECT_STATUS.md) y la
> [guía M5](docs/M5_DEMO.md); las fases pendientes descritas aquí ya han avanzado.

Documento de contexto para diseñar la **vista visual de conversación** de cada modelo.
Fuente: el README del proyecto (v0.1) y la identidad visual ya definida.
Lo que no consta en el README está marcado como **[POR CONFIRMAR]**.

---

## 1. Qué es

AI Police Lab es un laboratorio de **simulación híbrida de intervenciones policiales ficticias**.
Varios modelos de IA (hoy OpenAI y Anthropic) actúan como agente policial ante **el mismo caso sintético**, cada uno en una sesión aislada, y se registra todo lo que hacen para poder compararlos.

A medio plazo es un proyecto paraguas: se harán más experimentos de este tipo y se asociarán a trabajo científico (protocolos y artículos).

**Qué no es:** no es un sistema de apoyo policial real ni una evaluación científica validada. Solo casos ficticios y datos sintéticos. No instruye actuaciones policiales reales.

## 2. La idea central

> El motor decide los hechos. El modelo solo propone.

- La **verdad del caso** y el **estado** los conserva un motor determinista, no un LLM.
- El modelo que hace de agente solo **propone acciones**; el motor las valida y devuelve el resultado.
- La respuesta textual de un LLM no produce por sí sola acciones policiales ni altera hechos del mundo.
- Cada agente recibe el mismo caso inicial y ninguna instancia comparte información con otra.
- Todo se registra: decisión, mensaje, latencia, configuración y transición.

## 3. Quién participa en una sesión

| Papel | Quién lo interpreta | Notas |
|---|---|---|
| **Agente** (el policía) | Un modelo de IA por sesión | Es el sujeto del experimento. Ve solo el contexto público. |
| **Personajes A, B y C** (ciudadanos) | Ciudadano **controlado** por catálogo (hoy). Será un LLM en M3 | Cada uno tiene conocimiento permitido propio. C mantiene una declaración prudente. |
| **Motor** | Código determinista | Guarda la verdad privada, valida acciones y registra eventos. No habla como un personaje. |

Los roles de A, B y C dentro del caso (vecino, denunciante, testigo…) salen de `scenarios/PL-001.yaml`. **[POR CONFIRMAR]**

## 4. Qué puede hacer el agente en un turno

Acciones que constan en el README:

- **OBSERVE** — pide una observación del catálogo (ejemplo real: `hallway_sound`). El motor devuelve un hecho verificado.
- **ASK** — pregunta a un personaje. Solo se reconocen preguntas exactas de un catálogo versionado; si no se reconoce, el personaje responde que no lo sabe.
- **SPEAK** — se dirige a un personaje. Hoy devuelve el saludo del personaje.
- **Comprobaciones** y **cierre estructurado** — existen, pero sus nombres de acción exactos están en `schemas/action.schema.json`. **[POR CONFIRMAR]**

Una sesión de la demo: tres entrevistas, comprobaciones y un cierre, en ocho turnos.

## 5. Distinciones que el diseño debe respetar

Son la sustancia del proyecto; si se pierden en la vista, la vista engaña.

1. **Verificado frente a dicho.** Lo que devuelve el motor (observaciones, comprobaciones) es un hecho. Lo que dice un personaje es un testimonio y **no** se añade a lo verificado.
2. **Respuesta de desconocimiento.** Si la pregunta no está en el catálogo, el personaje no sabe. Debe verse como un caso distinto de una respuesta normal.
3. **El motor no es un interlocutor.** Sus resultados no son un bocadillo de persona.
4. **Sesiones independientes.** Dos modelos no conversan entre sí ni ven lo del otro. La comparación real es secuencial.
5. **Ficción visible.** Toda pantalla o captura debe leerse como simulación.
6. **Sin juicio de calidad.** Un cierre normal no indica acierto ni éxito policial. Las reglas sociales (tensión, cooperación) existen en el motor pero no están conectadas: la vista **no mide empatía ni desescalada**.

## 6. Datos disponibles para pintar

Cada sesión escribe una traza JSONL, un evento por línea, en `results/private/<run_id>/`.

Por evento o llamada, según el README: prompt e historial enviado, modelo solicitado y devuelto, versión del SDK, latencia, tokens y errores controlados. El coste es `null`.

Tipos de evento: consta `citizen_utterance` (una intervención de un personaje, que cuenta como un intercambio ASK/SPEAK). El resto de tipos y sus campos. **[POR CONFIRMAR con un JSONL real]**

Resumen de sesión (`summary`): cierre registrado y motivo, número de intercambios, integridad de la traza y revisión humana (pendiente por defecto).

Motivos de cierre que constan: cierre normal, 12 turnos, `provider_error`, `call_limit`, `interrupted`.

Límites por sesión: 16 llamadas, 1500 tokens de salida por llamada, 12 turnos válidos, un reintento.

## 7. Estado del proyecto

| Hito | Contenido | Estado |
|---|---|---|
| M0 | Carga de escenario, validación de acciones, motor determinista | Hecho |
| M1 | CLI, diálogo controlado, exportación JSONL, `demo` y `replay` | Hecho |
| M2 | Adaptadores OpenAI y Anthropic, trazas por evento, manifiestos | Validado con servicios simulados; falta probar con cuentas reales |
| M3 | Ciudadano interpretado por un LLM | Pendiente |
| M4 | **Interfaz visual** | Pendiente — aquí encaja este diseño |

Meta posterior: una arena de cuatro visores.

---

## 8. Encargo de diseño: la vista de conversación

### Objetivo

Ver la interacción de un modelo con las partes implicadas **como una escena**, no como un registro: quién habla, a quién, qué responde, y qué queda establecido como hecho.

### Idea de partida

- **Siluetas** de las partes implicadas (A, B, C) a un lado y la **silueta del agente** al otro.
- **Bocadillos** que van apareciendo turno a turno: lo que dice el agente y lo que le contesta el personaje.
- Se reproduce en el tiempo: avanzar, retroceder, reproducir.

### Cómo se traduce cada cosa de la traza

| En la traza | En la escena |
|---|---|
| `SPEAK` / `ASK` del agente | Bocadillo del agente, apuntando al personaje destinatario |
| `citizen_utterance` | Bocadillo del personaje que responde |
| Respuesta de desconocimiento | Bocadillo del personaje con tratamiento propio (atenuado o con marca) |
| `OBSERVE` y comprobaciones | **No es bocadillo.** Gesto del agente hacia el entorno y una ficha de «hecho verificado» que emite el motor |
| Testimonio | Se queda en el bocadillo; no pasa a la lista de hechos |
| Cierre | Tarjeta final con el motivo de cierre y el resumen de sesión |
| Latencia y tokens | Dato secundario bajo el bocadillo del agente |
| Personaje con el que se habla | Su silueta activa; las otras, atenuadas |

### Elementos de la pantalla

1. **Escena**: siluetas y bocadillos. Es el centro.
2. **Línea de turnos**: 1 a 12, con el turno actual marcado y el tipo de acción.
3. **Hechos verificados**: lista que crece solo con lo que devuelve el motor.
4. **Cabecera de sesión**: modelo, escenario, semilla, contadores (llamadas, turnos, tokens).
5. **Sello de ficción** siempre visible.

### Estados a diseñar

- Antes del primer turno (escena vacía, personajes presentados).
- Agente hablando / esperando respuesta del modelo.
- Personaje respondiendo.
- Respuesta de desconocimiento.
- Observación o comprobación (sin interlocutor).
- Cierre normal.
- Cierre por error de proveedor, límite de llamadas o interrupción.
- Traza incompleta o corrupta (no verificable).
- Comparación: dos sesiones lado a lado, alineadas por turno.

### Reglas para las siluetas

- **Neutras**: sin rasgos de edad, género, etnia ni clase. Son piezas de un caso sintético, no retratos.
- **El agente sin insignias reales**: nada de escudos, placas, uniformes ni emblemas de un cuerpo existente.
- Coherentes con el símbolo: construidas con geometría simple (cuadrados y círculo).
- Los personajes se distinguen por su letra (A, B, C) y posición, no por estereotipo.

## 9. Identidad visual a aplicar

**Símbolo:** cuadrícula 2 × 2 con dos cuadrados en diagonal (el motor), un círculo (el modelo) y una casilla vacía (lo que el agente no ve).

| Color | Hex | Uso |
|---|---|---|
| Cobalto | `#1F3BFF` | Fondo de marca; el modelo sobre fondos claros |
| Reflectante | `#DFFF3D` | Señal: el círculo y la marca de «ficticio» |
| Tinta | `#0B0E1A` | Texto, terminal, base oscura |
| Papel | `#F3F4F6` | Base clara, lectura larga |
| Gris | `#3D4354` | Texto secundario |

**Tipografía:** Archivo ExtraBold al 125 % de ancho para titulares; Archivo Regular y SemiBold para texto; Martian Mono para acciones, identificadores y etiquetas.

**Propuesta de reparto en la escena:** agente en cobalto, personajes en tinta, hechos verificados y sello de ficción en reflectante.

## 10. Para afinar el diseño hace falta

- `scenarios/PL-001.yaml`: quiénes son A, B y C, y el texto del caso.
- `schemas/action.schema.json`: nombres y campos exactos de todas las acciones.
- Un JSONL real de `demo`: tipos de evento y su estructura.
- Decidir si la vista es reproducción de una traza ya grabada o seguimiento en vivo de `run`.
