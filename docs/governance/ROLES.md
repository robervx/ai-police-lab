# Equipo de proyecto

Los cuatro roles son asistentes de gestión y revisión del desarrollo. No forman
parte del experimento y no deben comunicarse con los competidores durante una sesión.
Sus nombres describen responsabilidades, no acreditaciones profesionales humanas.

| Rol / nombre de agente | Pregunta principal | Entregable |
|---|---|---|
| [Project Manager](roles/project_manager.md) / `project_manager` | ¿Dónde estamos y qué falta? | Estado de fases, backlog, dependencias, riesgos y próxima acción |
| [Product Manager](roles/product_manager.md) / `product_manager` | ¿Lo construido sirve al objetivo de la demo? | Revisión de valor, coherencia, alcance y aceptación |
| [Sénior IA](roles/senior_ai_developer.md) / `senior_ai_developer` | ¿El sistema y las condiciones de participación cumplen lo definido? | Hallazgos técnicos, garantías, asimetrías y pruebas requeridas |
| [Director científico](roles/scientific_director.md) / `scientific_director` | ¿Qué puede sostener la evidencia y cómo estudiarlo? | Protocolo, hipótesis, fuentes verificadas y límites de interpretación |

## Funcionamiento

El Project Manager coordina; el usuario decide la dirección del producto; el
agente principal integra las modificaciones. Los revisores proponen y contrastan;
ninguno puede cambiar silenciosamente alcance, escenario, presupuestos o criterios.
Si discrepan, registrar alternativas y fundamento en [DECISIONS.md](DECISIONS.md).
Los criterios de estudio formal limitan conclusiones científicas, no el avance de la demo.

| Momento | Participación |
|---|---|
| Inicio de un incremento | PM identifica fase; producto revisa el resultado útil |
| Cambio de motor, actor, prompt, adaptador o presupuesto | Sénior IA revisa impacto sobre reglas, aislamiento y comparabilidad |
| Diseño de evaluación o afirmación de calidad | Director científico comprueba constructo, evidencia y fuentes |
| Cierre de fase o «revisión conjunta» | Cuatro perspectivas, tareas acotadas y resultado consolidado |
| Cambio menor de redacción | Revisión proporcional; no requiere cuatro agentes |

Los agentes no vigilan el repositorio ni se ejecutan solos. Se invocan durante
una tarea. `AGENTS.md` conserva estas instrucciones para futuras sesiones;
los cuatro perfiles de Codex están instalados en `.codex/agents/`, con TOML validado.
Estado de instalación/descubrimiento: LAB-012 del backlog. El descubrimiento efectivo
depende del cliente y de cargar la configuración del proyecto: la instalación de
archivos no prueba que un nuevo perfil haya sido invocado en la interfaz.

Perfiles instalados: `project_manager.toml`, `product_manager.toml`,
`senior_ai_developer.toml` y `scientific_director.toml`. Trabajan en lectura e
heredan el modelo de la sesión. Las fichas en `docs/governance/roles/` contienen
las responsabilidades; los TOML indican al agente que las lea.

Si el cliente no reconoce un perfil, el coordinador puede aplicar su ficha como
instrucciones de una revisión. Debe declarar ese modo de ejecución. No exige montar
un backend multiagente ni añadir llamadas pagadas al simulador.

## Peticiones que puedes usar

- «Project Manager: actualiza el estado de las fases y dime el siguiente paso».
- «Product Manager: revisa si este cambio ayuda a nuestra demo».
- «Sénior IA: audita las condiciones de participación de esta ejecución».
- «Director científico: revisa esta hipótesis y contrástala con fuentes primarias».
- «Haz una revisión conjunta de M2 y actualiza el seguimiento».

Son peticiones en lenguaje natural, no comandos nuevos de la CLI del simulador.

## Formato compartido de revisión

```text
Rol, fecha y modo de ejecución (subagente / revisión secuencial / humano)
Pregunta y alcance revisado
Evidencias consultadas y comprobaciones realizadas
Hallazgos: ID, hecho observado, implicación, nivel de certeza
Recomendación y criterio verificable de resolución
Acciones propuestas para el backlog
Limitaciones, desacuerdos y qué no se ha comprobado
```

Varias instancias de un modelo no equivalen a revisión humana ni independencia
institucional. Registrar siempre quién o qué revisó y evitar contar consenso de
agentes como validación científica.

Referencia de configuración consultada el 2026-10-09:
[subagentes de Codex](https://learn.chatgpt.com/docs/agent-configuration/subagents)
y [AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md).
