"""Versioned, exact-match dialogue catalog. No model or free-text inference."""

from .models import Scenario

CITIZEN_VERSION = "controlled-citizen-v1"
UNKNOWN = "No tengo información suficiente para responder a esa pregunta."
CATALOG = {
    ("A", "¿Qué ha ocurrido esta noche?"): ("F04", "B y yo hemos tenido una discusión verbal antes de vuestra llegada."),
    ("B", "¿Ha habido música esta noche?"): ("F02", "Sí, esta noche hemos reproducido música en casa."),
    ("B", "¿Quién está en la vivienda?"): ("F01", "Estoy en casa con dos visitas."),
    ("C", "¿Qué ha oído y qué puede confirmar?"): ("F05", "He oído voces fuertes, pero no sé de dónde venían."),
}


def respond(scenario: Scenario, action: dict) -> dict:
    target = action["target"]
    actor = scenario.actors[target]
    fact_ids = []
    if action["action"] == "SPEAK":
        text = actor.greeting
    else:
        entry = CATALOG.get((target, action["question"]))
        if entry and entry[0] in actor.knows:
            fact_ids = [entry[0]]
            text = entry[1]
        else:
            # Preserve the cautious witness response used by M0.
            text = actor.greeting if target == "C" else UNKNOWN
    return {"target": target, "text": text, "source": "testimony",
            "template_version": CITIZEN_VERSION, "fact_ids": fact_ids}
