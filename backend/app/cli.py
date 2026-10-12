"""Run with: python -m backend.app.cli demo | replay FILE."""

import argparse
import json
import os
import sys
from contextlib import ExitStack
from pathlib import Path
from typing import Literal

from .acceptance import render_summary, summarize_trace
from .citizen_runtime import CITIZEN_MODES
from .event_store import JsonlEventSink, export_session, read_events
from .rules import RuleEngine
from .scenario_loader import DEFAULT_SCENARIO, ROOT, load_scenario
from .scripted_agent import PROMPT_VERSION, SCRIPT_VERSION, ScriptedAgent
from .session_manager import SessionManager
from .trace_inspection import inspect_trace, render_inspection


def render(events: list[dict]) -> str:
    lines = []
    for event in events:
        # JSON escaping prevents terminal control characters in untrusted messages.
        payload = json.dumps(event["payload"], ensure_ascii=False)
        lines.append(f'{event["seq"]:03d} {event["type"]}: {payload}')
    return "\n".join(lines)


def run_demo(output: Path, seed: int = 42, scenario_path: Path = DEFAULT_SCENARIO,
             *, citizen_mode: str = "baseline", quiet: bool = False, participants: int = 2) -> list[Path]:
    if participants not in (2, 4):
        raise ValueError("La demo admite 2 o 4 participantes")
    scenario, digest = load_scenario(scenario_path)
    manager = SessionManager(scenario, digest, scene_seed=seed, citizen_mode=citizen_mode)
    directory = output / manager.run_id
    directory.mkdir(parents=True, exist_ok=False)
    from .run_manifest import source_snapshot, write_document
    people = [f"ficticio-{i}" for i in range(1, participants + 1)]
    write_document(directory / "manifest.json", {
        "manifest_schema_version": "2", "run_id": manager.run_id, "mode": "local_demo",
        "protocol": {"version": "local-demo-v2"}, "source": source_snapshot(),
        "scenario": {"id": scenario.scenario_id, "version": scenario.scenario_version,
                     "sha256": digest, "seed": seed},
        "citizen": {"mode": citizen_mode}, "execution_order": "sequential_input_order_no_counterbalancing",
        "participants": [{"order": i, "participant_id": person, "trace": f"{person}.jsonl",
                          "config": {"provider": "local", "model_id": SCRIPT_VERSION}}
                         for i, person in enumerate(people, 1)],
    })
    paths = []
    for participant in people:
        path = directory / f"{participant}.jsonl"
        with ExitStack() as stack:
            sink = (stack.enter_context(JsonlEventSink(path))
                    if citizen_mode == "guarded-local" else None)
            session = manager.create(participant, model_id=SCRIPT_VERSION, prompt_version=PROMPT_VERSION,
                                     event_sink=sink.append if sink else None)
            agent = ScriptedAgent(session.public_context())
            engine = RuleEngine()
            engine.start(session)
            while session.status == "active":
                action = agent.next_action()
                response = engine.execute(session, action)
                agent.receive(action, response)
                if not response["ok"]:
                    raise ValueError(f"Acción rechazada en el guion: {response['error']}")
            if sink is None:
                export_session(session, path)
        paths.append(path)
        if not quiet:
            print(f"\n{participant} — {session.turn} turnos — {session.status}")
            print(render(session.events))
            print(f"JSONL: {path}")
            print(render_summary(summarize_trace(path)))
    return paths


def run_live(args: argparse.Namespace) -> int:
    try:
        from dotenv import load_dotenv

        from .adapters.anthropic_adapter import AnthropicAdapter
        from .adapters.base import PoliceModelAdapter, ProviderConfig
        from .adapters.openai_adapter import OpenAIAdapter
        from .provider_runner import run_comparison
        from .secrets import Redactor
    except ImportError:
        raise ValueError("Instala dependencias: .venv/bin/python -m pip install -e '.[test,providers]'") from None
    load_dotenv(ROOT / ".env", override=False)
    from .adapters.gemini_adapter import GeminiAdapter
    from .adapters.ollama_adapter import OllamaAdapter
    from .participants import load_participants, participant_ids
    limits = {"max_output_tokens": args.max_output_tokens, "max_calls": args.max_calls,
              "max_retries": args.max_retries, "timeout_seconds": args.timeout}
    if args.participants:
        if args.openai_model or args.anthropic_model:
            raise ValueError("Usa --participants o las opciones de dos modelos, no ambas")
        configs, ids = load_participants(args.participants, **limits)
    else:
        configs = []
        providers: tuple[tuple[Literal["openai", "anthropic"], str | None], ...] = (
            ("openai", args.openai_model), ("anthropic", args.anthropic_model))
        for provider, model in providers:
            model_id = model or os.environ.get(f"{provider.upper()}_MODEL_ID", "")
            if not model_id:
                raise ValueError(f"Falta {provider.upper()}_MODEL_ID o --{provider}-model")
            configs.append(ProviderConfig(provider=provider, model_id=model_id, **limits))
        ids = participant_ids(configs)
    factories = {"openai": OpenAIAdapter, "anthropic": AnthropicAdapter,
                 "gemini": GeminiAdapter, "ollama": OllamaAdapter}
    keys = {provider: os.environ.get(f"{provider.upper()}_API_KEY", "").strip() for provider in factories}
    citizen_config = None
    if bool(args.citizen_provider) != bool(args.citizen_model):
        raise ValueError("Usa --citizen-provider y --citizen-model juntos")
    if args.citizen_provider:
        citizen_config = ProviderConfig(
            provider=args.citizen_provider, model_id=args.citizen_model,
            max_calls=args.citizen_max_calls, max_output_tokens=args.citizen_max_output_tokens,
            max_retries=0, timeout_seconds=args.timeout)
    redactor = Redactor(tuple(keys.values()))
    if args.dry_run:
        from .prompts import police_instructions
        from .run_manifest import build_manifest
        scenario, digest = load_scenario()
        manifest = build_manifest(configs, scenario, digest, police_instructions(), seed=args.seed,
                                  citizen_config=citizen_config, participant_ids=ids)
        print(json.dumps(redactor({"dry_run": True, "providers": [c.model_dump() for c in configs],
                                  "network_calls": 0, "manifest": manifest}), ensure_ascii=False, indent=2))
        return 0
    for config in configs + ([citizen_config] if citizen_config else []):
        if config.provider != "ollama" and not keys[config.provider]:
            raise ValueError(f"Falta {config.provider.upper()}_API_KEY en el entorno o .env")
    with ExitStack() as stack:
        def make_adapter(config: ProviderConfig) -> PoliceModelAdapter:
            try:
                adapter = factories[config.provider](config, keys[config.provider])
            except ImportError:
                raise ValueError("Instala el extra providers antes de ejecutar APIs") from None
            stack.callback(adapter.close)
            return adapter

        adapters = [make_adapter(config) for config in configs]
        citizen_factory = make_adapter
        results = run_comparison(adapters, args.output, seed=args.seed, redactor=redactor,
                                 citizen_config=citizen_config,
                                 citizen_factory=citizen_factory if citizen_config else None, participant_ids=ids)
    return 0 if all(r.status in {"agent_close", "max_turns"} for r in results) else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="AI Police Lab — simulación local con agentes ficticios")
    commands = parser.add_subparsers(dest="command", required=True)
    demo = commands.add_parser("demo", help="Ejecutar dos sesiones independientes")
    demo.add_argument("--output", type=Path, default=Path("results/private"))
    demo.add_argument("--seed", type=int, default=42)
    demo.add_argument("--participants", type=int, choices=(2, 4), default=2)
    demo.add_argument("--citizen-mode", choices=CITIZEN_MODES, default="baseline",
                      help="Ciudadano de referencia o selector local controlado (sin API)")
    live = commands.add_parser("run", help="Comparar OpenAI y Anthropic mediante APIs (consume tokens)")
    live.add_argument("--participants", type=Path, help="JSON con 2 o 4 participantes y IDs únicos")
    live.add_argument("--openai-model", help="ID exacto; alternativa: OPENAI_MODEL_ID")
    live.add_argument("--anthropic-model", help="ID exacto; alternativa: ANTHROPIC_MODEL_ID")
    live.add_argument("--output", type=Path, default=Path("results/private"))
    live.add_argument("--seed", type=int, default=42)
    live.add_argument("--max-output-tokens", type=int, default=1500)
    live.add_argument("--max-calls", type=int, default=16, help="Por sesión; incluye errores y reintentos")
    live.add_argument("--max-retries", type=int, default=1, help="Reintentos de errores transitorios por acción")
    live.add_argument("--timeout", type=float, default=30.0)
    live.add_argument("--dry-run", action="store_true", help="Comprobar configuración sin red ni claves")
    live.add_argument("--citizen-provider", choices=("openai", "anthropic", "gemini", "ollama"))
    live.add_argument("--citizen-model", help="ID del selector ciudadano; activa llamadas adicionales")
    live.add_argument("--citizen-max-calls", type=int, default=24, help="Total ciudadano por sesión, A+B+C")
    live.add_argument("--citizen-max-output-tokens", type=int, default=256)
    replay = commands.add_parser("replay", help="Reproducir la cronología de un JSONL")
    replay.add_argument("file", type=Path)
    summary = commands.add_parser("summary", help="Resumen de una traza sin llamadas de red")
    summary.add_argument("file", type=Path)
    summary.add_argument("--review", type=Path, help="Registro JSON externo de revisión humana")
    summary.add_argument("--json", action="store_true", help="Salida estructurada")
    inspect = commands.add_parser("inspect", help="Inspeccionar el prefijo válido de una traza sin modificarla")
    inspect.add_argument("file", type=Path)
    inspect.add_argument("--json", action="store_true", help="Diagnóstico y eventos del prefijo en JSON")
    arena = commands.add_parser("arena", help="Visor local de dos carriles, sin claves en navegador")
    arena.add_argument("--output", type=Path, default=Path("results/private"))
    arena.add_argument("--port", type=int, default=8765)
    export = commands.add_parser("export", help="Exportar proyección pública CSV o JSONL (sin red)")
    export.add_argument("run_id")
    export.add_argument("--root", type=Path, default=Path("results/private"))
    export.add_argument("--format", choices=("csv", "jsonl"), required=True)
    export.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "export":
            from .arena import ArenaStore
            from .public_export import render_export
            body = render_export(ArenaStore(args.root).run(args.run_id), args.format)
            with args.destination.open("xb") as stream:
                stream.write(body)
            print(f"Proyección pública exportada: {args.destination}")
        elif args.command == "arena":
            from .arena import serve
            serve(args.output, args.port)
        elif args.command == "demo":
            run_demo(args.output, args.seed, citizen_mode=args.citizen_mode, participants=args.participants)
        elif args.command == "run":
            return run_live(args)
        elif args.command == "inspect":
            report = inspect_trace(args.file)
            if args.json:
                print(json.dumps(report, ensure_ascii=False, indent=2))
            else:
                print(render_inspection(report))
                print(render(report["valid_prefix_events"]))
            return int(report["trace_status"] in {"invalid", "unreadable"})
        elif args.command == "summary":
            trace_summary = summarize_trace(args.file, args.review)
            print(json.dumps(trace_summary, ensure_ascii=False, indent=2) if args.json
                  else render_summary(trace_summary))
            return int(trace_summary["trace_status"] in {"invalid", "unreadable"}
                       or trace_summary["human_review"]["status"] == "invalid")
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
