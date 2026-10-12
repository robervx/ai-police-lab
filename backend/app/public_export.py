"""Versioned public projection exports. These are not private logs or replay inputs."""

import csv
import json
from collections.abc import Iterator
from io import StringIO

EXPORT_VERSION = "arena-public-v2"
FIELDS = ("record_type", "projection_version", "run_id", "participant_id", "session_id",
          "provider", "model_id", "status", "trace_sha256", "scenario_sha256", "source",
          "seq", "turn", "event_type", "payload_json", "conditions_warning")


def records(projection: dict) -> Iterator[dict]:
    base = dict.fromkeys(FIELDS, "")
    base.update(projection_version=EXPORT_VERSION, run_id=projection["run_id"],
                conditions_warning=projection["conditions_warning"])
    yield {**base, "record_type": "run", "payload_json": json.dumps({
        "notice": projection["notice"], "order": projection["order"],
        "scope": "public_projection_not_original_trace", "csv_formula_escape": "leading_apostrophe"},
        ensure_ascii=False)}
    for lane in projection["lanes"]:
        participant = {**base, "participant_id": lane["participant"],
                       "session_id": lane.get("session_id"), "provider": lane.get("provider"),
                       "model_id": lane.get("model"), "status": lane["status"],
                       "trace_sha256": lane.get("trace_sha256"), "source": lane.get("source"),
                       "scenario_sha256": lane.get("scenario_sha256")}
        yield {**participant, "record_type": "participant"}
        for event in lane["events"]:
            yield {**participant, "record_type": "event", "seq": event["seq"], "turn": event["turn"],
                   "event_type": event["type"], "payload_json": json.dumps(event["payload"], ensure_ascii=False)}


def render_export(projection: dict, format: str) -> bytes:
    if format == "jsonl":
        return "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n"
                       for row in records(projection)).encode("utf-8")
    if format != "csv":
        raise ValueError("Unsupported public export format")
    stream = StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=FIELDS)
    writer.writeheader()
    for row in records(projection):
        # Quotes alone do not stop spreadsheet formulas; JSONL remains unmodified.
        safe = {key: "'" + value if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@"))
                else value for key, value in row.items()}
        writer.writerow(safe)
    return stream.getvalue().encode("utf-8")
