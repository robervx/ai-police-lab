import json
from hashlib import sha256

import pytest

from backend.app.acceptance import summarize_trace
from backend.app.cli import main
from backend.app.event_store import read_events
from backend.app.trace_inspection import inspect_trace


def event(seq, kind):
    return {"event_schema_version": "0.1", "event_id": f"e{seq}", "run_id": "run",
            "session_id": "session", "seq": seq, "timestamp_utc": "2026-10-10T12:00:00Z",
            "actor": "engine", "type": kind, "payload": {}}


def encoded(value):
    return (json.dumps(value, ensure_ascii=False) + "\n").encode()


@pytest.mark.parametrize("suffix", [b'{"cut":', b'\xff', b'{"text":"\xc3', b'\n'])
def test_first_bad_line_stops_inspection_and_preserves_bytes(tmp_path, suffix):
    path = tmp_path / "trace.jsonl"
    start = encoded(event(1, "session_started"))
    raw = start + suffix + b"\n" + encoded(event(3, "session_closed"))
    path.write_bytes(raw)
    report = inspect_trace(path)
    assert report["trace_status"] == "invalid"
    assert report["valid_prefix_events"] == [event(1, "session_started")]
    assert report["valid_prefix_bytes"] == len(start)
    assert report["unvalidated_bytes"] == len(raw) - len(start)
    assert report["error"]["line"] == 2
    assert report["error"]["byte_offset"] == len(start)
    assert report["trace_sha256"] == sha256(raw).hexdigest()
    assert path.read_bytes() == raw
    assert summarize_trace(path)["citizen_exchanges"] is None
    with pytest.raises(ValueError):
        read_events(path)


@pytest.mark.parametrize("mutation", ["seq", "duplicate", "session", "run", "restart"])
def test_semantically_structural_errors_match_strict_reader(tmp_path, mutation):
    first, second = event(1, "session_started"), event(2, "tool_result")
    if mutation == "seq":
        second["seq"] = 3
    elif mutation == "duplicate":
        second["event_id"] = first["event_id"]
    elif mutation == "session":
        second["session_id"] = "other"
    elif mutation == "run":
        second["run_id"] = "other"
    else:
        second["type"] = "session_started"
    path = tmp_path / "trace.jsonl"
    path.write_bytes(encoded(first) + encoded(second))
    assert inspect_trace(path)["valid_prefix_events"] == [first]
    with pytest.raises(ValueError):
        read_events(path)


@pytest.mark.parametrize("newline", [True, False])
@pytest.mark.parametrize("closed", [True, False])
@pytest.mark.parametrize("separator", [b"\n", b"\r\n", b"\r"])
def test_valid_snapshots_match_replay(tmp_path, newline, closed, separator):
    path = tmp_path / "trace.jsonl"
    raw = encoded(event(1, "session_started"))
    if closed:
        raw += encoded(event(2, "session_closed"))
    if not newline:
        raw = raw[:-1]
    raw = raw.replace(b"\n", separator)
    path.write_bytes(raw)
    report = inspect_trace(path)
    assert report["valid_prefix_events"] == read_events(path)
    assert report["trace_status"] == ("complete" if closed else "incomplete")
    assert report["ends_with_newline"] == newline
    assert report["unvalidated_bytes"] == 0
    # Structural inspection does not validate closure reason or acceptance.
    if closed:
        assert summarize_trace(path)["trace_status"] == "invalid"


def test_closed_prefix_does_not_make_corrupt_file_complete(tmp_path):
    path = tmp_path / "trace.jsonl"
    path.write_bytes(encoded(event(1, "session_started")) + encoded(event(2, "session_closed")) + b"garbage")
    report = inspect_trace(path)
    assert report["trace_status"] == "invalid"
    assert report["prefix_has_closure"]
    assert len(report["valid_prefix_events"]) == 2


@pytest.mark.parametrize("raw", [b"", encoded(event(1, "tool_result"))])
def test_empty_or_missing_start(tmp_path, raw):
    path = tmp_path / "trace.jsonl"
    path.write_bytes(raw)
    report = inspect_trace(path)
    assert report["trace_status"] == "invalid"
    assert report["valid_prefix_events"] == []
    assert report["error"] == {"code": "invalid_structure", "line": 1, "byte_offset": 0}


def test_cli_readonly_and_error_output_escaping(tmp_path, capsys):
    path = tmp_path / "trace.jsonl"
    first = event(1, "session_started")
    first["payload"] = {"text": "\x1b[31m"}
    raw = encoded(first) + b"raw-private-invalid-line"
    path.write_bytes(raw)
    assert main(["inspect", str(path)]) == 1
    output = capsys.readouterr().out
    assert "\x1b" not in output and "raw-private-invalid-line" not in output
    assert "Solo lectura" in output
    assert path.read_bytes() == raw
    assert main(["inspect", str(path), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["valid_prefix_bytes"] == len(encoded(first))


def test_missing_file(tmp_path, capsys):
    path = tmp_path / "absent"
    report = inspect_trace(path)
    assert report["trace_status"] == "unreadable"
    assert report["trace_sha256"] is None
    assert main(["inspect", str(path)]) == 1
    capsys.readouterr()
    assert not path.exists()
