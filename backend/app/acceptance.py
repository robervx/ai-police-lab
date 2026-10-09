"""Read-only demo evidence; never a score or an automatic human acceptance."""

from datetime import datetime
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .event_store import parse_events


class HumanReview(BaseModel):
    """An external declaration, bound to the exact bytes reviewed, not authentication."""

    model_config = ConfigDict(extra="forbid", strict=True)
    reviewer_type: Literal["human"]
    reviewer: str = Field(min_length=1)
    reviewed_at: str
    notes: str = Field(min_length=1)
    trace_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")

    @field_validator("reviewer", "notes")
    @classmethod
    def nonblank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Required text")
        return value

    @field_validator("reviewed_at")
    @classmethod
    def dated(cls, value: str) -> str:
        if datetime.fromisoformat(value).utcoffset() is None:
            raise ValueError("Timezone required")
        return value


def summarize_trace(path: Path, review_path: Path | None = None) -> dict:
    summary = {
        "trace": str(path), "trace_sha256": None,
        "trace_status": "unreadable", "trace_error": None,
        "session_id": None, "participant_id": None,
        "execution_terminated": None, "closure_reason": None,
        "citizen_exchanges": None, "minimum_exchanges": 3,
        "minimum_exchanges_met": None,
        "human_review": {"status": "pending"},
    }
    try:
        raw = path.read_bytes()
    except OSError:
        summary["trace_error"] = "No se puede leer la traza."
    else:
        summary["trace_sha256"] = sha256(raw).hexdigest()
        try:
            events = parse_events(StringIO(raw.decode("utf-8")))
            closed = events[-1]["type"] == "session_closed"
            reason = events[-1]["payload"].get("reason") if closed else None
            if closed and reason not in (
                "agent_close", "max_turns", "provider_error", "call_limit", "interrupted"
            ):
                raise ValueError("Motivo de cierre ausente o desconocido.")
        except ValueError:
            summary.update(trace_status="invalid", trace_error="Traza inválida o truncada; no se calculan totales.")
        else:
            count = sum(e["type"] == "citizen_utterance" for e in events)
            summary.update(
                trace_status="complete" if closed else "incomplete",
                session_id=events[0]["session_id"],
                participant_id=events[0]["payload"].get("participant_id"),
                execution_terminated=closed, closure_reason=reason,
                citizen_exchanges=count, minimum_exchanges_met=count >= 3,
            )
    if review_path is not None:
        try:
            review = HumanReview.model_validate(json.loads(review_path.read_text(encoding="utf-8")))
            if review.trace_sha256 != summary["trace_sha256"]:
                raise ValueError("Different trace")
        except (OSError, ValueError):
            summary["human_review"] = {
                "status": "invalid", "error": "Registro de revisión inválido, ilegible o de otra traza."
            }
        else:
            summary["human_review"] = {"status": "recorded", **review.model_dump()}
    return summary


def render_summary(summary: dict) -> str:
    def display(value):
        if value is None:
            return "no verificable"
        if isinstance(value, bool):
            return "sí" if value else "no"
        return json.dumps(value, ensure_ascii=False)

    integrity = {"complete": "completa (estructura y secuencia válidas, con cierre)",
                 "incomplete": "incompleta (estructura y secuencia válidas, sin cierre)",
                 "invalid": "inválida o truncada", "unreadable": "no legible"}
    review = summary["human_review"]
    review_status = {"pending": "pendiente", "invalid": "registro no válido",
                     "recorded": "realizada según declaración externa; identidad no autenticada"}
    lines = [
        f"Resumen de sesión — {display(summary['trace'])}",
        f"  Ejecución terminada (cierre registrado): {display(summary['execution_terminated'])}",
        f"  Motivo de cierre: {display(summary['closure_reason'])}",
        f"  Intercambios con ciudadano (ASK/SPEAK): {display(summary['citizen_exchanges'])}",
        f"  Umbral de 3 intercambios alcanzado: {display(summary['minimum_exchanges_met'])}",
        f"  Integridad de traza: {integrity[summary['trace_status']]}",
        f"  Revisión humana: {review_status[review['status']]}",
    ]
    if review["status"] == "recorded":
        lines.extend([f"  Revisor: {display(review['reviewer'])}; fecha: {display(review['reviewed_at'])}",
                      f"  Notas: {display(review['notes'])}"])
    lines.append("  El conteo incluye saludos; no acredita calidad policial ni aceptación del MVP.")
    return "\n".join(lines)
