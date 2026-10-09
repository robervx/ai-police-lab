# Empezar en VS Code — AI Police Lab

## 0. Preparación
1. Abrir esta carpeta con VS Code. Para el entorno reproducible M2, seguir [DEVELOPMENT.md](DEVELOPMENT.md); Node.js se necesitará al abordar la interfaz.
2. Para APIs reales, copiar `.env.example` a `.env` y completar `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_MODEL_ID` y `ANTHROPIC_MODEL_ID`. La demo local y los tests no requieren claves.
3. Añadir `.gitignore` con `.env`, `*.db`, `.venv/`, `node_modules/`, `results/private/`.
4. Conservar `scenarios/PL-001.yaml` y `schemas/action.schema.json` versionados.

## 1. Prompt para el asistente de programación (Codex / Claude Code)
El prompt siguiente describe el arranque original. M0 y M1 ya están implementados.
M2 tiene adaptadores, CLI y pruebas HTTP simuladas; falta validarlo con cuentas y
modelos reales. Consultar README.md y CHANGELOG.md para ejecutarlos, y
[M2_CODE_TOUR.md](M2_CODE_TOUR.md) para recorrer el código por bloques.

> Construye AI Police Lab MVP v0.1 conforme a README.md, docs/PROJECT_SPEC.md, scenarios/PL-001.yaml, schemas/action.schema.json y docs/SIMULATOR_CONTRACT.md. Comienza SOLO por M0: loader del YAML, Pydantic para validación, sesiones clonadas, motor determinista y pytest para los tests de tests/ACCEPTANCE.md. No desarrolles frontend ni conectes APIs hasta que los tests pasen. No cambies la verdad del escenario sin registrar cambio de versión y justificarlo. No simules resultados policiales o jurídicos no definidos. Las claves van en .env excluido de Git. Devuelve tests ejecutados, limitaciones y archivos modificados.

## 2. Estructura futura sugerida
`backend/app/{main.py,scenario_loader.py,session_manager.py,rules.py,event_store.py,models.py,adapters/}`
`backend/tests/`
`frontend/src/{Arena.tsx,components/Timeline.tsx,components/ModelLane.tsx}`

## 3. Secuencia de desarrollo
**Primera sesión (M0):** validación de escenario, RuleEngine y tests de seguridad/consistencia.
**Segunda (M1):** interfaz CLI con dos agentes ficticios para probar conversaciones y export JSONL.
**Tercera (M2):** OpenAI/Anthropic API; `model_id` configurable y logs de llamadas; comparar el mismo escenario.
**Cuarta (M3):** actor LLM, filtrado/plantillas de hechos y fallback.
**Quinta (M4):** frontend 2 carriles con replay; después cuatro carriles.

## 4. Decisiones pendientes que no bloquean M0
- Versión exacta de los modelos y coste por token.
- Proveedor del ciudadano LLM y forma de validar sus respuestas.
- Versión normativa específica a aplicar para futura evaluación jurídica por expertos.
- Rúbrica científica e interevaluadores.

## Definition of Done
No llamar 'implementado' a un componente por existir su archivo. Requiere ejecución funcional, pruebas y evidencia de qué pasó. Registrar desviaciones en CHANGELOG.md.
