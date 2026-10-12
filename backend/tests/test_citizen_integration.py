import json

import pytest

from backend.app.acceptance import summarize_trace
from backend.app.citizen_contract import CitizenProviderError
from backend.app.citizen_runtime import LOCAL_SELECTOR_VERSION
from backend.app.cli import main, run_demo
from backend.app.event_store import JsonlEventSink, parse_events, read_events
from backend.app.rules import RuleEngine
from backend.app.scenario_loader import load_scenario
from backend.app.session_manager import SessionManager


def manager():
    scenario, digest = load_scenario()
    return SessionManager(scenario, digest, citizen_mode="guarded-local")


def ask(target="B", question="¿Habéis puesto música esta noche?"):
    return {"action": "ASK", "target": target, "question": question}


def test_guarded_demo_records_equal_conditions_and_replays(tmp_path, capsys):
    paths = run_demo(tmp_path, citizen_mode="guarded-local")
    traces = [read_events(p) for p in paths]
    assert traces[0][0]["session_id"] != traces[1][0]["session_id"]
    assert traces[0][0]["payload"]["citizen_conditions"] == traces[1][0]["payload"]["citizen_conditions"]
    for path, events in zip(paths, traces, strict=True):
        assert events[0]["payload"]["citizen_model_id"] == LOCAL_SELECTOR_VERSION
        diagnostics = [e for e in events if e["type"] == "citizen_diagnostic"]
        assert [e["payload"]["turn"] for e in diagnostics] == [2, 3, 5]
        assert all(e["payload"]["attempts"] == 1 for e in diagnostics)
        assert summarize_trace(path)["citizen_exchanges"] == 3
        assert summarize_trace(path)["trace_status"] == "complete"
        assert main(["replay", str(path)]) == 0
    capsys.readouterr()


def test_instances_are_separate_for_every_actor_and_session():
    pool = manager()
    one, two = pool.create("one"), pool.create("two")
    selectors = [s for session in (one, two) for s in session.citizen._selectors.values()]
    assert len({id(s) for s in selectors}) == 6
    # A deliberately stateful substitute proves only the addressed instance is used.
    class Remembering:
        def __init__(self):
            self.history = []

        def propose(self, context, *, repair_code):
            self.history.append(context)
            return json.dumps({"answer_id": context.allowed_answers[0].answer_id})

    for session in (one, two):
        session.citizen._selectors.update({a: Remembering() for a in ("A", "B", "C")})
    engine = RuleEngine()
    response = engine.execute(one, ask())
    assert len(one.citizen._selectors["B"].history) == 1
    assert not one.citizen._selectors["A"].history
    assert not any(s.history for s in two.citizen._selectors.values())
    assert two.events == [] and two.turn == 0
    assert one.state.public_evidence == []
    assert set(response["result"]) == {"target", "text", "source"}
    assert "fact_ids" not in json.dumps(response) and "violations" not in json.dumps(response)


@pytest.mark.parametrize("recover", [True, False])
def test_rejections_are_private_and_persisted(tmp_path, recover):
    class Faulty:
        calls = 0

        def propose(self, context, *, repair_code):
            self.calls += 1
            if recover and self.calls == 2:
                return '{"answer_id":"B:F02"}'
            raise CitizenProviderError("secret-error-body")

    path = tmp_path / "session.jsonl"
    with JsonlEventSink(path) as sink:
        session = manager().create("one", event_sink=sink.append)
        session.citizen._selectors["B"] = Faulty()
        response = RuleEngine().execute(session, ask())
    events = read_events(path)
    diagnostic = next(e["payload"] for e in events if e["type"] == "citizen_diagnostic")
    assert diagnostic["attempts"] == 2
    assert diagnostic["fallback_used"] is not recover
    assert diagnostic["violations"] == ["selector_error"] * (1 if recover else 2)
    assert "secret-error-body" not in path.read_text()
    assert "answer_id" not in json.dumps(response)
    assert summarize_trace(path)["citizen_exchanges"] == 1


def test_unknown_and_speak_bypass_selector_and_rejected_action_has_no_diagnostic():
    session = manager().create("one")
    engine = RuleEngine()
    assert not engine.execute(session, {**ask(), "extra": "bad"})["ok"]
    assert not any(e["type"] == "citizen_diagnostic" for e in session.events)
    engine.execute(session, ask(question="¿Quién amenazó a quién?"))
    engine.execute(session, {"action": "SPEAK", "target": "C", "message": "Hola"})
    diagnostics = [e["payload"] for e in session.events if e["type"] == "citizen_diagnostic"]
    assert [d["attempts"] for d in diagnostics] == [0, 0]
    assert [d["reason"] for d in diagnostics] == ["unrecognized_question", "acknowledgement"]


def test_unexpected_error_preserves_demo_prefix(tmp_path, monkeypatch):
    from backend.app.citizen_runtime import LocalSelector

    def fail(*args, **kwargs):
        raise RuntimeError("programming error")

    monkeypatch.setattr(LocalSelector, "propose", fail)
    with pytest.raises(RuntimeError):
        run_demo(tmp_path, citizen_mode="guarded-local")
    paths = list(tmp_path.glob("*/*.jsonl"))
    assert len(paths) == 1
    assert read_events(paths[0])[-1]["type"] == "agent_action_requested"
    assert summarize_trace(paths[0])["trace_status"] == "incomplete"


def test_unsupported_mode_and_scenario_fail_before_output(tmp_path):
    with pytest.raises(ValueError):
        run_demo(tmp_path, citizen_mode="not-a-mode")
    assert not list(tmp_path.iterdir())
    scenario, digest = load_scenario()
    scenario.scenario_version = "0.2.0"
    with pytest.raises(ValueError):
        SessionManager(scenario, digest, citizen_mode="guarded-local")


def test_cli_guarded_option(tmp_path, capsys):
    assert main(["demo", "--citizen-mode", "guarded-local", "--output", str(tmp_path)]) == 0
    assert "citizen_diagnostic" in capsys.readouterr().out


@pytest.mark.parametrize("field,value", [("attempts", 3), ("violations", ["secret"]),
                                       ("fallback_used", True), ("turn", 0)])
def test_replay_rejects_malformed_diagnostic(field, value):
    session = manager().create("one")
    RuleEngine().execute(session, ask())
    events = session.events
    diagnostic = next(e for e in events if e["type"] == "citizen_diagnostic")
    diagnostic["payload"][field] = value
    with pytest.raises(ValueError):
        parse_events(json.dumps(e) for e in events)
