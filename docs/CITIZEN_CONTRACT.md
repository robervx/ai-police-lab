# Contrato ciudadano: prototipo local LAB-004

Versión `citizen-selector-prototype-v1`, solo PL-001 0.1.0. LAB-015 conecta el
contrato a motor y `demo --citizen-mode guarded-local`, con selector local.
LAB-016 añade `run --citizen-provider ... --citizen-model ...` y manifiestos
ciudadanos; [API y límites](CITIZEN_API.md). El modo predeterminado conserva M2.

## 1. Entrada y contexto permitido

En [citizen_contract.py](../backend/app/citizen_contract.py), `CitizenRequest`
acepta ASK con pregunta o SPEAK con mensaje, target A/B/C y ningún campo extra.
`prepare_context()` autoriza conjuntamente actor, pregunta reconocida y `knows`.
Comprueba el texto/tipo del hecho usado antes de reutilizar su plantilla; rechaza
otra versión del escenario. No modifica hechos ni estado del escenario.

Se normalizan Unicode NFC, mayúsculas y espacios; no se eliminan signos ni se
buscan coincidencias parciales. Las únicas reformulaciones adicionales son:

| Actor | Alias | Pregunta del catálogo |
|---|---|---|
| A | ¿Qué ocurrió esta noche? | ¿Qué ha ocurrido esta noche? |
| B | ¿Habéis puesto música esta noche? | ¿Ha habido música esta noche? |
| B | ¿Quién está en casa? | ¿Quién está en la vivienda? |
| C | ¿Qué escuchó y qué puede confirmar? | ¿Qué ha oído y qué puede confirmar? |

El selector recibe una copia de contexto inmutable con actor, pregunta canónica,
versión y respuestas permitidas para esa pregunta. No recibe el escenario completo,
verdad oculta, otros participantes, notas de revisión ni pregunta desconocida en bruto.

## 2. Propuesta y validación

El selector solo puede devolver un objeto JSON como:

```json
{"answer_id": "B:F02"}
```

La propuesta admite hasta 1024 caracteres. `Proposal` rechaza campos extra,
claves duplicadas, tipos incorrectos y Markdown; se controlan errores de
anidamiento del parser.
El servidor verifica el ID contra las opciones capturadas y devuelve su plantilla;
no acepta prosa generada. Conocer F01 no autoriza a B a seleccionarlo al preguntarle
por música (F02). `unknown` también es una selección permitida.

Esto controla selección dentro de un catálogo cerrado; no detecta contradicciones
en lenguaje libre. Ampliar a prosa generada exige otro contrato y validación.

## 3. Segundo intento y salida pública

`respond_guarded()` realiza como máximo dos llamadas. En la segunda facilita el
mismo contexto y un código: `invalid_proposal`, `unauthorized_answer` o
`selector_error`. No reenvía el contenido rechazado ni el cuerpo de errores.
Los adaptadores deben convertir sus fallos esperados a `CitizenProviderError`;
LAB-016 aporta adaptador de red, timeout y presupuesto ciudadano por sesión.

Después de dos rechazos devuelve desconocimiento. Las preguntas desconocidas o
sin conocimiento permitido no llaman al selector. SPEAK responde «Le escucho.».
En este prototipo `fallback_used` indica la salida determinista alternativa,
incluido SPEAK; `reason` permite distinguir esos casos de `attempt_limit`.

```python
def public_reply(self):
    return {"text": self.answer.text, "source": "testimony"}
```

Intentos, IDs, hechos y códigos quedan en `CitizenResult`, fuera de esa salida.
El componente devuelve diagnósticos en memoria; el modo integrado LAB-015 los
persiste como eventos privados `citizen_diagnostic`. Un testimonio
no se convierte en observación verificada. `unknown` seleccionado válidamente tiene
`fallback_used=False`: ausencia de fallback no implica información pertinente.

## 4. Ver y ejecutar el código

1. [Contrato y guardas](../backend/app/citizen_contract.py): entrada → contexto → propuesta → resultado.
2. [Ejemplo local](../examples/citizen_contract_demo.py): cuatro secuencias prefijadas.
3. [Pruebas](../backend/tests/test_citizen_contract.py): aliases, propuestas adversariales,
   hechos alterados, aislamiento de snapshots y conservación de la referencia M1.

```sh
.venv/bin/python -m examples.citizen_contract_demo
.venv/bin/python -m pytest -q --tb=short
```

El ejemplo muestra por separado diagnóstico privado y respuesta pública para
desarrollo; su salida completa no debe enviarse al participante. Resultados:

| Caso | Intentos | Fallback | Resultado |
|---|---:|---|---|
| ID autorizado B:F02 | 1 | No | Testimonio sobre música |
| ID autorizado unknown | 1 | No | Desconocimiento elegido |
| B:F01 rechazado, B:F02 válido | 2 | No | Testimonio; un rechazo conservado |
| B:F01 y A:F04 rechazados | 2 | Sí | Desconocimiento; dos rechazos conservados |

## Límites y siguientes incrementos

El prototipo no tiene historial conversacional ni memoria entre solicitudes.
Cada llamada captura opciones nuevas; la instancia del selector la proporciona
quien llama. En LAB-015, `SessionManager` crea un runtime propio por sesión y un
selector propio por actor; el selector local no mantiene memoria.
No interpreta tensión/cooperación ni mide empatía o efectos de desescalada.

La referencia [citizen.py](../backend/app/citizen.py) permanece vigente en M1/M2.
En ella C conserva su saludo ante preguntas desconocidas; el prototipo utiliza
desconocimiento genérico y SPEAK neutro. Es una diferencia explícita de modo,
no un cambio silencioso del escenario ni del contrato ejecutado por `run`.

[LAB-015](governance/BACKLOG.md#lab-015) integra el modo local versionado, separación
por sesión/actor, eventos privados y condiciones previas para ambos participantes.
[Guía del recorrido integrado](CITIZEN_INTEGRATION.md). LAB-016 incorpora adaptador ciudadano API y manifiestos ampliados, probados con
HTTP simulado; falta piloto real LAB-017. Este
prototipo refina la implementación por etapas del [contrato previsto](SIMULATOR_CONTRACT.md),
sin completar sus capacidades. M2/M3 siguen pendientes de piloto real; el selector API y el visor M4 tienen
validación local.

El constructo observable es cumplimiento de selección cerrada por solicitud,
con sus intentos y resultado. No acredita realismo humano, comprensión semántica,
neutralidad comparativa ni prevención general de alucinaciones. La evidencia es
local con selectores simulados; no se presentan hipótesis como resultados científicos.
