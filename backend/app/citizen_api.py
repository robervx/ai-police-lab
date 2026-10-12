"""Stateless citizen selection through the existing provider adapter boundary."""

import json
import re
import time
from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version

from .adapters.base import ProviderError, transport_metadata
from .citizen_contract import CONTRACT_VERSION, CitizenProviderError

CITIZEN_PROMPT_VERSION = "citizen-selection-v1"
INSTRUCTIONS = (
    "Eres un selector de respuestas de un personaje ficticio. El JSON recibido contiene "
    "una pregunta y allowed_answers autorizadas. Devuelve exclusivamente un objeto JSON "
    'con answer_id: {"answer_id":"identificador"}. Selecciona la respuesta pertinente ' 
    "o unknown. No añadas texto ni hechos. repair_code indica un intento anterior inválido."
)


def api_conditions(config):
    if config.max_retries != 0:
        raise ValueError("Citizen retries belong to the contract; set max_retries=0")
    return {"mode": "guarded-api", "contract_version": CONTRACT_VERSION,
            "provider_config": config.model_dump(), "prompt_version": CITIZEN_PROMPT_VERSION,
            "prompt_sha256": sha256(INSTRUCTIONS.encode()).hexdigest(),
            "max_attempts_per_request": 2, "call_budget_scope": "session_all_actors",
            "memory": "none", "sampling": "provider_defaults", "sdk_retries": 0}


@dataclass
class CitizenBudget:
    calls: int = 0


class ApiSelector:
    def __init__(self, adapter, config, budget):
        if adapter.config != config:
            raise ValueError("Citizen adapter config does not match declared conditions")
        self.adapter, self.config, self.budget = adapter, config, budget
        self.record = None

    def propose(self, context, *, repair_code):
        if self.adapter.config != self.config:
            raise RuntimeError("Citizen adapter config changed")
        if self.budget.calls >= self.config.max_calls:
            self.record("citizen_provider_error", {"target": context.actor_id,
                        "code": "call_limit", "network_call": False})
            raise CitizenProviderError()
        self.budget.calls += 1
        call = self.budget.calls
        content = {"context": context.model_dump(mode="json"), "repair_code": repair_code}
        self.record("citizen_provider_request", {
            "call_number": call, "target": context.actor_id,
            "provider": self.config.provider, "model_id": self.config.model_id,
            "prompt_version": CITIZEN_PROMPT_VERSION, "instructions": INSTRUCTIONS,
            "input": content, **transport_metadata(self.config.provider, lookup=version),
        })
        started = time.perf_counter()
        try:
            reply = self.adapter.generate(INSTRUCTIONS, [
                {"role": "user", "content": json.dumps(content, ensure_ascii=False)}])
        except ProviderError as error:
            # The contract retries once; no nested SDK or adapter retries.
            self.record("citizen_provider_error", {
                "call_number": call, "target": context.actor_id,
                "code": (error.code if error.code in {"timeout", "connection_error", "malformed_response"}
                         or re.fullmatch(r"http_[0-9]{3}", error.code) else "provider_error"),
                "network_call": True,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3)})
            raise CitizenProviderError() from None
        self.record("citizen_provider_response", {
            "call_number": call, "target": context.actor_id, "model_id": reply.model_id,
            "response_id": reply.response_id, "usage": reply.usage,
            "completed": reply.completed, "finish_reason": reply.finish_reason,
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
            "estimated_cost_usd": None,
        })
        if not reply.completed:
            raise CitizenProviderError()
        return reply.text
