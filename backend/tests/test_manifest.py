"""Manifest evidence uses local adapters; no provider network is involved."""

from dataclasses import dataclass, field
from hashlib import sha256
import json

import pytest

from backend.app.adapters.base import ModelReply, ProviderConfig, ProviderError
from backend.app.event_store import read_events
from backend.app.provider_runner import run_comparison
from backend.app.run_manifest import collect_outcomes, git_snapshot, source_snapshot
from backend.app.secrets import Redactor

CLOSE = {"action": "CLOSE", "final_decision": "Fin", "actions_taken": [],
         "verified_facts": [], "unverified_claims": [], "remaining_uncertainties": [],
         "justification": "Prueba"}


def reply(model="resolved-model", action=None):
    return ModelReply(json.dumps(action or CLOSE), model, "response-test", {}, True, "end_turn")


@dataclass
class LocalAdapter:
    config: ProviderConfig
    outcomes: list = field(default_factory=lambda: [reply()])
    requests: list = field(default_factory=list)
    before_call: object = None

    def generate(self, instructions, messages):
        self.requests.append({"instructions": instructions, "messages": messages})
        if self.before_call:
            self.before_call()
        result = self.outcomes.pop(0)
        if isinstance(result, BaseException):
            raise result
        return result


@pytest.fixture(autouse=True)
def fake_sdk_metadata(monkeypatch):
    monkeypatch.setattr("backend.app.provider_runner.version", lambda _: "test-sdk")


@pytest.mark.parametrize("field,value", [("max_output_tokens", 2048), ("max_calls", 2),
                                         ("max_retries", 0), ("timeout_seconds", 15.0)])
def test_mismatched_limits_rejected_before_files_or_calls(tmp_path, field, value):
    first = LocalAdapter(ProviderConfig(provider="openai", model_id="first"))
    second = LocalAdapter(ProviderConfig(provider="anthropic", model_id="second", **{field: value}))
    with pytest.raises(ValueError, match=field):
        run_comparison([first, second], tmp_path)
    assert not list(tmp_path.iterdir())
    assert not first.requests and not second.requests


def test_empty_comparison_rejected(tmp_path):
    with pytest.raises(ValueError, match="participante"):
        run_comparison([], tmp_path)
    assert not list(tmp_path.iterdir())


def test_manifest_precedes_calls_and_matches_requests(tmp_path):
    captured = []

    def before_call():
        path, = tmp_path.glob("*/manifest.json")
        captured.append(path.read_bytes())
        assert not (path.parent / "manifest-outcomes.json").exists()

    adapters = [LocalAdapter(ProviderConfig(provider=p, model_id=f"requested-{p}"), before_call=before_call)
                for p in ("openai", "anthropic")]
    results = run_comparison(adapters, tmp_path)
    directory = results[0].path.parent
    raw = (directory / "manifest.json").read_bytes()
    manifest = json.loads(raw)
    outcomes = json.loads((directory / "manifest-outcomes.json").read_text())
    assert captured == [raw, raw]
    assert outcomes["manifest_sha256"] == sha256(raw).hexdigest()
    assert outcomes["run_status"] == "loop_completed"
    assert manifest["preflight"]["equal_compute_claimed"] is False
    assert manifest["code"]["source"]["sha256"]
    assert manifest["environment"]["packages"]
    assert manifest["protocol"]["version"] == "demo-m2-v1"
    assert manifest["citizen"]["version"] == "controlled-citizen-v1"
    assert manifest["scenario"]["seed"] == 42
    assert manifest["failure_policy"]["sdk_retries"] == 0
    for i, (adapter, result) in enumerate(zip(adapters, results)):
        events = read_events(result.path)
        assert manifest["run_id"] == events[0]["run_id"]
        assert manifest["scenario"]["sha256"] == events[0]["payload"]["scenario_sha256"]
        assert manifest["prompt"]["sha256"] == sha256(adapter.requests[0]["instructions"].encode()).hexdigest()
        assert manifest["participants"][i]["config"] == adapter.config.model_dump()
        assert outcomes["participants"][i]["resolved_model_ids"] == ["resolved-model"]
        assert outcomes["participants"][i]["trace_sha256"] == sha256(result.path.read_bytes()).hexdigest()
        assert "manifest_schema_version" not in json.dumps(adapter.requests)
        assert "packages" not in json.dumps(adapter.requests)


def test_prompt_is_built_once_per_comparison(tmp_path, monkeypatch):
    calls = []

    def prompt():
        calls.append(True)
        return f"instructions-{len(calls)}"

    monkeypatch.setattr("backend.app.provider_runner.police_instructions", prompt)
    adapters = [LocalAdapter(ProviderConfig(provider=p, model_id=p)) for p in ("openai", "anthropic")]
    run_comparison(adapters, tmp_path)
    assert len(calls) == 1
    assert adapters[0].requests[0]["instructions"] == adapters[1].requests[0]["instructions"]


def test_model_changes_and_repeated_providers_remain_distinct(tmp_path):
    first = LocalAdapter(ProviderConfig(provider="openai", model_id="alias"), outcomes=[
        reply("resolved-1", {"action": "SPEAK", "target": "A", "message": "Hola"}), reply("resolved-2")])
    second = LocalAdapter(ProviderConfig(provider="openai", model_id="alias-2"))
    results = run_comparison([first, second], tmp_path)
    data = json.loads((results[0].path.parent / "manifest-outcomes.json").read_text())
    assert data["participants"][0]["resolved_model_ids"] == ["resolved-1", "resolved-2"]
    assert data["participants"][0]["model_observations"] == [
        {"call_number": 1, "model_id": "resolved-1"}, {"call_number": 2, "model_id": "resolved-2"}]
    assert results[0].path.name == "1-openai.jsonl"
    assert results[1].path.name == "2-openai.jsonl"


@pytest.mark.parametrize("error,status,trace_status", [
    (KeyboardInterrupt(), "interrupted", "complete"), (RuntimeError("synthetic"), "aborted", "incomplete")])
def test_interruption_and_unhandled_error_preserve_not_started(tmp_path, error, status, trace_status):
    first = LocalAdapter(ProviderConfig(provider="openai", model_id="first"), outcomes=[error])
    second = LocalAdapter(ProviderConfig(provider="anthropic", model_id="second"))
    with pytest.raises(type(error)):
        run_comparison([first, second], tmp_path)
    path, = tmp_path.glob("*/manifest-outcomes.json")
    data = json.loads(path.read_text())
    assert data["run_status"] == status
    assert data["participants"][0]["trace_status"] == trace_status
    assert data["participants"][0]["resolved_model_ids"] == []
    assert data["participants"][1]["trace_status"] == "not_started"
    assert not data["participants"][1]["attempted"]
    assert not second.requests


def test_provider_failure_preserved_and_next_participant_runs(tmp_path):
    first = LocalAdapter(ProviderConfig(provider="openai", model_id="first"), outcomes=[ProviderError("http_401")])
    second = LocalAdapter(ProviderConfig(provider="anthropic", model_id="second"))
    results = run_comparison([first, second], tmp_path)
    data = json.loads((results[0].path.parent / "manifest-outcomes.json").read_text())
    assert data["run_status"] == "loop_completed"
    assert data["participants"][0]["closure_reason"] == "provider_error"
    assert data["participants"][0]["resolved_model_ids"] == []
    assert data["participants"][1]["closure_reason"] == "agent_close"


def test_source_hash_changes_but_ignores_secrets_and_outputs(tmp_path):
    files = {"backend/app/main.py": "initial", "pyproject.toml": "project",
             "schemas/action.schema.json": "{}", "scenarios/PL-001.yaml": "scenario",
             "docs/RUN_PROTOCOL.md": "protocol"}
    for name, content in files.items():
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    first = source_snapshot(tmp_path)
    (tmp_path / ".env").write_text("TOKEN=secret-never-read")
    (tmp_path / "results/private").mkdir(parents=True)
    (tmp_path / "results/private/trace.jsonl").write_text("private")
    assert source_snapshot(tmp_path) == first
    (tmp_path / "backend/app/main.py").write_text("changed")
    assert source_snapshot(tmp_path)["sha256"] != first["sha256"]
    assert git_snapshot(tmp_path) == {"status": "not_initialized", "commit": None, "dirty": None}
    assert "secret-never-read" not in json.dumps(first)


def test_configured_secret_is_absent_from_all_artifacts(tmp_path):
    secret = "test-configured-credential"
    adapter = LocalAdapter(ProviderConfig(provider="openai", model_id=secret), outcomes=[reply(secret)])
    results = run_comparison([adapter], tmp_path, redactor=Redactor((secret,)))
    for path in results[0].path.parent.iterdir():
        assert secret not in path.read_text()


@pytest.mark.parametrize("interrupt", [False, True])
def test_final_write_failure_never_masks_original_error(tmp_path, monkeypatch, interrupt):
    import backend.app.provider_runner as runner
    original = runner.write_document

    def fail_final(path, data, redactor):
        if path.name == "manifest-outcomes.json":
            raise OSError("synthetic disk failure")
        return original(path, data, redactor)

    monkeypatch.setattr(runner, "write_document", fail_final)
    adapter = LocalAdapter(ProviderConfig(provider="openai", model_id="model"),
                           outcomes=[KeyboardInterrupt() if interrupt else reply()])
    with pytest.raises(KeyboardInterrupt if interrupt else OSError):
        run_comparison([adapter], tmp_path)
    assert list(tmp_path.glob("*/manifest.json"))
    assert list(tmp_path.glob("*/*.jsonl"))


def test_initial_write_failure_prevents_calls(tmp_path, monkeypatch):
    def fail(*_):
        raise OSError("synthetic disk failure")

    monkeypatch.setattr("backend.app.provider_runner.write_document", fail)
    adapter = LocalAdapter(ProviderConfig(provider="openai", model_id="model"))
    with pytest.raises(OSError):
        run_comparison([adapter], tmp_path)
    assert not adapter.requests


def test_corrupt_trace_does_not_invent_resolved_models(tmp_path):
    adapter = LocalAdapter(ProviderConfig(provider="openai", model_id="model"))
    result, = run_comparison([adapter], tmp_path)
    directory = result.path.parent
    manifest = json.loads((directory / "manifest.json").read_text())
    result.path.write_bytes(result.path.read_bytes() + b'{"partial":')
    data = collect_outcomes(directory, manifest, "test-hash", attempted={1}, run_status="aborted")
    assert data["participants"][0]["trace_status"] == "invalid"
    assert data["participants"][0]["resolved_model_ids"] == []
    assert not data["participants"][0]["resolved_ids_verified_from_trace"]
