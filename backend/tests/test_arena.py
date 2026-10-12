import json
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from backend.app.arena import ArenaStore, make_server, project_trace, public_payload
from backend.app.cli import main, run_demo


def test_projection_excludes_private_fields_and_nested_objects(tmp_path):
    path = run_demo(tmp_path, citizen_mode="guarded-local", quiet=True)[0]
    events = [json.loads(line) for line in path.read_text().splitlines()]
    for event in events:
        event["payload"]["SECRET_PRIVATE"] = "PRIVATE_SENTINEL"
    events[0]["payload"]["initial_context"]["truth_private"] = "PRIVATE_SENTINEL"
    path.write_text("\n".join(json.dumps(e) for e in events if e["type"] != "citizen_diagnostic"))
    # Retain valid seq after removing diagnostics (which correctly forbid extra fields).
    events = [json.loads(line) for line in path.read_text().splitlines()]
    for i, event in enumerate(events, 1):
        event["seq"] = i
    path.write_text("\n".join(json.dumps(e) for e in events))
    projected = project_trace(path)
    assert projected["status"] == "complete"
    assert "PRIVATE_SENTINEL" not in json.dumps(projected)
    assert "fact_ids" not in json.dumps(projected)
    assert projected["events"][-1]["turn"] == 8
    assert public_payload("citizen_provider_request", {"input": "SECRET"}) is None
    assert public_payload("state_transition", {"tension": "SECRET"}) is None
    assert public_payload("tool_result", {"output": {"secret": "SECRET"}}) == {}
    assert public_payload("agent_action_requested", {"action": {"secret": 1}}) is None


def test_partial_corrupt_trace_keeps_prefix_without_accepting_closure(tmp_path):
    paths = run_demo(tmp_path, quiet=True)
    path = paths[0]
    path.write_bytes(path.read_bytes() + b'{"broken"')
    lane = project_trace(path)
    assert lane["status"] == "invalid"
    assert lane["events"][-1]["type"] == "session_closed"
    other = paths[1]
    lines = other.read_text().splitlines()
    other.write_text("\n".join(lines[:-1]))
    assert project_trace(other)["status"] == "incomplete"


def test_store_rejects_paths_and_symlinks(tmp_path):
    store = ArenaStore(tmp_path)
    assert store.runs() == []
    with pytest.raises(ValueError):
        store.run("../../.env")
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    link = tmp_path / "00000000-0000-0000-0000-000000000000"
    link.symlink_to(outside, target_is_directory=True)
    assert store.runs() == []
    with pytest.raises(ValueError):
        store.run(link.name)


def test_missing_second_participant_and_damaged_manifest(tmp_path):
    paths = run_demo(tmp_path, quiet=True)
    directory = paths[0].parent
    paths[1].unlink()
    (directory / "manifest.json").write_text(json.dumps({"participants": [
        {"trace": paths[0].name}, {"trace": paths[1].name}]}))
    store = ArenaStore(tmp_path)
    assert store.run(directory.name)["lanes"][1]["status"] == "not_started"
    (directory / "manifest.json").write_text("[]")
    assert len(store.run(directory.name)["lanes"]) == 2


def test_html_is_data_not_markup_in_projection():
    payload = public_payload("citizen_utterance", {"text": "<script>alert(1)</script>"})
    assert payload["text"].startswith("<script>")
    script = (Path(__file__).parents[1] / "app/web/app.js").read_text()
    assert "innerHTML" not in script and "textContent" in script


def test_mixed_run_is_rejected_and_different_scenario_warns(tmp_path):
    first = run_demo(tmp_path, quiet=True)
    second = run_demo(tmp_path, quiet=True)
    first[1].write_bytes(second[1].read_bytes())
    store = ArenaStore(tmp_path)
    assert store.run(first[0].parent.name)["lanes"][1]["status"] == "unreadable"
    events = [json.loads(line) for line in second[1].read_text().splitlines()]
    for event in events:
        event["run_id"] = first[0].parent.name
    events[0]["payload"]["scenario_sha256"] = "a" * 64
    first[1].write_text("\n".join(json.dumps(e) for e in events))
    assert store.run(first[0].parent.name)["conditions_warning"]


def test_http_routes_and_local_demo(tmp_path):
    # Runs with ordinary loopback permission; no external network or APIs.
    server = make_server(tmp_path, 0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base + "/") as response:
            assert b"Cuatro perspectivas" in response.read()
            assert response.headers["Content-Security-Policy"].startswith("default-src 'self'")
        for route in ("/.env", "/api/runs/../../.env", "/api/runs?path=.env"):
            with pytest.raises(HTTPError):
                urlopen(base + route)
        with pytest.raises(HTTPError):
            urlopen(Request(base + "/api/demo", method="POST"))
        with pytest.raises(HTTPError):
            urlopen(Request(base + "/api/demo", method="POST", headers={
                "X-Lab-Request": "demo", "Origin": "https://example.com"}))
        with urlopen(Request(base + "/api/demo", method="POST", headers={"X-Lab-Request": "demo"})) as response:
            run_id = json.load(response)["run_id"]
        with urlopen(base + "/api/runs/" + run_id) as response:
            data = json.load(response)
            assert len(data["lanes"]) == 2
            assert all(lane["status"] == "complete" for lane in data["lanes"])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_cli_arena_command_wires_output_and_port(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr("backend.app.arena.serve", lambda root, port: calls.append((root, port)))
    assert main(["arena", "--output", str(tmp_path), "--port", "9999"]) == 0
    assert calls == [(tmp_path, 9999)]
