"""JSONL snapshots and validated chronological replay of a single session."""

import json
import os
from pathlib import Path
from typing import Literal
from collections.abc import Iterable

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .session_manager import Session


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
                  "provider_request", "provider_response", "provider_error"]
    payload: dict


class JsonlEventSink:
    """One session per file; commit each complete event before returning it."""

    def __init__(self, path: Path):
        self._stream = path.open("x", encoding="utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
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
    events = []
    seen = set()
    for line_number, line in enumerate(lines, 1):
        try:
            event = Event.model_validate(json.loads(line)).model_dump()
        except (ValueError, ValidationError) as exc:
            raise ValueError(f"Evento inválido en línea {line_number}") from exc
        if event["seq"] != line_number or event["event_id"] in seen:
            raise ValueError(f"Secuencia inválida en línea {line_number}")
        if events and any(event[key] != events[0][key] for key in ("session_id", "run_id")):
            raise ValueError("El archivo mezcla sesiones o ejecuciones")
        if events and (event["type"] == "session_started" or events[-1]["type"] == "session_closed"):
            raise ValueError("Ciclo de sesión inválido")
        seen.add(event["event_id"])
        events.append(event)
    if not events or events[0]["type"] != "session_started":
        raise ValueError("Falta el inicio de sesión")
    return events
