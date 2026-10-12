import json

import pytest

from backend.app.adapters.base import ProviderConfig
from backend.app.cli import main
from backend.app.rules import RuleEngine
from backend.app.scenario_loader import load_scenario
from backend.app.session_manager import SessionManager
from backend.tests import test_m2 as sdk_tests
from backend.tests.test_m2 import CLOSE, response_body

adapter_factory = sdk_tests.adapter_factory


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_citizen_real_sdk_mock_transport_isolated_and_bounded(provider, adapter_factory):
    config = ProviderConfig(provider=provider, model_id="requested-test-model", max_retries=0, max_calls=2)
    captures = []

    def factory(expected):
        adapter, requests = adapter_factory(provider, [
            response_body(provider, '{"answer_id":"B:F01","secret":"NEVER_FORWARD"}'),
            response_body(provider, '{"answer_id":"B:F02"}')], max_retries=0, max_calls=2)
        captures.append(requests)
        assert adapter.config == expected
        return adapter

    scenario, digest = load_scenario()
    manager = SessionManager(scenario, digest, citizen_mode="guarded-api",
                             citizen_config=config, citizen_factory=factory)
    one, two = manager.create("one"), manager.create("two")
    engine = RuleEngine()
    question = {"action": "ASK", "target": "B", "question": "¿Ha habido música esta noche?"}
    result = engine.execute(one, question)
    assert set(result["result"]) == {"target", "source", "text"}
    assert "NEVER_FORWARD" not in json.dumps(captures) + json.dumps(one.events)
    assert len(captures[0]) == 2
    assert len(captures[0][1]["input" if provider == "openai" else "messages"]) == 1
    engine.execute(one, {"action": "ASK", "target": "A", "question": "¿Qué ha ocurrido esta noche?"})
    assert captures[1] == []  # A shares B's exhausted budget.
    engine.execute(two, question)
    assert len(captures[2]) == 2 and two.citizen._budget.calls == 2
    assert one.citizen._budget.calls == 2
    assert any(e["payload"].get("code") == "call_limit" for e in one.events)


@pytest.mark.parametrize("outcome", ["timeout", "incomplete"])
def test_api_failure_falls_back_without_error_body(outcome, adapter_factory):
    config = ProviderConfig(provider="openai", model_id="requested-test-model", max_retries=0)
    response = "timeout" if outcome == "timeout" else response_body("openai", '{"answer_id":"B:F02"}', False)
    def factory(config):
        return adapter_factory("openai", [response, response], max_retries=0)[0]
    scenario, digest = load_scenario()
    session = SessionManager(scenario, digest, citizen_mode="guarded-api", citizen_config=config,
                             citizen_factory=factory).create("one")
    RuleEngine().execute(session, {"action": "ASK", "target": "B", "question": "¿Ha habido música esta noche?"})
    diag = next(e["payload"] for e in session.events if e["type"] == "citizen_diagnostic")
    assert diag["fallback_used"] and diag["attempts"] == 2
    assert "sk-test-secret" not in json.dumps(session.events)


def test_citizen_dry_run_records_config_without_keys(tmp_path, capsys):
    assert main(["run", "--openai-model", "example-a", "--anthropic-model", "example-b",
                 "--citizen-provider", "openai", "--citizen-model", "example-c",
                 "--dry-run", "--output", str(tmp_path)]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["network_calls"] == 0
    assert data["manifest"]["citizen"]["memory"] == "none"
    assert data["manifest"]["protocol"]["version"] == "demo-m3-selector-v1"
    assert data["manifest"]["citizen"]["call_budget_scope"] == "session_all_actors"
    assert not list(tmp_path.iterdir())


def test_comparison_manifest_and_police_context(tmp_path, adapter_factory):
    from backend.app.event_store import read_events
    from backend.app.provider_runner import run_comparison
    question = {"action": "ASK", "target": "B", "question": "¿Ha habido música esta noche?"}
    police, captured = adapter_factory("openai", [response_body("openai", json.dumps(question)),
                                                  response_body("openai", json.dumps(CLOSE))])
    config = ProviderConfig(provider="openai", model_id="requested-test-model", max_retries=0)
    def factory(config):
        return adapter_factory("openai", [response_body("openai", '{"answer_id":"B:F02"}')],
                               max_retries=0)[0]
    results = run_comparison([police], tmp_path, citizen_config=config, citizen_factory=factory)
    directory = results[0].path.parent
    manifest = json.loads((directory / "manifest.json").read_text())
    outcomes = json.loads((directory / "manifest-outcomes.json").read_text())
    events = read_events(results[0].path)
    assert manifest["citizen"] == events[0]["payload"]["citizen_conditions"]
    assert outcomes["participants"][0]["citizen_network_calls"] == 1
    assert outcomes["participants"][0]["citizen_model_observations"][0]["model_id"] == "resolved-test-model"
    assert "allowed_answers" not in json.dumps(captured)
    assert "citizen_diagnostic" not in json.dumps(captured)
