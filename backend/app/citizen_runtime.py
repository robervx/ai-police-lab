"""Session-owned citizen runtime. Local or API selector, without conversational memory."""

import json
from collections.abc import Callable
from dataclasses import dataclass, field

from .adapters.base import ProviderConfig
from .citizen import CATALOG, CITIZEN_VERSION, respond
from .citizen_api import ApiSelector, CitizenBudget, api_conditions
from .citizen_contract import (
    CONTRACT_VERSION,
    CitizenContext,
    CitizenRequest,
    prepare_context,
    respond_guarded,
)
from .models import Scenario

CITIZEN_MODES = ("baseline", "guarded-local")
LOCAL_SELECTOR_VERSION = "first-authorized-answer-v1"


class LocalSelector:
    def propose(self, context: CitizenContext, *, repair_code: str | None) -> str:
        return json.dumps({"answer_id": context.allowed_answers[0].answer_id})


@dataclass(frozen=True)
class CitizenRuntime:
    mode: str = "baseline"
    api_config: object = None
    adapter_factory: object = field(default=None, repr=False, compare=False)
    _selectors: dict = field(default_factory=dict, repr=False, compare=False)
    _budget: CitizenBudget = field(default_factory=CitizenBudget, repr=False, compare=False)

    def __post_init__(self) -> None:
        if self.mode not in (*CITIZEN_MODES, "guarded-api"):
            raise ValueError("Unsupported citizen mode")
        if self.mode == "guarded-api":
            if self.api_config is None or self.adapter_factory is None:
                raise ValueError("Citizen API requires config and adapter factory")
            api_conditions(self.api_config)
        if self.mode == "guarded-local":
            self._selectors.update({actor: LocalSelector() for actor in ("A", "B", "C")})

    def validate_scenario(self, scenario: Scenario) -> None:
        if self.mode != "baseline":
            for actor, question in CATALOG:
                prepare_context(scenario, CitizenRequest(action="ASK", target=actor, question=question))

    def metadata(self) -> dict[str, object]:
        if self.mode == "guarded-api":
            assert isinstance(self.api_config, ProviderConfig)  # noqa: S101 — narrowing, ya validado en __post_init__
            return {"citizen_model_id": self.api_config.model_id,
                    "citizen_conditions": api_conditions(self.api_config)}
        if self.mode == "baseline":
            return {"citizen_model_id": CITIZEN_VERSION}
        return {"citizen_model_id": LOCAL_SELECTOR_VERSION, "citizen_conditions": {
            "mode": self.mode, "contract_version": CONTRACT_VERSION,
            "selector_version": LOCAL_SELECTOR_VERSION, "provider": "local",
            "max_attempts_per_request": 2, "memory": "none",
            "selector_scope": "session_actor", "sampling": "deterministic",
        }}

    def reply(
        self, scenario: Scenario, action: dict, *,
        record: Callable[[str, dict[str, object]], object] | None = None,
    ) -> tuple[dict, dict | None]:
        if self.mode == "baseline":
            return respond(scenario, action), None
        target = action["target"]
        if self.mode == "guarded-api" and target not in self._selectors:
            assert isinstance(self.api_config, ProviderConfig) and callable(self.adapter_factory)  # noqa: S101 — narrowing, ya validado en __post_init__
            adapter = self.adapter_factory(self.api_config)
            self._selectors[target] = ApiSelector(adapter, self.api_config, self._budget)
        selector = self._selectors[target]
        if self.mode == "guarded-api":
            selector.record = record
        try:
            result = respond_guarded(scenario, action, selector)
        finally:
            if self.mode == "guarded-api":
                selector.record = None
        diagnostic = {
            "contract_version": CONTRACT_VERSION, "target": action["target"],
            "answer_id": result.answer.answer_id, "fact_ids": list(result.answer.fact_ids),
            "attempts": result.attempts, "fallback_used": result.fallback_used,
            "reason": result.reason, "violations": list(result.violations),
        }
        return {"target": action["target"], **result.public_reply()}, diagnostic
