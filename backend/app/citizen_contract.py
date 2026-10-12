"""Closed answer-selection contract shared by local and API citizen runtimes."""

import json
import unicodedata
from dataclasses import dataclass
from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .citizen import CATALOG, UNKNOWN
from .models import Scenario

CONTRACT_VERSION = "citizen-selector-prototype-v1"
MAX_PROPOSAL_CHARS = 1024
EXPECTED_FACTS = {
    "F01": "En la vivienda B están presentes su residente y dos visitas.",
    "F02": "Se ha reproducido música esa noche en la vivienda B.",
    "F04": "A y B tuvieron una discusión verbal antes de la llegada policial.",
    "F05": "C escuchó voces elevadas sin poder atribuirlas con certeza.",
}
# Exact, reviewed alternatives, not a semantic classifier or substring match.
ALIASES = {
    ("A", "¿Qué ocurrió esta noche?"): "¿Qué ha ocurrido esta noche?",
    ("B", "¿Habéis puesto música esta noche?"): "¿Ha habido música esta noche?",
    ("B", "¿Quién está en casa?"): "¿Quién está en la vivienda?",
    ("C", "¿Qué escuchó y qué puede confirmar?"): "¿Qué ha oído y qué puede confirmar?",
}


class FrozenModel(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True)


class CitizenRequest(FrozenModel):
    action: Literal["ASK", "SPEAK"]
    target: Literal["A", "B", "C"]
    question: str | None = Field(default=None, min_length=1, max_length=1200)
    message: str | None = Field(default=None, min_length=1, max_length=1200)

    @model_validator(mode="after")
    def one_utterance(self) -> Self:
        if self.action == "ASK" and (self.question is None or self.message is not None):
            raise ValueError("ASK requires only question")
        if self.action == "SPEAK" and (self.message is None or self.question is not None):
            raise ValueError("SPEAK requires only message")
        return self


class Answer(FrozenModel):
    answer_id: str
    text: str
    fact_ids: tuple[str, ...] = ()


class CitizenContext(FrozenModel):
    actor_id: Literal["A", "B", "C"]
    question: str
    allowed_answers: tuple[Answer, ...]
    contract_version: str = CONTRACT_VERSION


class Proposal(FrozenModel):
    answer_id: str = Field(min_length=1, max_length=80)


class CitizenProviderError(Exception):
    """Adapter boundary error; its message is never added to diagnostics."""


class CitizenSelector(Protocol):
    def propose(self, context: CitizenContext, *, repair_code: str | None) -> str: ...


@dataclass(frozen=True)
class CitizenResult:
    answer: Answer
    attempts: int
    fallback_used: bool
    reason: str
    violations: tuple[str, ...]

    def public_reply(self) -> dict:
        # Private diagnostics never enter the police model's context.
        return {"text": self.answer.text, "source": "testimony"}


def normalize_question(text: str) -> str:
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def prepare_context(scenario: Scenario, request: CitizenRequest) -> tuple[CitizenContext, str]:
    if scenario.scenario_id != "PL-001" or scenario.scenario_version != "0.1.0":
        raise ValueError("Prototype catalog supports only PL-001 0.1.0")
    unknown = Answer(answer_id="unknown", text=UNKNOWN)
    answers: tuple[Answer, ...] = (unknown,)
    reason = "unrecognized_question"
    canonical = request.question or ""
    if request.action == "SPEAK":
        return CitizenContext(actor_id=request.target, question="", allowed_answers=(
            Answer(answer_id="acknowledge", text="Le escucho."),)), "acknowledgement"
    candidates = {normalize_question(q): q for actor, q in CATALOG if actor == request.target}
    candidates.update({normalize_question(q): original for (actor, q), original in ALIASES.items()
                       if actor == request.target})
    canonical = candidates.get(normalize_question(canonical), "")
    if canonical:
        fact_id, text = CATALOG[(request.target, canonical)]
        if fact_id in scenario.actors[request.target].knows:
            fact = next((f for f in scenario.truth_private.event_facts if f.id == fact_id), None)
            if fact is None or fact.text != EXPECTED_FACTS[fact_id] or fact.type != "synthetic_ground_truth":
                raise ValueError("Scenario fact differs from the reviewed template")
            authorized = Answer(answer_id=f"{request.target}:{fact_id}", text=text, fact_ids=(fact_id,))
            answers = (authorized, unknown)
            reason = "authorized_question"
        else:
            reason = "knowledge_not_allowed"
    # Unknown/injected text is not sent to the selector. Known questions are canonicalized.
    return CitizenContext(actor_id=request.target, question=canonical, allowed_answers=answers), reason


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate JSON field")
        result[key] = value
    return result


def respond_guarded(scenario: Scenario, raw_request: dict, selector: CitizenSelector) -> CitizenResult:
    request = CitizenRequest.model_validate(raw_request)
    context, reason = prepare_context(scenario, request)
    if reason != "authorized_question":
        return CitizenResult(context.allowed_answers[0], 0, True, reason, ())
    allowed = {answer.answer_id: answer for answer in context.allowed_answers}
    violations: list[str] = []
    repair = None
    for attempt in (1, 2):
        try:
            raw = selector.propose(context.model_copy(deep=True), repair_code=repair)
            if not isinstance(raw, str) or len(raw) > MAX_PROPOSAL_CHARS:
                raise ValueError("Proposal exceeds the JSON string contract")
            proposal = Proposal.model_validate(json.loads(raw, object_pairs_hook=_unique_object))
        except CitizenProviderError:
            repair = "selector_error"
        except (ValidationError, ValueError, TypeError, RecursionError):
            repair = "invalid_proposal"
        else:
            if proposal.answer_id in allowed:
                return CitizenResult(allowed[proposal.answer_id], attempt, False,
                                     "authorized_selection", tuple(violations))
            repair = "unauthorized_answer"
        violations.append(repair)
    return CitizenResult(allowed["unknown"], 2, True, "attempt_limit", tuple(violations))
