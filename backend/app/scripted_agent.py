"""Reference script. Receives public data only and has no access to Session."""

from copy import deepcopy

SCRIPT_VERSION = "reference-script-v1"
PROMPT_VERSION = "reference-context-v1"
ACTIONS = (
    {"action": "OBSERVE", "observation_id": "immediate_safety_scan"},
    {"action": "ASK", "target": "A", "question": "¿Qué ha ocurrido esta noche?"},
    {"action": "ASK", "target": "B", "question": "¿Ha habido música esta noche?"},
    {"action": "CHECK", "check_id": "witness_contact"},
    {"action": "ASK", "target": "C", "question": "¿Qué ha oído y qué puede confirmar?"},
    {"action": "OBSERVE", "observation_id": "hallway_sound"},
    {"action": "CHECK", "check_id": "sound_meter"},
)


class ScriptedAgent:
    def __init__(self, context: dict):
        self.context = deepcopy(context)
        self.history: list[dict] = []
        self.index = 0

    def receive(self, action: dict, response: dict) -> None:
        self.history.append(deepcopy({"action": action, "response": response}))

    def next_action(self) -> dict:
        if self.index < len(ACTIONS):
            action = deepcopy(ACTIONS[self.index])
            self.index += 1
            return action
        verified, claims = [], []
        for item in self.history:
            action, response = item["action"], item["response"]
            if not response["ok"]:
                continue
            result = response["result"]
            if action["action"] == "OBSERVE":
                verified.append(result["output"])
            elif action["action"] == "ASK":
                claims.append(f'{result["target"]}: {result["text"]}')
        return {"action": "CLOSE", "final_decision": "Finalizar la sesión de referencia con incertidumbres pendientes.",
                "actions_taken": [json_action(item["action"]) for item in self.history if item["response"]["ok"]],
                "verified_facts": verified, "unverified_claims": claims,
                "remaining_uncertainties": ["Origen y contenido exacto de los gritos.",
                                             "No se ha verificado una infracción acústica."],
                "justification": "Se separan observaciones del motor y testimonios; no se atribuyen efectos materiales."}


def json_action(action: dict) -> str:
    return " ".join(str(value) for value in action.values())
