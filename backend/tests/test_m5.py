import csv
import json
from io import StringIO

import pytest

from backend.app.adapters.base import ProviderConfig, ProviderError
from backend.app.arena import ArenaStore
from backend.app.cli import main, run_demo
from backend.app.event_store import read_events
from backend.app.participants import load_participants
from backend.app.provider_runner import run_comparison
from backend.app.public_export import render_export
from backend.app.run_manifest import collect_outcomes
from backend.tests.test_manifest import LocalAdapter


def test_four_local_sessions_and_repeatability(tmp_path):
    first = run_demo(tmp_path, participants=4, citizen_mode="guarded-local", quiet=True)
    second = run_demo(tmp_path, participants=4, citizen_mode="guarded-local", quiet=True)
    assert first[0].parent != second[0].parent
    all_sessions = [read_events(p) for p in first + second]
    assert len({events[0]["session_id"] for events in all_sessions}) == 8
    reference = [(e["type"], e["payload"]) for e in all_sessions[0][1:]]
    assert all([(e["type"], e["payload"]) for e in events[1:]] == reference for events in all_sessions)
    projection = ArenaStore(tmp_path).run(first[0].parent.name)
    assert len(projection["lanes"]) == 4
    assert len({lane["participant"] for lane in projection["lanes"]}) == 4


def test_four_mixed_providers_have_unique_ids_and_failures(tmp_path):
    clients = [LocalAdapter(ProviderConfig(provider=p, model_id="model", max_retries=0))
               for p in ("openai", "openai", "gemini", "ollama")]
    clients[1].outcomes = [ProviderError("http_401")]
    results = run_comparison(clients, tmp_path)
    directory = results[0].path.parent
    manifest = json.loads((directory / "manifest.json").read_text())
    ids = [p["participant_id"] for p in manifest["participants"]]
    assert ids == ["p01-openai", "p02-openai", "p03-gemini", "p04-ollama"]
    assert [read_events(r.path)[0]["payload"]["participant_id"] for r in results] == ids
    assert results[1].status == "provider_error" and results[3].status == "agent_close"
    assert len(ArenaStore(tmp_path).run(directory.name)["lanes"]) == 4
    # Same provider/model, distinct IDs: swapping logs is detectable.
    raw = results[0].path.read_bytes()
    results[0].path.write_bytes(results[1].path.read_bytes())
    results[1].path.write_bytes(raw)
    final = collect_outcomes(directory, manifest, "hash", attempted={1, 2, 3, 4}, run_status="loop_completed")
    assert final["participants"][0]["trace_status"] == "invalid"
    assert final["participants"][1]["trace_status"] == "invalid"
    assert ArenaStore(tmp_path).run(directory.name)["lanes"][0]["status"] == "unreadable"


def test_not_started_corrupt_and_incomplete_participants_are_exported(tmp_path):
    clients = [LocalAdapter(ProviderConfig(provider="openai", model_id=f"m{i}")) for i in range(4)]
    clients[1].outcomes = [RuntimeError("deliberate interruption")]
    with pytest.raises(RuntimeError):
        run_comparison(clients, tmp_path)
    directory, = tmp_path.iterdir()
    first = directory / "1-openai.jsonl"
    first.write_bytes(first.read_bytes() + b'{"partial":')
    projection = ArenaStore(tmp_path).run(directory.name)
    assert [lane["status"] for lane in projection["lanes"]] == ["invalid", "incomplete", "not_started", "not_started"]
    rows = [json.loads(line) for line in render_export(projection, "jsonl").decode().splitlines()]
    people = [row for row in rows if row["record_type"] == "participant"]
    assert len(people) == 4
    assert [p["status"] for p in people] == [lane["status"] for lane in projection["lanes"]]
    assert all(p["participant_id"] for p in people)
    csv_rows = list(csv.DictReader(StringIO(render_export(projection, "csv").decode())))
    assert len(csv_rows) == len(rows)
    assert "provider_request" not in render_export(projection, "jsonl").decode()
    assert "instructions" not in render_export(projection, "csv").decode()


def test_csv_formula_protection_preserves_jsonl(tmp_path):
    paths = run_demo(tmp_path, quiet=True)
    projection = ArenaStore(tmp_path).run(paths[0].parent.name)
    projection["lanes"][0]["model"] = "  =HYPERLINK(\"evil\")"
    csv_rows = list(csv.DictReader(StringIO(render_export(projection, "csv").decode())))
    assert csv_rows[1]["model_id"].startswith("'  =")
    json_rows = [json.loads(line) for line in render_export(projection, "jsonl").decode().splitlines()]
    assert json_rows[1]["model_id"] == "  =HYPERLINK(\"evil\")"


@pytest.mark.parametrize("bad", [[], [{"id": "same", "provider": "openai", "model_id": "a"}] * 2,
    [{"id": "../bad", "provider": "openai", "model_id": "a"}] * 2,
    [{"id": "first", "provider": "openai", "model_id": "a", "api_key": "SECRET"}] * 2])
def test_invalid_rosters_fail_before_calls(bad, tmp_path):
    file = tmp_path / "people.json"
    file.write_text(json.dumps(bad))
    with pytest.raises(ValueError) as error:
        load_participants(file)
    assert "SECRET" not in str(error.value)


def test_four_dry_run_never_creates_output(tmp_path, capsys):
    file = tmp_path / "people.json"
    file.write_text(json.dumps([{"id": f"p{i}", "provider": p, "model_id": "example-model"}
                               for i, p in enumerate(("openai", "anthropic", "gemini", "ollama"))]))
    output = tmp_path / "output"
    assert main(["run", "--participants", str(file), "--dry-run", "--output", str(output)]) == 0
    manifest = json.loads(capsys.readouterr().out)["manifest"]
    assert len(manifest["participants"]) == 4
    assert manifest["manifest_schema_version"] == "2"
    assert not output.exists()


def test_duplicate_ids_rejected_before_manifest(tmp_path):
    clients = [LocalAdapter(ProviderConfig(provider="openai", model_id="a")) for _ in range(2)]
    with pytest.raises(ValueError):
        run_comparison(clients, tmp_path, participant_ids=["duplicate", "duplicate"])
    assert not list(tmp_path.iterdir()) and all(not a.requests for a in clients)


def test_cli_export_is_public_and_exclusive(tmp_path, capsys):
    paths = run_demo(tmp_path, participants=4, quiet=True)
    target = tmp_path / "export.csv"
    args = ["export", paths[0].parent.name, "--root", str(tmp_path), "--format", "csv", "--destination", str(target)]
    assert main(args) == 0
    before = target.read_bytes()
    assert main(args) == 1 and target.read_bytes() == before
    assert len([r for r in csv.DictReader(StringIO(before.decode())) if r["record_type"] == "participant"]) == 4
    capsys.readouterr()


@pytest.mark.parametrize("raw", [b"", b'{"bad":'])
def test_custom_identity_survives_empty_or_corrupt_start(tmp_path, raw):
    clients = [LocalAdapter(ProviderConfig(provider="openai", model_id="a")) for _ in range(2)]
    results = run_comparison(clients, tmp_path, participant_ids=["model-alpha", "model-beta"])
    results[0].path.write_bytes(raw)
    projection = ArenaStore(tmp_path).run(results[0].path.parent.name)
    assert projection["lanes"][0]["participant"] == "model-alpha"
    assert projection["lanes"][0]["model"] == "a"
    assert projection["lanes"][0]["status"] == "invalid"
    rows = [json.loads(line) for line in render_export(projection, "jsonl").decode().splitlines()]
    assert rows[1]["participant_id"] == "model-alpha" and rows[1]["status"] == "invalid"
