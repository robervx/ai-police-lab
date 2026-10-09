# Participación y comparabilidad entre modelos

Versión: borrador 0.2 · 2026-10-10 · propietario: sénior IA · revisión: ciencia.
Ámbito: **comparabilidad experimental**, no certificación de equidad social,
legalidad ni capacidad policial real. La demo puede avanzar con limitaciones declaradas.

## Qué se compara hoy

Sistemas configurados sobre PL-001: modelo + adaptador + prompt + herramientas
del simulador + ciudadano controlado + límites. No el «modelo aislado» ni agentes
policiales reales. El motor es la autoridad sobre hechos y transiciones.

| Dimensión | Evidencia actual | Límite o trabajo pendiente |
|---|---|---|
| Aviso y prompt | `Session.public_context()` y `police_instructions()` comunes | Evidencia de igualdad en pruebas HTTP simuladas; comprobar ejecución real |
| Historial y estado | Copias profundas en `SessionManager.create()`; mensajes locales en `run_session()` | No introducir notas de revisión ni información entre participantes |
| Acciones | Un JSON Schema local y mismas reglas | Calidad de JSON no equivale a calidad de decisión |
| Ciudadano | Catálogo publicado sin respuestas; misma función `respond()` | Coincidencia literal: no representa entrevista libre; condición debe identificarse |
| Límites | CLI comparte cifras; `run_comparison()` rechaza diferencias de salida/llamadas/reintentos/timeout antes de ejecutar | Límites nominales no acreditan igual cómputo, coste ni muestreo |
| Muestreo | Registrado como `provider_defaults` | No equivale a ajustes idénticos ni respuesta determinista |
| Orden | OpenAI seguido de Anthropic en CLI | Sin contrabalanceo ni réplicas; posible efecto temporal/servicio |
| Fallos | Peticiones, uso, motivo de fin y errores registrados | Separar servicio, rechazo, truncamiento, formato y cierre deliberado |
| Estados sociales | Reglas con etiquetas revisadas en motor | `run_session()` no proporciona etiquetas; el ciudadano no usa dichos estados |
| Reproducción | Manifiesto de protocolo, hashes de fuentes/escenario/prompt/esquema, entorno instalado y resultados observados vinculados por hash | Restauración local con lock/Python fijados (LAB-007); fuentes en disco no verifican código importado; replay no regenera respuestas |

## Condiciones mínimas de una demo honesta

1. Indicar escenario/ciudadano y mostrar que se trata de simulación ficticia.
2. Mostrar qué se observó, qué declaró cada actor y qué queda desconocido.
3. Conservar fallos y cierres tempranos; no etiquetar el límite de turnos como éxito.
4. Registrar las configuraciones realmente utilizadas y cualquier diferencia.
5. Limitar conclusiones al recorrido demostrado; no anunciar un ganador por
   menos turnos, mayor longitud, menor latencia o más llamadas a herramientas.

## Antes de una comparación formal

Lo siguiente es un criterio para interpretar resultados comparativos, no una
condición para implementar la demo:

- Congelar hipótesis, versiones, rúbrica, políticas de reintento y exclusión.
- Determinar qué presupuesto se iguala: límites nominales, coste, tiempo u otro;
  justificar la decisión y mostrar lo que no queda igualado.
- Validar previamente configs; impedir comparaciones accidentales entre condiciones
  distintas o separarlas explícitamente en el análisis.
- Repetir con bloques emparejados y orden contrabalanceado; registrar todo intento.
- Definir una revisión humana con cegamiento razonable y revisar sus desacuerdos.
- Tratar tiempo por llamada, espera/reintentos y turnos como magnitudes diferentes.
- Evaluar sensibilidad al prompt/ciudadano si las conclusiones dependen de ellos.
- Separar fallos de infraestructura de resultados del comportamiento, sin borrarlos.

## Evidencia por ejecución (automatización parcial)

LAB-003 genera `manifest.json` antes de llamadas y `manifest-outcomes.json` al
finalizar o interrumpir, cuando el disco lo permite. LAB-002 resume intercambios,
cierre, integridad estructural y revisión humana declarada externamente.
Los eventos de errores y reintentos siguen en JSONL; aún no hay informe agregado
de conformidad experimental. Ver [protocolo operativo](../RUN_PROTOCOL.md).

El siguiente esquema sigue siendo una guía para un informe integrado:

```text
run_id / fecha / protocolo / código-entorno / escenario-hash / ciudadano-versión
participantes: proveedor, modelo solicitado y devuelto
prompt-hash / catálogo-esquema / límites / muestreo declarado / orden
intercambios / acciones inválidas / reintentos / respuestas incompletas
traza completa o incompleta / cierre y causa
asimetrías detectadas / revisión realizada / limitaciones
```

Estado global inicial: **apto para seguir desarrollando la demo; neutralidad de
una competición formal no demostrada**. LAB-003 y LAB-007 validados localmente; acciones pendientes: LAB-001, 005, 006 y 011.
La CI remota requiere evidencia separada.
Fundamento metodológico: [bibliografía S1–S5](../research/BIBLIOGRAPHY.md).
