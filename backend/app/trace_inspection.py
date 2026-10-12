"""Read-only diagnosis of one captured byte snapshot, not repair or acceptance."""

import json
from collections.abc import Iterator
from hashlib import sha256
from pathlib import Path
from typing import Literal, TypedDict

from .event_store import iter_events


class InspectionError(TypedDict):
    code: Literal["unreadable", "invalid_utf8", "invalid_structure"]
    line: int | None
    byte_offset: int | None


class InspectionReport(TypedDict):
    trace: str
    trace_sha256: str | None
    snapshot_bytes: int | None
    trace_status: Literal["unreadable", "invalid", "incomplete", "complete"]
    valid_prefix_events: list[dict]
    valid_prefix_bytes: int
    unvalidated_bytes: int | None
    prefix_has_closure: bool
    ends_with_newline: bool | None
    error: InspectionError | None


def inspect_trace(path: Path) -> InspectionReport:
    report: InspectionReport = {
        "trace": str(path), "trace_sha256": None, "snapshot_bytes": None,
        "trace_status": "unreadable", "valid_prefix_events": [],
        "valid_prefix_bytes": 0, "unvalidated_bytes": None,
        "prefix_has_closure": False, "ends_with_newline": None, "error": None,
    }
    try:
        raw = path.read_bytes()
    except OSError:
        report["error"] = {"code": "unreadable", "line": None, "byte_offset": None}
        return report
    report.update({"trace_sha256": sha256(raw).hexdigest(), "snapshot_bytes": len(raw),
                  "ends_with_newline": raw.endswith((b"\n", b"\r"))})
    cursor = {"line": 1, "byte_offset": 0, "end": 0}

    def decoded_lines() -> Iterator[str]:
        for number, line in enumerate(raw.splitlines(keepends=True), 1):
            cursor.update(line=number, byte_offset=cursor["end"], end=cursor["end"] + len(line))
            yield line.decode("utf-8")

    try:
        for event in iter_events(decoded_lines()):
            report["valid_prefix_events"].append(event)
            report["valid_prefix_bytes"] = cursor["end"]
    except (ValueError, UnicodeError) as error:
        report["trace_status"] = "invalid"
        report["error"] = {
            "code": "invalid_utf8" if isinstance(error, UnicodeError) else "invalid_structure",
            "line": cursor["line"], "byte_offset": cursor["byte_offset"],
        }
    else:
        report["trace_status"] = (
            "complete" if report["valid_prefix_events"][-1]["type"] == "session_closed" else "incomplete"
        )
    prefix = report["valid_prefix_events"]
    report["prefix_has_closure"] = bool(prefix and prefix[-1]["type"] == "session_closed")
    report["unvalidated_bytes"] = len(raw) - report["valid_prefix_bytes"]
    return report


def render_inspection(report: InspectionReport) -> str:
    labels = {"complete": "estructura válida con cierre", "incomplete": "estructura válida sin cierre",
              "invalid": "inválida: solo se muestra el prefijo validado", "unreadable": "no legible"}
    lines = [
        f"Inspección de instantánea — {json.dumps(report['trace'], ensure_ascii=False)}",
        f"Estado: {labels[report['trace_status']]}",
        f"SHA256: {report['trace_sha256']}",
        f"Eventos del prefijo: {len(report['valid_prefix_events'])}",
        f"Bytes del prefijo: {report['valid_prefix_bytes']}; sin validar: {report['unvalidated_bytes']}",
    ]
    if report["error"]:
        error = report["error"]
        lines.append(f"Primer error: {error['code']}; línea {error['line']}; offset de byte {error['byte_offset']}")
    if report["ends_with_newline"] is False:
        lines.append("Sin salto de línea final: no implica truncamiento si el evento está completo.")
    lines.append("Solo lectura: no repara, reanuda ni acepta la sesión; no verifica semántica ni autenticidad.")
    return "\n".join(lines)
