"""Loopback-only read projection and local demo launcher for up to four lanes."""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer, ThreadingHTTPServer
from pathlib import Path
from threading import Lock
from urllib.parse import urlsplit

from .trace_inspection import inspect_trace

STATIC = Path(__file__).parent / "web"
RUN_ID = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
ACTION_FIELDS = {
    "ASK": ("target", "question"), "SPEAK": ("target", "message"),
    "OBSERVE": ("observation_id",), "CHECK": ("check_id",),
    "REQUEST_SUPPORT": ("reason",), "DECIDE": ("decision", "justification"),
    "CLOSE": ("final_decision", "actions_taken", "verified_facts", "unverified_claims",
              "remaining_uncertainties", "justification"),
}
CLOSURES = {"agent_close", "max_turns", "provider_error", "call_limit", "interrupted"}


def public_payload(kind: str, payload: dict) -> dict | None:
    """Project by event AND leaf fields. Never return a raw payload or nested dict."""
    if kind == "agent_action_requested":
        action = payload.get("action")
        if not isinstance(action, str) or action not in ACTION_FIELDS:
            return None
        result: dict[str, str | list[str]] = {"action": action}
        for key in ACTION_FIELDS[action]:
            value = payload.get(key)
            if isinstance(value, str) or (isinstance(value, list) and all(isinstance(x, str) for x in value)):
                result[key] = value
        return result
    if kind == "citizen_utterance":
        return {k: payload[k] for k in ("target", "text", "source") if isinstance(payload.get(k), str)}
    if kind == "tool_result":
        return {k: payload[k] for k in ("output", "available", "recorded", "material_effect")
                if isinstance(payload.get(k), (str, bool))}
    if kind == "agent_action_rejected":
        return {"message": "Acción rechazada por el motor"}
    if kind == "session_closed":
        reason = payload.get("reason")
        return {"reason": reason if isinstance(reason, str) and reason in CLOSURES else "unknown"}
    return None


def project_trace(path: Path, expected_run: str | None = None) -> dict:
    if path.is_symlink() or path.stat().st_size > 16 * 1024 * 1024:
        raise ValueError("Unsupported trace")
    report = inspect_trace(path)
    events = report["valid_prefix_events"]
    if events and expected_run is not None and events[0]["run_id"] != expected_run:
        raise ValueError("Trace belongs to another run")
    start = events[0]["payload"] if events else {}
    def string(key: str, default: str = "") -> str:
        return start[key] if isinstance(start.get(key), str) else default
    projected, turn = [], 1
    for event in events:
        if event["type"] == "turn_completed":
            turn += 1
        payload = public_payload(event["type"], event["payload"])
        if payload is not None:
            event_turn = event["payload"].get("turn") if event["type"] == "session_closed" else turn
            projected.append({"seq": event["seq"], "turn": event_turn if type(event_turn) is int else turn,
                              "type": event["type"], "payload": payload})
    intro = start.get("initial_context", {})
    intro = intro.get("intro_public", "") if isinstance(intro, dict) else ""
    return {"participant": string("participant_id", path.stem),
            "session_id": events[0]["session_id"] if events else None,
            "model": string("model_id"), "provider": string("provider"),
            "citizen": string("citizen_model_id"),
            "scenario": string("scenario_id"), "scenario_version": string("scenario_version"),
            "scenario_sha256": string("scenario_sha256"),
            "intro": intro if isinstance(intro, str) else "",
            "status": report["trace_status"], "events": projected,
            "trace_sha256": report.get("trace_sha256"),
            "review": "pending", "source": path.name}


class ArenaStore:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root).resolve()
        self.demo_lock = Lock()

    def runs(self) -> list[dict]:
        if not self.root.exists():
            return []
        paths = [p for p in self.root.iterdir() if RUN_ID.fullmatch(p.name)
                 and p.is_dir() and not p.is_symlink()]
        return [{"id": p.name} for p in sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[:100]]

    def run(self, run_id: str) -> dict:
        if not RUN_ID.fullmatch(run_id):
            raise ValueError("Invalid run")
        directory = self.root / run_id
        if not directory.is_dir() or directory.is_symlink():
            raise ValueError("Unknown run")
        paths = sorted(p for p in directory.glob("*.jsonl") if not p.is_symlink())
        # A sequential comparison may not have created the second trace yet.
        manifest_path = directory / "manifest.json"
        expected = []
        expected_metadata = {}
        manifest_warning = ""
        if manifest_path.is_file() and not manifest_path.is_symlink() and manifest_path.stat().st_size < 2_000_000:
            try:
                manifest = json.loads(manifest_path.read_text())
                participants = manifest.get("participants", [])
                if len(participants) > 4:
                    manifest_warning = "El manifiesto supera cuatro participantes; solo se muestran los cuatro primeros."
                for participant in participants[:4]:
                    trace = participant.get("trace")
                    if isinstance(trace, str) and re.fullmatch(r"[a-zA-Z0-9_-]+\.jsonl", trace):
                        expected.append(directory / trace)
                        expected_metadata[trace] = participant
            except (ValueError, TypeError, AttributeError):
                pass
        lanes = []
        for path in (expected or paths)[:4]:
            metadata = expected_metadata.get(path.name, {})
            config = metadata.get("config", {})
            if not isinstance(config, dict):
                config = {}
            identity = metadata.get("participant_id", config.get("provider", path.stem))
            identity = identity if isinstance(identity, str) else path.stem
            placeholder: dict[str, object] = {"participant": identity, "events": [], "source": path.name,
                           "model": config.get("model_id") if isinstance(config.get("model_id"), str) else "",
                           "provider": config.get("provider") if isinstance(config.get("provider"), str) else ""}
            if not path.exists() and not path.is_symlink():
                lanes.append({**placeholder, "status": "not_started"})
                continue
            try:
                lane = project_trace(path, run_id)
                if not lane.get("session_id"):
                    lane.update({key: placeholder[key] for key in ("participant", "model", "provider")})
                if lane.get("session_id") and metadata and (
                        ("participant_id" in metadata and lane["participant"] != identity)
                        or ("provider" in config and lane["provider"] != config["provider"])
                        or ("model_id" in config and lane["model"] != config["model_id"])):
                    raise ValueError("Participant differs from manifest")
                lanes.append(lane)
            except (OSError, ValueError):
                lanes.append({**placeholder, "status": "unreadable"})
        while len(lanes) < 2:
            lanes.append({"participant": f"Participante {len(lanes) + 1}", "events": [], "status": "not_started"})
        scenario_hashes = {lane.get("scenario_sha256") for lane in lanes if lane.get("scenario_sha256")}
        identities = [lane.get("session_id") for lane in lanes if lane.get("session_id")]
        warnings = [manifest_warning] if manifest_warning else []
        if not expected and len(paths) > 4:
            warnings.append("La carpeta supera cuatro trazas; solo se muestran las cuatro primeras.")
        if len(scenario_hashes) > 1:
            warnings.append("Los escenarios de los carriles difieren.")
        if len(identities) != len(set(identities)):
            warnings.append("Los carriles contienen la misma sesión; no son participantes independientes.")
        return {"run_id": run_id, "lanes": lanes, "order": "sequential",
                "conditions_warning": " ".join(warnings),
                "notice": "Simulación ficticia. Sin puntuación ni evaluación policial validada."}

    def demo(self, participants: int = 2) -> dict:
        if not self.demo_lock.acquire(blocking=False):
            raise ValueError("Demo already running")
        try:
            from .cli import run_demo
            paths = run_demo(self.root, citizen_mode="guarded-local", quiet=True, participants=participants)
            return {"run_id": paths[0].parent.name}
        finally:
            self.demo_lock.release()


def make_server(root: str | Path, port: int = 8765) -> ThreadingHTTPServer:
    store = ArenaStore(root)

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args: object) -> None:
            pass

        def allowed_host(self) -> bool:
            assert isinstance(self.server, HTTPServer)  # noqa: S101 — narrowing, server siempre es el de make_server
            return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}",
                                                f"localhost:{self.server.server_port}"}

        def send_body(self, status: int, body: bytes,
                      content_type: str = "application/json; charset=utf-8") -> None:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; object-src 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)

        def send_json(self, status: int, data: object) -> None:
            self.send_body(status, json.dumps(data, ensure_ascii=False, allow_nan=False).encode())

        def do_GET(self) -> None:
            if not self.allowed_host():
                return self.send_json(403, {"error": "Host no permitido"})
            url = urlsplit(self.path)
            if url.query:
                return self.send_json(400, {"error": "No se admiten rutas por query"})
            try:
                if url.path == "/api/runs":
                    return self.send_json(200, store.runs())
                if url.path.startswith("/api/runs/"):
                    tail = url.path.removeprefix("/api/runs/")
                    if tail.endswith(("/export.csv", "/export.jsonl")):
                        from .public_export import render_export
                        run_id, filename = tail.rsplit("/", 1)
                        format = filename.split(".")[1]
                        body = render_export(store.run(run_id), format)
                        return self.send_body(200, body, "text/csv; charset=utf-8" if format == "csv"
                                              else "application/x-ndjson; charset=utf-8")
                    return self.send_json(200, store.run(tail))
                assets = {"/": ("index.html", "text/html; charset=utf-8"),
                          "/app.js": ("app.js", "text/javascript; charset=utf-8"),
                          "/style.css": ("style.css", "text/css; charset=utf-8")}
                if url.path in assets:
                    name, mime = assets[url.path]
                    return self.send_body(200, (STATIC / name).read_bytes(), mime)
            except (OSError, ValueError):
                return self.send_json(404, {"error": "Ejecución no disponible"})
            self.send_json(404, {"error": "Ruta no disponible"})

        def do_POST(self) -> None:
            origin = self.headers.get("Origin")
            if (not self.allowed_host() or self.path not in {"/api/demo", "/api/demo/4"}
                    or self.headers.get("X-Lab-Request") != "demo"
                    or (origin and origin != f"http://{self.headers.get('Host')}")):
                return self.send_json(403, {"error": "Solicitud no permitida"})
            try:
                return self.send_json(201, store.demo(4 if self.path == "/api/demo/4" else 2))
            except (OSError, ValueError):
                return self.send_json(409, {"error": "No se pudo completar la demo; revisa las trazas"})

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def serve(root: str | Path, port: int = 8765) -> None:
    with make_server(root, port) as server:
        print(f"AI POLICE LAB · http://127.0.0.1:{server.server_port} · Ctrl+C para cerrar", flush=True)
        server.serve_forever()
