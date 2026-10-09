# Dirección científica — borrador de protocolo 0.1

Fecha: 2026-10-09 · estado: **propuesta, no preregistro ni estudio ejecutado**.
Prioridad actual: demo funcional para explorar investigación y formación.
Este documento guía decisiones y afirmaciones; no bloquea la demostración técnica.

## Qué podemos afirmar ahora

| Afirmación | Estado y evidencia necesaria |
|---|---|
| El núcleo pasa casos de validación de contratos y aislamiento | Evidencia local en tests; acotada a esos casos |
| Los adaptadores procesan el flujo de ambos SDK | Evidencia HTTP simulada; validación con servicios reales pendiente |
| La demo muestra acciones y testimonios sobre PL-001 | Demostrado con agentes ficticios M1; verificar con proveedores |
| Un modelo es mejor policía, más empático o más legal | No sustentado ni objetivo del MVP vigente |
| La herramienta mejora el aprendizaje humano | No estudiado; requiere diseño formativo distinto |
| Hay un estudio preregistrado o revisión humana independiente | No: solo borrador y revisión asesora IA |

`immediate_threat_confirmed = false` significa que no se ha confirmado la amenaza
en el escenario; no demuestra que toda amenaza sea inexistente. Tensión/cooperación
son reglas de juego, no medidas psicológicas. Un JSON válido, un cierre temprano
o agotar turnos tampoco mide corrección de la actuación.

## Preguntas exploratorias e hipótesis futuras

Ninguna está confirmada. Se seleccionará una pregunta primaria si se decide
investigar formalmente; no se promete una muestra suficiente por defecto.

| ID | Pregunta / hipótesis provisional | Observación propuesta | Límite |
|---|---|---|---|
| Q1 | ¿Se distingue evidencia accesible de testimonios en el cierre? | Sesiones con alguna afirmación incompatible con evidencia visible, según rúbrica humana | Consistencia en PL-001, no veracidad universal |
| Q2 | ¿Se respetan herramientas y contrato? | Sesiones con acciones inválidas; causas y llamadas totales | Error de formato, integración y servicio deben diferenciarse |
| Q3 | ¿Se reconocen incertidumbres específicas? | Reconocimiento correcto de falta de medición y origen incierto de voces | No premiar dudas genéricas ni usar hechos que el modelo no pudo conocer |
| H1 | Cambiar ciudadano controlado por LLM modifica la proporción de sesiones con inconsistencia factual | Futuro diseño por condición de ciudadano y modelo, con rúbrica congelada | Efecto del simulador, no prueba de realismo humano |
| H2 | Paráfrasis previamente declaradas del prompt cambian la distribución de resultados | Bloques modelo × paráfrasis semánticamente equivalentes | No elegir después la formulación que favorezca a una marca |

Las variables y rúbricas anteriores aún no están automatizadas ni validadas.
Fuente conceptual para constructos: [S3](BIBLIOGRAPHY.md#s3).
Sensibilidad al prompt: [S5](BIBLIOGRAPHY.md#s5).

## Diseño propuesto si se activa la vía de investigación

**Objeto:** sistema configurado —modelo, prompt, adaptación, herramientas,
ciudadano y límites—. Las diferencias de integración no deben atribuirse sin más
al modelo aislado. Usar dimensiones separadas y declarar cobertura limitada,
en línea con la orientación de [S1](BIBLIOGRAPHY.md#s1).

**Unidad de análisis:** sesión completa. Los turnos son observaciones dependientes,
no réplicas independientes. Repetir PL-001 permite estudiar variación en PL-001;
no amplía por sí solo la población de situaciones a las que se generaliza.

**Bloques comparables:** todos los participantes bajo la misma versión de escenario,
variante de prompt, condición de ciudadano y política de presupuesto. Alternar
o aleatorizar el orden y registrarlo. La semilla local no controla por igual
generación en APIs externas. Ver [comparabilidad](../governance/COMPARABILITY.md).

**Muestra y parada:** piloto separado para conocer variación, factibilidad y costes;
justificar después número de sesiones por precisión/potencia acorde con la pregunta.
No fijar un número arbitrario como garantía de suficiencia. Congelar regla de
parada y no detenerse cuando aparece el resultado preferido.

**Antes de recoger datos confirmatorios:** fijar pregunta y variable primaria,
secundarias, criterios de inclusión, réplicas, versiones, anotación, exclusiones,
reintentos, análisis y manejo de desviaciones. Si se preregistra, conservar URL/ID,
fecha y versión externa. Un archivo mutable del repositorio no es ese registro.
Separación exploración/confirmación: [S6](BIBLIOGRAPHY.md#s6).

## Fallos, exclusiones y denominadores

Registrar sesiones planificadas, iniciadas, completadas y evaluables. Conservar
todos los intentos y diferenciar indisponibilidad/timeout, rechazo del proveedor,
truncamiento, JSON inválido, acción no permitida, fallo de persistencia y
contaminación del simulador. Definir antes cuáles afectan al comportamiento
estudiado y cuáles impiden interpretarlo.

Un fallo no desaparece porque su exclusión mejora el resultado. Una repetición
debe obedecer una regla previa y enlazar al intento original; no elegir el mejor.
La latencia por llamada, el tiempo total con esperas y el tiempo narrativo son
magnitudes distintas. Menos turnos o más herramientas no tienen un signo de
calidad universal.

## Revisión humana y posible juez LLM

Propuesta para un estudio: rúbrica pilotada con hechos observables; dos revisores
humanos en una muestra predefinida; identidad del proveedor oculta y orden
aleatorio cuando sea viable. Conservar etiquetas originales, desacuerdos y su
resolución; elegir medida de acuerdo según el tipo de escala, no una cifra universal.
El estilo puede hacer imperfecto el cegamiento y debe reconocerse.

Mostrar al evaluador la evidencia que el participante tenía en cada momento.
Si el análisis usa la verdad sintética completa, distinguirla de la información
accesible al modelo para no penalizar desconocimiento legítimo.

Un juez LLM sería auxiliar y requeriría validación local frente a humanos, pruebas
de orden/longitud y sensibilidad a la familia del modelo. No asumir neutralidad
ni transferir cifras de acuerdo de otros benchmarks a PL-001. [S2](BIBLIOGRAPHY.md#s2).

## Reproducción e informe

Preparar manifiesto de código, dependencias, escenario, prompt, ciudadano, modelos,
límites y protocolo; conservar trazas y desviaciones. Es una adaptación al proyecto
de prácticas de documentación de [S4](BIBLIOGRAPHY.md#s4), no garantía de regenerar
salidas idénticas de servicios externos.

Reportar dimensiones por separado, tamaños de efecto e incertidumbre con un
método que conserve los bloques/dependencias del diseño. No sumar a una nota total
sin justificar pesos y significado. Un resultado exploratorio se etiqueta como tal.

## Si se elige formación

Una demo puede apoyar discusión sobre evidencias e incertidumbres. Afirmar mejora
de aprendizaje requeriría objetivos pedagógicos, participantes y evaluación humana,
medición antes/después o comparación apropiada y análisis de transferencia.
El buen desempeño de un modelo no demuestra aprendizaje de una persona.
Ese diseño se decidirá tras LAB-010, fuera del alcance actual.

## Próxima revisión científica

Al cambiar ciudadano, escenario, métricas o condiciones comparativas, revisar
constructo y amenazas a validez. Antes de estudio formal, profundizar la lectura
de las fuentes elegidas y buscar bibliografía específica de la pregunta; el listado
actual es una selección inicial, no una revisión sistemática.
