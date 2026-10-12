"""Public participant identities and bounded CLI roster; no secrets or endpoints."""

import json
import re
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from .adapters.base import ProviderConfig

ID_PATTERN = r"^[a-zA-Z0-9][a-zA-Z0-9_-]{0,47}$"


class Participant(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True, frozen=True, hide_input_in_errors=True)
    id: str = Field(pattern=ID_PATTERN)
    provider: Literal["openai", "anthropic", "gemini", "ollama"]
    model_id: str


def participant_ids(configs: list[ProviderConfig], ids: list[str] | None = None) -> list[str]:
    result = list(ids) if ids is not None else [f"p{i:02d}-{c.provider}" for i, c in enumerate(configs, 1)]
    if (len(result) != len(configs)
            or any(not isinstance(x, str) or not re.fullmatch(ID_PATTERN, x) for x in result)
            or len(set(result)) != len(result)):
        raise ValueError("Participant IDs must be unique safe identifiers, one per config")
    return result


def load_participants(path: Path, **limits: int | float) -> tuple[list[ProviderConfig], list[str]]:
    if path.stat().st_size > 64_000:
        raise ValueError("Participant config too large")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or len(data) not in (2, 4):
        raise ValueError("Participant config must contain 2 or 4 entries")
    people = [Participant.model_validate(item) for item in data]
    # El plugin de mypy para Pydantic no reparte por nombre un **kwargs de valor
    # uniforme contra un constructor con campos de tipos distintos; limits siempre
    # trae las cuatro claves nominales reales (max_output_tokens, max_calls,
    # max_retries, timeout_seconds), nunca posicionales.
    configs = [ProviderConfig(provider=p.provider, model_id=p.model_id, **limits)  # type: ignore[arg-type]
              for p in people]
    ids = participant_ids(configs, [p.id for p in people])
    return configs, ids
