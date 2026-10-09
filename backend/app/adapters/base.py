"""The simulator speaks this small contract, independent of any provider SDK."""

from dataclasses import dataclass
from typing import Literal, Protocol

from pydantic import BaseModel, ConfigDict, Field


class ProviderConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True, strict=True)
    provider: Literal["openai", "anthropic"]
    model_id: str = Field(min_length=1, pattern=r"^\S+$")
    max_output_tokens: int = Field(default=1500, ge=128, le=8192)
    timeout_seconds: float = Field(default=30.0, gt=0, le=60)
    max_calls: int = Field(default=16, ge=1, le=40)
    max_retries: int = Field(default=1, ge=0, le=2)


@dataclass(frozen=True)
class ModelReply:
    text: str
    model_id: str
    response_id: str
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
