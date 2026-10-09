"""Run with: python -m backend.app.cli demo | replay FILE."""

import argparse
from contextlib import ExitStack
import json
import os
from pathlib import Path
import sys

from .event_store import export_session, read_events
from .acceptance import render_summary, summarize_trace
from .rules import RuleEngine
from .scenario_loader import DEFAULT_SCENARIO, ROOT, load_scenario
from .scripted_agent import PROMPT_VERSION, SCRIPT_VERSION, ScriptedAgent
from .session_manager import SessionManager


def render(events: list[dict]) -> str:
    lines = []
    for event in events:
        # JSON escaping prevents terminal control characters in untrusted messages.
        payload = json.dumps(event["payload"], ensure_ascii=False)
        lines.append(f'{event["seq"]:03d} {event["type"]}: {payload}')
    return "\n".join(lines)


def run_demo(output: Path, seed: int = 42, scenario_path: Path = DEFAULT_SCENARIO) -> list[Path]:
    scenario, digest = load_scenario(scenario_path)
    manager = SessionManager(scenario, digest, scene_seed=seed)
    directory = output / manager.run_id
    directory.mkdir(parents=True, exist_ok=False)
    paths = []
    for participant in ("ficticio-1", "ficticio-2"):
        session = manager.create(participant, model_id=SCRIPT_VERSION, prompt_version=PROMPT_VERSION)
        agent = ScriptedAgent(session.public_context())
        engine = RuleEngine()
        engine.start(session)
        while session.status == "active":
            action = agent.next_action()
            response = engine.execute(session, action)
            agent.receive(action, response)
            if not response["ok"]:
                raise ValueError(f"Acción rechazada en el guion: {response['error']}")
        path = directory / f"{participant}.jsonl"
        export_session(session, path)
        paths.append(path)
        print(f"\n{participant} — {session.turn} turnos — {session.status}")
        print(render(session.events))
        print(f"JSONL: {path}")
        print(render_summary(summarize_trace(path)))
    return paths


def run_live(args) -> int:
    try:
        from dotenv import load_dotenv
        from .adapters.openai_adapter import OpenAIAdapter
        from .adapters.anthropic_adapter import AnthropicAdapter
        from .adapters.base import ProviderConfig
        from .provider_runner import run_comparison
        from .secrets import Redactor
    except ImportError:
        raise ValueError("Instala dependencias: .venv/bin/python -m pip install -e '.[test,providers]'") from None
    load_dotenv(ROOT / ".env", override=False)
    configs = []
    for provider, model in (("openai", args.openai_model), ("anthropic", args.anthropic_model)):
        model_id = model or os.environ.get(f"{provider.upper()}_MODEL_ID", "")
        if not model_id:
            raise ValueError(f"Falta {provider.upper()}_MODEL_ID o --{provider}-model")
        configs.append(ProviderConfig(
            provider=provider, model_id=model_id, max_output_tokens=args.max_output_tokens,
            max_calls=args.max_calls, max_retries=args.max_retries, timeout_seconds=args.timeout,
        ))
    keys = [os.environ.get(f"{config.provider.upper()}_API_KEY", "").strip() for config in configs]
    redactor = Redactor(tuple(keys))
    if args.dry_run:
        from .run_manifest import build_manifest
        from .prompts import police_instructions
        scenario, digest = load_scenario()
        manifest = build_manifest(configs, scenario, digest, police_instructions(), seed=args.seed)
        print(json.dumps(redactor({"dry_run": True, "providers": [c.model_dump() for c in configs],
                                  "network_calls": 0, "manifest": manifest}), ensure_ascii=False, indent=2))
        return 0
    for config, key in zip(configs, keys):
        if not key:
            raise ValueError(f"Falta {config.provider.upper()}_API_KEY en el entorno o .env")
    with ExitStack() as stack:
        adapters = []
        for factory, config, key in zip((OpenAIAdapter, AnthropicAdapter), configs, keys):
            try:
                adapter = factory(config, key)
            except ImportError:
                raise ValueError("Instala el extra providers antes de ejecutar APIs") from None
            stack.callback(adapter.close)
            adapters.append(adapter)
        results = run_comparison(adapters, args.output, seed=args.seed, redactor=redactor)
    return 0 if all(r.status in {"agent_close", "max_turns"} for r in results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Police Lab — simulación local con agentes ficticios")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Ejecutar dos sesiones independientes")
    demo.add_argument("--output", type=Path, default=Path("results/private"))
    demo.add_argument("--seed", type=int, default=42)
    live = commands.add_parser("run", help="Comparar OpenAI y Anthropic mediante APIs (consume tokens)")
    live.add_argument("--openai-model", help="ID exacto; alternativa: OPENAI_MODEL_ID")
    live.add_argument("--anthropic-model", help="ID exacto; alternativa: ANTHROPIC_MODEL_ID")
    live.add_argument("--output", type=Path, default=Path("results/private"))
    live.add_argument("--seed", type=int, default=42)
    live.add_argument("--max-output-tokens", type=int, default=1500)
    live.add_argument("--max-calls", type=int, default=16, help="Por sesión; incluye errores y reintentos")
    live.add_argument("--max-retries", type=int, default=1, help="Reintentos de errores transitorios por acción")
    live.add_argument("--timeout", type=float, default=30.0)
    live.add_argument("--dry-run", action="store_true", help="Comprobar configuración sin red ni claves")
    replay = commands.add_parser("replay", help="Reproducir la cronología de un JSONL")
    replay.add_argument("file", type=Path)
    summary = commands.add_parser("summary", help="Resumen de una traza sin llamadas de red")
    summary.add_argument("file", type=Path)
    summary.add_argument("--review", type=Path, help="Registro JSON externo de revisión humana")
    summary.add_argument("--json", action="store_true", help="Salida estructurada")
    args = parser.parse_args(argv)
    try:
        if args.command == "demo":
            run_demo(args.output, args.seed)
        elif args.command == "run":
            return run_live(args)
        elif args.command == "summary":
            report = summarize_trace(args.file, args.review)
            print(json.dumps(report, ensure_ascii=False, indent=2) if args.json else render_summary(report))
            return int(report["trace_status"] in {"invalid", "unreadable"}
                       or report["human_review"]["status"] == "invalid")
        else:
            events = read_events(args.file)
            print(render(events))
            if events[-1]["type"] != "session_closed":
                print("Sesión incompleta: la traza no contiene un cierre.")
            print(render_summary(summarize_trace(args.file)))
    except (OSError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Ejecución interrumpida; revisa la traza conservada.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
