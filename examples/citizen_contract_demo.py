"""Run from repository root: python -m examples.citizen_contract_demo. No network."""

import json
from dataclasses import asdict

from backend.app.citizen_contract import respond_guarded
from backend.app.scenario_loader import load_scenario


class LocalSelector:
    def __init__(self, *answer_ids):
        self._answers = iter(answer_ids)

    def propose(self, context, *, repair_code):
        return json.dumps({"answer_id": next(self._answers)})


def main():
    scenario, _ = load_scenario()
    request = {"action": "ASK", "target": "B", "question": "¿Habéis puesto música esta noche?"}
    cases = [
        ("Selección autorizada", LocalSelector("B:F02")),
        ("Desconocimiento autorizado", LocalSelector("unknown")),
        ("Rechazo y regeneración", LocalSelector("B:F01", "B:F02")),
        ("Dos rechazos y fallback", LocalSelector("B:F01", "A:F04")),
    ]
    for label, selector in cases:
        result = respond_guarded(scenario, request, selector)
        diagnostic = asdict(result)
        diagnostic["answer"] = result.answer.model_dump(mode="json")
        print(json.dumps({"case": label, "question": request["question"],
                          "private_diagnostic": diagnostic, "public_reply": result.public_reply()},
                         ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
