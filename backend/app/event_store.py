"""JSONL snapshots and validated chronological replay of a single session."""

import json
import os
from collections.abc import Iterable, Iterator
from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from .session_manager import Session


class CitizenDiagnostic(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    contract_version: str
    turn: int = Field(ge=1)
    target: Literal["A", "B", "C"]
    answer_id: str
    fact_ids: list[str]
    attempts: int = Field(ge=0, le=2)
    fallback_used: bool
    reason: Literal["authorized_selection", "attempt_limit", "unrecognized_question",
                    "knowledge_not_allowed", "acknowledgement"]
    violations: list[Literal["invalid_proposal", "unauthorized_answer", "selector_error"]]

    @model_validator(mode="after")
    def consistent_attempts(self) -> Self:
        if self.reason == "authorized_selection":
            valid = (self.attempts >= 1 and not self.fallback_used
                     and len(self.violations) == self.attempts - 1)
        elif self.reason == "attempt_limit":
            valid = self.attempts == 2 and self.fallback_used and len(self.violations) == 2
        else:
            valid = self.attempts == 0 and self.fallback_used and not self.violations
        if not valid:
            raise ValueError("Inconsistent citizen attempt diagnostic")
        return self


class Event(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    event_schema_version: Literal["0.1"]
    event_id: str
    run_id: str
    session_id: str
    seq: int = Field(ge=1)
    timestamp_utc: str
    actor: str
    type: Literal["session_started", "agent_action_requested", "agent_action_rejected",
                  "tool_result", "citizen_utterance", "state_transition", "turn_completed", "session_closed",
                  "provider_request", "provider_response", "provider_error", "citizen_diagnostic",
                  "citizen_provider_request", "citizen_provider_response", "citizen_provider_error"]
    payload: dict

    @model_validator(mode="after")
    def validate_diagnostic(self) -> Self:
        if self.type == "citizen_diagnostic":
            CitizenDiagnostic.model_validate(self.payload)
        return self


class JsonlEventSink:
    """One session per file; commit each complete event before returning it."""

    def __init__(self, path: Path):
        self._stream = path.open("x", encoding="utf-8")

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args: object) -> None:
        self._stream.close()

    def append(self, event: dict) -> None:
        Event.model_validate(event)
        self._stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")
        self._stream.flush()
        os.fsync(self._stream.fileno())


def export_session(session: Session, path: Path) -> None:
    """Exclusive creation: existing traces are never overwritten."""
    with path.open("x", encoding="utf-8") as stream:
        for event in session.events:
            stream.write(json.dumps(event, ensure_ascii=False, allow_nan=False) + "\n")


def read_events(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as stream:
        return parse_events(stream)


def parse_events(lines: Iterable[str]) -> list[dict]:
    """Validate a captured trace using the same rules as chronological replay."""
    return list(iter_events(lines))


def iter_events(lines: Iterable[str]) -> Iterator[dict]:
    """Yield only the contiguous, structurally valid prefix; never skip a bad line."""
    first = None
    previous = None
    seen = set()
    for line_number, line in enumerate(lines, 1):
        try:
            event = Event.model_validate(json.loads(line)).model_dump()
        except (ValueError, ValidationError) as exc:
            raise ValueError(f"Evento inválido en línea {line_number}") from exc
        if event["seq"] != line_number or event["event_id"] in seen:
            raise ValueError(f"Secuencia inválida en línea {line_number}")
        if first is None and event["type"] != "session_started":
            raise ValueError("Falta el inicio de sesión")
        if first and any(event[key] != first[key] for key in ("session_id", "run_id")):
            raise ValueError("El archivo mezcla sesiones o ejecuciones")
        if previous and (event["type"] == "session_started" or previous["type"] == "session_closed"):
            raise ValueError("Ciclo de sesión inválido")
        seen.add(event["event_id"])
        first = first or event
        previous = event
        yield event
    if first is None:
        raise ValueError("Falta el inicio de sesión")
