"""Exercise real SDK serialization/parsing against in-memory HTTP transports."""

from copy import deepcopy
import importlib
import json

import pytest

openai = pytest.importorskip("openai")
anthropic = pytest.importorskip("anthropic")

from backend.app.adapters.base import ProviderConfig
from backend.app.adapters.openai_adapter import OpenAIAdapter
from backend.app.adapters.anthropic_adapter import AnthropicAdapter
from backend.app.cli import main
from backend.app.event_store import JsonlEventSink, read_events
from backend.app.provider_runner import run_comparison, run_session
from backend.app.scenario_loader import load_scenario
from backend.app.secrets import Redactor
from backend.app.session_manager import SessionManager

SECRET = "sk-test-secret-never-log-this"
CLOSE = {"action": "CLOSE", "final_decision": "Fin de prueba", "actions_taken": [],
         "verified_facts": [], "unverified_claims": [], "remaining_uncertainties": ["Pendientes"],
         "justification": "Cierre de prueba"}


def response_body(provider, text, complete=True):
    if provider == "openai":
        return {"id": "resp_test", "object": "response", "created_at": 1,
                "model": "resolved-test-model", "status": "completed" if complete else "incomplete",
                "output": [{"id": "msg_test", "type": "message", "role": "assistant",
                            "status": "completed", "content": [{"type": "output_text", "text": text,
                                                                   "annotations": []}]}],
                "usage": {"input_tokens": 15, "output_tokens": 10, "total_tokens": 25,
                          "input_tokens_details": {"cached_tokens": 0},
                          "output_tokens_details": {"reasoning_tokens": 0}}}
    return {"id": "msg_test", "type": "message", "role": "assistant", "model": "resolved-test-model",
            "stop_reason": "end_turn" if complete else "max_tokens", "stop_sequence": None,
            "content": [{"type": "text", "text": text}], "usage": {"input_tokens": 15, "output_tokens": 10}}


@pytest.fixture
def adapter_factory():
    adapters = []

    def make(provider, outcomes, *, on_request=None, **options):
        sdk = openai if provider == "openai" else anthropic
        # SDK releases may use httpx or httpx2; use the installed SDK's transport.
        transport_module = next(base.__module__.split(".")[0] for base in sdk.DefaultHttpxClient.__mro__
                                if base.__module__.split(".")[0] in {"httpx", "httpx2"})
        http = importlib.import_module(transport_module)
        captured = []
        queue = list(outcomes)

        def handle(request):
            captured.append(json.loads(request.content))
            if on_request:
                on_request(request)
            outcome = queue.pop(0)
            if outcome == "timeout":
                raise http.ReadTimeout(SECRET, request=request)
            if isinstance(outcome, int):
                return http.Response(outcome, json={"error": {"type": "api_error", "message": SECRET}})
            return http.Response(200, json=outcome)

        client_type = sdk.OpenAI if provider == "openai" else sdk.Anthropic
        client = client_type(api_key=SECRET, max_retries=0,
                             http_client=http.Client(transport=http.MockTransport(handle)))
        config = ProviderConfig(provider=provider, model_id="requested-test-model", **options)
        factory = OpenAIAdapter if provider == "openai" else AnthropicAdapter
        adapter = factory(config, SECRET, client=client)
        adapters.append(adapter)
        return adapter, captured

    yield make
    for adapter in adapters:
        adapter.close()


def session_for(adapter, **kwargs):
    scenario, digest = load_scenario()
    return SessionManager(scenario, digest).create(
        adapter.config.provider, provider=adapter.config.provider,
        model_id=adapter.config.model_id, redact=Redactor((SECRET,)), **kwargs)


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_sdk_request_and_normalized_reply(provider, adapter_factory):
    adapter, captured = adapter_factory(provider, [response_body(provider, json.dumps(CLOSE))])
    messages = [{"role": "user", "content": "Caso público"}]
    reply = adapter.generate("Instrucciones iguales", messages)
    request = captured[0]
    assert request["model"] == "requested-test-model"
    assert reply.model_id == "resolved-test-model"
    assert reply.completed
    assert reply.usage["input_tokens"] == 15
    assert json.loads(reply.text) == CLOSE
    if provider == "openai":
        assert request["input"] == messages
        assert request["instructions"] == "Instrucciones iguales"
        assert request["store"] is False
        assert request["max_output_tokens"] == 1500
    else:
        assert request["messages"] == messages
        assert request["system"] == "Instrucciones iguales"
        assert request["max_tokens"] == 1500
    assert "temperature" not in request
    assert SECRET not in json.dumps(request)


def test_two_providers_three_interviews_and_isolation(tmp_path, adapter_factory, capsys):
    actions = [
        {"action": "ASK", "target": "A", "question": "¿Qué ha ocurrido esta noche?"},
        {"action": "ASK", "target": "B", "question": "¿Ha habido música esta noche?"},
        {"action": "ASK", "target": "C", "question": "¿Qué ha oído y qué puede confirmar?"}, CLOSE,
    ]
    adapters, requests = [], []
    for provider in ("openai", "anthropic"):
        adapter, captured = adapter_factory(provider, [response_body(provider, json.dumps(a)) for a in actions])
        adapters.append(adapter)
        requests.append(captured)
    results = run_comparison(adapters, tmp_path, redactor=Redactor((SECRET,)))
    output = capsys.readouterr().out
    assert output.count("Resumen de sesión") == 2
    assert output.count("Umbral de 3 intercambios alcanzado: sí") == 2
    assert output.count("Revisión humana: pendiente") == 2
    assert all(result.status == "agent_close" and result.calls == 4 and result.turns == 4 for result in results)
    assert requests[0][0]["input"] == requests[1][0]["messages"]
    assert requests[0][0]["instructions"] == requests[1][0]["system"]
    assert len(requests[1][0]["messages"]) == 1
    for result in results:
        events = read_events(result.path)
        assert len([event for event in events if event["type"] == "citizen_utterance"]) == 3
        assert len([event for event in events if event["type"] == "provider_request"]) == 4
        assert events[-1]["type"] == "session_closed"
        assert SECRET not in result.path.read_text()
    # No private source data or arbitrary internal state is sent to either API.
    scenario, _ = load_scenario()
    initial_wire = json.dumps(requests[0][0], ensure_ascii=False)
    for fact in scenario.truth_private.event_facts:
        assert fact.text not in initial_wire
    assert "initial_state" not in initial_wire


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
@pytest.mark.parametrize("failure", [429, 500, "timeout"])
def test_transient_failure_recovers_without_advancing_turn(tmp_path, provider, failure, adapter_factory):
    adapter, requests = adapter_factory(provider, [failure, response_body(provider, json.dumps(CLOSE))])
    session = session_for(adapter)
    calls = run_session(session, adapter, sleep=lambda _: None)
    assert calls == 2 and session.turn == 1 and session.status == "agent_close"
    assert requests[0] == requests[1]
    errors = [e for e in session.events if e["type"] == "provider_error"]
    assert errors[0]["payload"]["will_retry"] is True
    assert SECRET not in json.dumps(session.events)


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_auth_failure_is_controlled_and_never_retried(provider, adapter_factory):
    adapter, requests = adapter_factory(provider, [401])
    session = session_for(adapter)
    assert run_session(session, adapter) == 1
    assert len(requests) == 1 and session.turn == 0 and session.status == "provider_error"
    assert SECRET not in json.dumps(session.events)


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_malformed_response_is_a_controlled_error(provider, adapter_factory):
    adapter, _ = adapter_factory(provider, [{}])
    session = session_for(adapter)
    assert run_session(session, adapter) == 1
    assert session.status == "provider_error" and session.turn == 0
    errors = [event for event in session.events if event["type"] == "provider_error"]
    assert errors[0]["payload"]["code"] == "malformed_response"


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_retry_budget_exhausted(provider, adapter_factory):
    adapter, requests = adapter_factory(provider, [429, 429])
    session = session_for(adapter)
    assert run_session(session, adapter, sleep=lambda _: None) == 2
    assert session.status == "provider_error" and session.turn == 0
    assert len(requests) == 2


@pytest.mark.parametrize("provider", ["openai", "anthropic"])
def test_incomplete_response_cannot_execute_action(provider, adapter_factory):
    adapter, _ = adapter_factory(provider, [response_body(provider, json.dumps(CLOSE), complete=False)])
    session = session_for(adapter)
    run_session(session, adapter)
    assert session.status == "provider_error" and session.turn == 0
    assert not any(e["type"] == "agent_action_requested" for e in session.events)
    assert any(e["type"] == "provider_response" for e in session.events)


def test_invalid_json_is_bounded_and_can_be_corrected(adapter_factory):
    adapter, captured = adapter_factory("openai", [response_body("openai", "{"),
                                                 response_body("openai", json.dumps(CLOSE))])
    session = session_for(adapter)
    assert run_session(session, adapter) == 2
    assert session.turn == 1
    assert "invalid_action" in captured[1]["input"][-1]["content"]
    adapter, _ = adapter_factory("openai", [response_body("openai", "{")], max_calls=1)
    session = session_for(adapter)
    run_session(session, adapter)
    assert session.status == "call_limit" and session.turn == 0


def test_event_is_on_disk_before_network_and_action(tmp_path, adapter_factory):
    path = tmp_path / "trace.jsonl"

    def check_disk(_request):
        assert read_events(path)[-1]["type"] == "provider_request"

    adapter, _ = adapter_factory("openai", [response_body("openai", json.dumps(CLOSE))], on_request=check_disk)
    with JsonlEventSink(path) as sink:
        session = session_for(adapter, event_sink=sink.append)
        run_session(session, adapter)
        assert read_events(path) == session.events


def test_disk_failure_prevents_network_call(adapter_factory):
    adapter, captured = adapter_factory("openai", [])

    def broken_sink(_event):
        raise OSError("disk full")

    session = session_for(adapter, event_sink=broken_sink)
    with pytest.raises(OSError):
        run_session(session, adapter)
    assert captured == [] and session.turn == 0


def test_secret_in_response_is_redacted_before_execution_and_storage(adapter_factory):
    action = deepcopy(CLOSE)
    action["justification"] = SECRET
    adapter, _ = adapter_factory("anthropic", [response_body("anthropic", json.dumps(action))])
    session = session_for(adapter)
    run_session(session, adapter)
    serialized = json.dumps(session.events)
    assert SECRET not in serialized and "[REDACTED]" in serialized


def test_openai_refusal_cannot_be_executed(adapter_factory):
    body = response_body("openai", "")
    body["output"][0]["content"] = [{"type": "refusal", "refusal": "No"}]
    adapter, _ = adapter_factory("openai", [body])
    session = session_for(adapter)
    run_session(session, adapter)
    assert session.status == "provider_error" and session.turn == 0


def test_ctrl_c_keeps_a_closed_trace(tmp_path, adapter_factory):
    def interrupt(_request):
        raise KeyboardInterrupt

    adapter, _ = adapter_factory("openai", [], on_request=interrupt)
    path = tmp_path / "interrupt.jsonl"
    with JsonlEventSink(path) as sink:
        session = session_for(adapter, event_sink=sink.append)
        with pytest.raises(KeyboardInterrupt):
            run_session(session, adapter)
    assert read_events(path)[-1]["payload"]["reason"] == "interrupted"


def test_comparison_prints_summary_on_interrupt(tmp_path, adapter_factory, capsys):
    def interrupt(_request):
        raise KeyboardInterrupt

    adapter, _ = adapter_factory("openai", [], on_request=interrupt)
    second, requests = adapter_factory("anthropic", [])
    with pytest.raises(KeyboardInterrupt):
        run_comparison([adapter, second], tmp_path, redactor=Redactor((SECRET,)))
    output = capsys.readouterr().out
    assert "Resumen de sesión" in output
    assert 'Motivo de cierre: "interrupted"' in output
    assert "Revisión humana: pendiente" in output
    assert len(list(tmp_path.glob("*/*.jsonl"))) == 1
    assert requests == []


def test_cli_dry_run_and_missing_keys(monkeypatch, tmp_path, capsys):
    import backend.app.cli as cli
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "OPENAI_MODEL_ID", "ANTHROPIC_MODEL_ID"):
        monkeypatch.delenv(name, raising=False)
    args = ["run", "--openai-model", "test-openai", "--anthropic-model", "test-anthropic"]
    assert main([*args, "--dry-run"]) == 0
    preview = json.loads(capsys.readouterr().out)
    assert preview["network_calls"] == 0
    assert preview["manifest"]["mode"] == "dry_run_preview"
    assert preview["manifest"]["run_id"] is None
    assert preview["manifest"]["preflight"]["equal_compute_claimed"] is False
    assert not list(tmp_path.iterdir())
    assert main(args) == 1
    assert "Falta OPENAI_API_KEY" in capsys.readouterr().err


def test_dotenv_does_not_override_environment(monkeypatch, tmp_path, capsys):
    import backend.app.cli as cli
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    (tmp_path / ".env").write_text("OPENAI_MODEL_ID=file-model\nANTHROPIC_MODEL_ID=file-claude\n")
    monkeypatch.setenv("OPENAI_MODEL_ID", "environment-model")
    monkeypatch.setenv("ANTHROPIC_MODEL_ID", "environment-claude")
    assert main(["run", "--dry-run"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert data["providers"][0]["model_id"] == "environment-model"


@pytest.mark.parametrize("field,value", [("max_calls", 0), ("max_retries", 10), ("max_output_tokens", 0),
                                         ("timeout_seconds", -1.0), ("model_id", " ")])
def test_invalid_limits(field, value):
    with pytest.raises(ValueError):
        ProviderConfig(**{**{"provider": "openai", "model_id": "test"}, field: value})
