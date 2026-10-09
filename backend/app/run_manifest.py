"""Local provenance and nominal preflight checks, outside participant context."""

from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import distributions
from io import StringIO
import json
import os
from pathlib import Path
import platform
import subprocess

from .adapters.base import ProviderConfig
from .citizen import CITIZEN_VERSION
from .event_store import parse_events
from .prompts import PROMPT_VERSION
from .scenario_loader import ROOT
from .secrets import Redactor

PROTOCOL_VERSION = "demo-m2-v1"
NOMINAL_FIELDS = ("max_output_tokens", "max_calls", "max_retries", "timeout_seconds")


def check_conditions(configs: list[ProviderConfig]) -> dict:
    if not configs:
        raise ValueError("Se requiere al menos un participante.")
    differences = [name for name in NOMINAL_FIELDS
                   if any(getattr(c, name) != getattr(configs[0], name) for c in configs[1:])]
    if differences:
        raise ValueError("Condiciones nominales distintas: " + ", ".join(differences))
    return {"status": "nominal_limits_match", "checked_fields": list(NOMINAL_FIELDS),
            "participant_count": len(configs), "equal_compute_claimed": False,
            "sampling": "provider_defaults_not_equivalent"}


def source_snapshot(root: Path = ROOT) -> dict:
    # Explicit source scope: never traverse environment files, results or Git contents.
    paths = sorted(set(root.joinpath("backend").rglob("*.py")) | {
        root / "pyproject.toml", root / "schemas/action.schema.json",
        root / "scenarios/PL-001.yaml", root / "docs/RUN_PROTOCOL.md",
    })
    hashes = {}
    for path in paths:
        if path.is_symlink() or any(parent.is_symlink() for parent in path.parents if root in parent.parents):
            raise ValueError("El conjunto de fuentes no admite enlaces simbólicos.")
        hashes[path.relative_to(root).as_posix()] = sha256(path.read_bytes()).hexdigest()
    canonical = json.dumps(hashes, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {"algorithm": "sha256", "aggregate_encoding": "sorted_compact_json_of_file_hashes",
            "sha256": sha256(canonical).hexdigest(), "files": hashes,
            "scope": "backend/**/*.py, pyproject.toml, schema, scenario, run protocol",
            "meaning": "files_on_disk_at_preflight_not_a_source_archive"}


def git_snapshot(root: Path = ROOT) -> dict:
    if not (root / ".git").exists():
        return {"status": "not_initialized", "commit": None, "dirty": None}
    try:
        commit = subprocess.run(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                                check=True, capture_output=True, text=True, timeout=5).stdout.strip()
        status = subprocess.run(["git", "-C", str(root), "status", "--porcelain"],
                                check=True, capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return {"status": "unavailable", "commit": None, "dirty": None}
    return {"status": "available", "commit": commit, "dirty": bool(status)}


def environment_snapshot() -> dict:
    packages = sorted({(d.metadata["Name"], d.version) for d in distributions()
                       if d.metadata["Name"]})
    return {"python": platform.python_version(), "implementation": platform.python_implementation(),
            "system": platform.system(), "release": platform.release(), "machine": platform.machine(),
            "packages": [{"name": name, "version": version} for name, version in packages],
            "restoration_verified": False}


def build_manifest(configs, scenario, scenario_sha256, instructions, *, seed=42, run_id=None) -> dict:
    preflight = check_conditions(configs)
    sources = source_snapshot()
    return {
        "manifest_schema_version": "1", "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "mode": "execution" if run_id is not None else "dry_run_preview",
        "protocol": {"version": PROTOCOL_VERSION, "path": "docs/RUN_PROTOCOL.md",
                     "sha256": sources["files"]["docs/RUN_PROTOCOL.md"]},
        "code": {"source": sources, "git": git_snapshot()},
        "environment": environment_snapshot(), "preflight": preflight,
        "scenario": {"id": scenario.scenario_id, "version": scenario.scenario_version,
                     "sha256": scenario_sha256, "seed": seed, "max_turns": scenario.max_turns},
        "prompt": {"version": PROMPT_VERSION, "sha256": sha256(instructions.encode()).hexdigest()},
        "action_schema_sha256": sources["files"]["schemas/action.schema.json"],
        "citizen": {"version": CITIZEN_VERSION, "mode": "deterministic_exact_catalog"},
        "execution_order": "sequential_input_order_no_counterbalancing",
        "participants": [{"order": index, "config": config.model_dump(),
                          "trace": f"{index}-{config.provider}.jsonl"}
                         for index, config in enumerate(configs, 1)],
        "failure_policy": {
            "sdk_retries": 0, "retry_scope": "recoverable_errors_per_action_within_max_calls",
            "retry_delays_seconds": [1, 2],
            "invalid_action": "record_and_continue_within_call_limit",
            "incomplete_or_refused_response": "close_provider_error",
            "provider_failure": "close_session_then_continue_next_participant",
            "interrupt_or_unhandled_error": "stop_run_preserve_traces",
        },
        "limitations": ["Nominal limits do not establish equal compute or cost.",
                        "Provider sampling defaults are not equivalent settings.",
                        "Local seed does not seed provider generation.",
                        "File hashes and installed versions do not prove environment restoration.",
                        "Resolved model IDs are observations in manifest-outcomes.json and JSONL.",
                        "Custom adapters or injected SDK clients are not authenticated by preflight."],
    }


def write_document(path: Path, document: dict, redactor: Redactor | None = None) -> str:
    raw = (json.dumps((redactor or Redactor())(document), ensure_ascii=False,
                      indent=2, allow_nan=False) + "\n").encode("utf-8")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())
    return sha256(raw).hexdigest()


def collect_outcomes(directory: Path, manifest: dict, manifest_sha256: str,
                     *, attempted: set[int], run_status: str) -> dict:
    participants = []
    for participant in manifest["participants"]:
        path = directory / participant["trace"]
        item = {"order": participant["order"], "trace": participant["trace"],
                "requested_model_id": participant["config"]["model_id"],
                "attempted": participant["order"] in attempted,
                "trace_status": "unreadable" if participant["order"] in attempted else "not_started",
                "trace_sha256": None, "closure_reason": None, "resolved_model_ids": [],
                "model_observations": [], "resolved_ids_verified_from_trace": False}
        if participant["order"] in attempted:
            try:
                raw = path.read_bytes()
            except OSError:
                pass
            else:
                item["trace_sha256"] = sha256(raw).hexdigest()
                try:
                    events = parse_events(StringIO(raw.decode("utf-8")))
                    if events[0]["run_id"] != manifest["run_id"]:
                        raise ValueError("Different run")
                    observations = [{"call_number": event["payload"]["call_number"],
                                     "model_id": event["payload"]["model_id"]}
                                    for event in events if event["type"] == "provider_response"]
                    if any(not isinstance(o["model_id"], str) for o in observations):
                        raise ValueError("Invalid model identity")
                    closed = events[-1]["type"] == "session_closed"
                    reason = events[-1]["payload"]["reason"] if closed else None
                except (ValueError, KeyError):
                    item["trace_status"] = "invalid"
                else:
                    item.update(trace_status="complete" if closed else "incomplete", closure_reason=reason,
                                resolved_model_ids=list(dict.fromkeys(o["model_id"] for o in observations)),
                                model_observations=observations, resolved_ids_verified_from_trace=True)
        participants.append(item)
    return {"manifest_schema_version": "1", "run_id": manifest["run_id"],
            "manifest_sha256": manifest_sha256, "run_status": run_status,
            "recorded_at": datetime.now(timezone.utc).isoformat(), "participants": participants}
