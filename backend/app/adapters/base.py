"""The simulator speaks this small contract, independent of any provider SDK."""

import platform
import re
from collections.abc import Callable
from dataclasses import dataclass
from importlib.metadata import version
from typing import Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True, hide_input_in_errors=True)
    provider: Literal["openai", "anthropic", "gemini", "ollama"]
    model_id: str = Field(min_length=1, pattern=r"^\S+$")
    max_output_tokens: int = Field(default=1500, ge=128, le=8192)
    timeout_seconds: float = Field(default=30.0, gt=0, le=60)
    max_calls: int = Field(default=16, ge=1, le=40)
    max_retries: int = Field(default=1, ge=0, le=2)

    @model_validator(mode="after")
    def provider_model(self) -> Self:
        if self.provider == "gemini" and not re.fullmatch(r"[a-zA-Z0-9._-]+", self.model_id):
            raise ValueError("Gemini requires a model ID without models/ prefix")
        return self


@dataclass(frozen=True)
class ModelReply:
    text: str
    model_id: str | None
    response_id: str | None
    usage: dict
    completed: bool
    finish_reason: str


class ProviderError(Exception):
    """Only safe, controlled codes; never persist exception bodies or headers."""

    def __init__(self, code: str, *, recoverable: bool = False):
        super().__init__(code)
        self.code = code
        self.recoverable = recoverable


class PoliceModelAdapter(Protocol):
    config: ProviderConfig

    def generate(self, instructions: str, messages: list[dict]) -> ModelReply: ...

    def close(self) -> None: ...


def transport_metadata(
    provider: str, *, lookup: Callable[[str], str] = version
) -> dict[str, str | None]:
    if provider in {"openai", "anthropic"}:
        return {"transport": "provider_sdk", "sdk_version": lookup(provider)}
    return {"transport": "python_urllib", "sdk_version": None,
            "transport_version": platform.python_version()}
