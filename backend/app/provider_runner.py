"""Bounded model loop. Only public context and this session's replies leave the process."""

import json
import sys
import time
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from importlib.metadata import version
from pathlib import Path

from .acceptance import render_summary, summarize_trace
from .adapters.base import PoliceModelAdapter, ProviderError, transport_metadata
from .event_store import JsonlEventSink
from .participants import participant_ids as resolve_participant_ids
from .prompts import PROMPT_VERSION, police_instructions
from .rules import RuleEngine
from .run_manifest import (
    build_manifest,
    check_conditions,
    collect_outcomes,
    write_document,
)
from .scenario_loader import load_scenario
from .secrets import Redactor
from .session_manager import Session, SessionManager


@dataclass(frozen=True)
class RunResult:
    path: Path
    provider: str
    status: str
    turns: int
    calls: int


def run_session(session: Session, adapter: PoliceModelAdapter, *,
                sleep: Callable[[float], None] = time.sleep,
                instructions: str | None = None) -> int:
    engine = RuleEngine()
    engine.start(session)
    instructions = police_instructions() if instructions is None else instructions
    messages = [{"role": "user", "content": json.dumps({
        **session.public_context(), "max_turns": session.scenario.max_turns,
    }, ensure_ascii=False)}]
    retries = 0
    calls = 0
    try:
        while session.status == "active" and calls < adapter.config.max_calls:
            calls += 1
            engine.record_provider_event(session, "provider_request", {
                "call_number": calls, "turn": session.turn + 1,
                "provider": adapter.config.provider, "model_id": adapter.config.model_id,
                "prompt_version": PROMPT_VERSION,
                "prompt_sha256": sha256(instructions.encode()).hexdigest(),
                "instructions": instructions, "messages": deepcopy(messages),
                "max_output_tokens": adapter.config.max_output_tokens,
                "sampling_settings": {}, "sampling_mode": "provider_defaults",
                **transport_metadata(adapter.config.provider, lookup=version),
            })
            started = time.perf_counter()
            try:
                reply = adapter.generate(instructions, deepcopy(messages))
            except ProviderError as error:
                will_retry = (error.recoverable and retries < adapter.config.max_retries
                              and calls < adapter.config.max_calls)
                engine.record_provider_event(session, "provider_error", {
                    "call_number": calls, "code": error.code,
                    "recoverable": error.recoverable, "will_retry": will_retry,
                    "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
                })
                if will_retry:
                    retries += 1
                    sleep(float(retries))
                    continue
                engine.close_technical(session, "provider_error")
                break
            retries = 0
            text = session.redact(reply.text)
            engine.record_provider_event(session, "provider_response", {
                "call_number": calls, "provider": adapter.config.provider,
                "requested_model_id": adapter.config.model_id, "model_id": reply.model_id,
                "response_id": reply.response_id, "text": text,
                "usage": reply.usage, "estimated_cost_usd": None,
                "completed": reply.completed, "finish_reason": reply.finish_reason,
                "elapsed_ms": round((time.perf_counter() - started) * 1000, 3),
            })
            if not reply.completed:
                engine.record_provider_event(session, "provider_error", {
                    "call_number": calls, "code": "incomplete_or_refused_response",
                    "recoverable": False, "will_retry": False,
                })
                engine.close_technical(session, "provider_error")
                break
            result = engine.execute(session, text)
            messages.extend([
                {"role": "assistant", "content": text},
                {"role": "user", "content": json.dumps(result, ensure_ascii=False)},
            ])
        if session.status == "active":
            engine.close_technical(session, "call_limit")
    except KeyboardInterrupt:
        engine.close_technical(session, "interrupted")
        raise
    return calls


def run_comparison(adapters: list[PoliceModelAdapter], output: Path, *, seed: int = 42,
                   redactor: Redactor | None = None, citizen_config: object = None,
                   citizen_factory: object = None,
                   participant_ids: list[str] | None = None) -> list[RunResult]:
    configs = [adapter.config for adapter in adapters]
    check_conditions(configs)
    ids = resolve_participant_ids(configs, participant_ids)
    scenario, digest = load_scenario()
    if (citizen_config is None) != (citizen_factory is None):
        raise ValueError("Citizen config and factory must be supplied together")
    manager = SessionManager(scenario, digest, scene_seed=seed,
                             citizen_mode="guarded-api" if citizen_config else "baseline",
                             citizen_config=citizen_config, citizen_factory=citizen_factory)
    instructions = police_instructions()
    manifest = build_manifest(configs, scenario, digest, instructions, seed=seed, run_id=manager.run_id,
                              citizen_config=citizen_config, participant_ids=ids)
    directory = output / manager.run_id
    directory.mkdir(parents=True, exist_ok=False)
    manifest_hash = write_document(directory / "manifest.json", manifest, redactor)
    print(f"Condiciones nominales comprobadas. Manifiesto: {directory / 'manifest.json'}", flush=True)
    results = []
    attempted = set()
    run_status = "aborted"
    try:
        for index, adapter in enumerate(adapters, 1):
            config = adapter.config
            if config != configs[index - 1]:
                raise ValueError("Configuración modificada después de la comprobación previa.")
            path = directory / f"{index}-{config.provider}.jsonl"
            attempted.add(index)
            print(f"Iniciando {config.provider}. Traza: {path}", flush=True)
            try:
                with JsonlEventSink(path) as sink:
                    session = manager.create(
                        ids[index - 1], model_id=config.model_id, provider=config.provider,
                        prompt_version=PROMPT_VERSION, max_output_tokens=config.max_output_tokens,
                        max_calls=config.max_calls, max_retries=config.max_retries,
                        timeout_seconds=config.timeout_seconds, event_sink=sink.append, redact=redactor,
                    )
                    calls = run_session(session, adapter, instructions=instructions)
            finally:
                print(render_summary(summarize_trace(path)), flush=True)
            results.append(RunResult(path, config.provider, session.status, session.turn, calls))
            print(f"{config.provider}: {session.turn} turnos, {calls} llamadas, cierre={session.status}", flush=True)
        run_status = "loop_completed"
        return results
    except KeyboardInterrupt:
        run_status = "interrupted"
        raise
    finally:
        original_error = sys.exc_info()[0] is not None
        try:
            outcomes = collect_outcomes(directory, manifest, manifest_hash,
                                        attempted=attempted, run_status=run_status)
            write_document(directory / "manifest-outcomes.json", outcomes, redactor)
        except Exception:
            if not original_error:
                raise
            print("No se pudo guardar el informe final; conserva y revisa las trazas.", file=sys.stderr)
