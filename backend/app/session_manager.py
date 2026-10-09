from copy import deepcopy
from dataclasses import dataclass, field
from uuid import uuid4
from typing import Callable

from .models import Scenario, State


@dataclass
class Session:
    scenario: Scenario
    scenario_sha256: str
    participant_id: str
    run_id: str
    scene_seed: int
    state: State
    model_id: str = "manual-actions-v1"
    prompt_version: str = "manual-v1"
    provider: str = "local"
    max_output_tokens: int | None = None
    max_calls: int | None = None
    max_retries: int = 0
    timeout_seconds: float | None = None
    event_sink: Callable[[dict], None] | None = field(default=None, repr=False)
    redact: Callable = field(default=lambda value: deepcopy(value), repr=False)
    session_id: str = field(default_factory=lambda: str(uuid4()))
    turn: int = 0
    status: str = "active"
    applied_rules: set[str] = field(default_factory=set)
    _events: list[dict] = field(default_factory=list, repr=False)

    @property
    def events(self) -> list[dict]:
        return deepcopy(self._events)

    def public_context(self) -> dict:
        """Explicit allowlist: never serialize the private scenario or state."""
        return {"intro_public": self.scenario.intro_public}


class SessionManager:
    def __init__(self, scenario: Scenario, scenario_sha256: str, scene_seed: int = 0):
        self._scenario = scenario.model_copy(deep=True)
        self._sha = scenario_sha256
        self._seed = scene_seed
        self.run_id = str(uuid4())

    def create(self, participant_id: str, *, model_id: str = "manual-actions-v1",
               prompt_version: str = "manual-v1", provider: str = "local",
               max_output_tokens: int | None = None, max_calls: int | None = None,
               max_retries: int = 0, timeout_seconds: float | None = None,
               event_sink: Callable[[dict], None] | None = None, redact: Callable | None = None) -> Session:
        return Session(
            scenario=self._scenario.model_copy(deep=True),
            scenario_sha256=self._sha,
            participant_id=participant_id,
            run_id=self.run_id,
            scene_seed=self._seed,
            state=self._scenario.initial_state.model_copy(deep=True),
            model_id=model_id,
            prompt_version=prompt_version,
            provider=provider,
            max_output_tokens=max_output_tokens,
            max_calls=max_calls,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            event_sink=event_sink,
            redact=redact or (lambda value: deepcopy(value)),
        )
