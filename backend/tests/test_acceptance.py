"""Evidence summaries must not turn completion into acceptance."""

from hashlib import sha256
import json

import pytest

from backend.app.acceptance import summarize_trace, render_summary
from backend.app.cli import main, run_demo
from backend.app.event_store import export_session
from backend.app.rules import RuleEngine
from backend.app.scenario_loader import load_scenario
from backend.app.session_manager import SessionManager

CLOSE = {"action": "CLOSE", "final_decision": "Fin", "actions_taken": [],
         "verified_facts": [], "unverified_claims": [], "remaining_uncertainties": [],
         "justification": "Prueba"}


def trace(tmp_path, exchanges=0, reason="agent_close"):
    scenario, digest = load_scenario()
    session = SessionManager(scenario, digest).create("test")
    engine = RuleEngine()
    engine.start(session)
    for _ in range(exchanges):
        engine.execute(session, {"action": "SPEAK", "target": "A", "message": "Hola"})
    if reason == "agent_close":
        assert engine.execute(session, CLOSE)["ok"]
    elif reason:
        engine.close_technical(session, reason)
    path = tmp_path / "trace.jsonl"
    export_session(session, path)
    return path


@pytest.mark.parametrize("exchanges", [0, 2, 3])
def test_early_closure_is_separate_from_exchange_threshold(tmp_path, exchanges):
    report = summarize_trace(trace(tmp_path, exchanges))
    assert report["execution_terminated"] is True
    assert report["closure_reason"] == "agent_close"
    assert report["trace_status"] == "complete"
    assert report["citizen_exchanges"] == exchanges
    assert report["minimum_exchanges_met"] is (exchanges >= 3)
    assert report["human_review"] == {"status": "pending"}


@pytest.mark.parametrize("reason", ["provider_error", "call_limit", "interrupted"])
def test_technical_closure_does_not_imply_acceptance(tmp_path, reason):
    report = summarize_trace(trace(tmp_path, 3, reason))
    assert report["execution_terminated"] is True
    assert report["closure_reason"] == reason
    assert report["minimum_exchanges_met"] is True
    assert report["human_review"]["status"] == "pending"
    assert "no acredita calidad policial ni aceptación" in render_summary(report)


def test_trace_without_closure_is_incomplete(tmp_path):
    report = summarize_trace(trace(tmp_path, 3, None))
    assert report["trace_status"] == "incomplete"
    assert report["execution_terminated"] is False
    assert report["closure_reason"] is None
    assert report["citizen_exchanges"] == 3


@pytest.mark.parametrize("damage", ["partial_line", "sequence", "empty", "encoding", "closure"])
def test_invalid_trace_has_no_misleading_totals(tmp_path, damage):
    path = trace(tmp_path, 3)
    if damage == "partial_line":
        path.write_bytes(path.read_bytes() + b'{"unfinished":')
    elif damage == "empty":
        path.write_bytes(b"")
    elif damage == "encoding":
        path.write_bytes(b"\xff")
    else:
        events = [json.loads(line) for line in path.read_text().splitlines()]
        if damage == "sequence":
            events[1]["seq"] = 99
        else:
            events[-1]["payload"] = {}
        path.write_text("\n".join(json.dumps(e) for e in events))
    before = path.read_bytes()
    report = summarize_trace(path)
    assert report["trace_status"] == "invalid"
    assert report["execution_terminated"] is None
    assert report["citizen_exchanges"] is None
    assert report["minimum_exchanges_met"] is None
    assert path.read_bytes() == before


def test_missing_file_and_cli_exit_codes(tmp_path, capsys):
    missing = tmp_path / "missing.jsonl"
    assert main(["summary", str(missing), "--json"]) == 1
    assert json.loads(capsys.readouterr().out)["trace_status"] == "unreadable"
    path = trace(tmp_path)
    assert main(["summary", str(path), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["minimum_exchanges_met"] is False
    assert report["human_review"]["status"] == "pending"


def review_file(tmp_path, path, **overrides):
    review = {"reviewer_type": "human", "reviewer": "Revisor de prueba",
              "reviewed_at": "2026-10-10T12:00:00+02:00", "notes": "Registro sintético de prueba.",
              "trace_sha256": sha256(path.read_bytes()).hexdigest(), **overrides}
    target = tmp_path / "review.json"
    target.write_text(json.dumps(review))
    return target


def test_explicit_review_bound_to_exact_bytes(tmp_path, capsys):
    path = trace(tmp_path)
    review = review_file(tmp_path, path)
    before = path.read_bytes()
    assert main(["summary", str(path), "--review", str(review), "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["human_review"]["status"] == "recorded"
    assert report["minimum_exchanges_met"] is False
    assert "identidad no autenticada" in render_summary(report)
    assert path.read_bytes() == before
    path.write_bytes(before + b"\n")
    assert summarize_trace(path, review)["human_review"]["status"] == "invalid"


@pytest.mark.parametrize("overrides", [
    {"trace_sha256": "0" * 64}, {"reviewer_type": "assistant"}, {"reviewer": " "},
    {"reviewed_at": "2026-10-10"}, {"notes": ""}, {"accepted": True},
])
def test_invalid_review_cannot_mark_review_complete(tmp_path, overrides):
    path = trace(tmp_path)
    review = review_file(tmp_path, path, **overrides)
    assert summarize_trace(path, review)["human_review"]["status"] == "invalid"
    assert main(["summary", str(path), "--review", str(review)]) == 1


def test_review_terminal_control_characters_are_escaped(tmp_path):
    path = trace(tmp_path)
    review = review_file(tmp_path, path, reviewer="Name\x1b[2J", notes="Note\nForged line")
    text = render_summary(summarize_trace(path, review))
    assert "\x1b" not in text
    assert "Note\nForged line" not in text


def test_demo_and_replay_show_summary(tmp_path, capsys):
    paths = run_demo(tmp_path)
    assert capsys.readouterr().out.count("Resumen de sesión") == 2
    assert main(["replay", str(paths[0])]) == 0
    assert "Revisión humana: pendiente" in capsys.readouterr().out
