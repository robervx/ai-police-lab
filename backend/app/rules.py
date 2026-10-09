"""Synchronous deterministic engine, without provider calls."""

from copy import deepcopy
from datetime import datetime, timezone
import json
from uuid import uuid4

from jsonschema import Draft202012Validator

from .scenario_loader import ROOT
from .session_manager import Session
from .citizen import CITIZEN_VERSION, respond


class RuleEngine:
    def __init__(self):
        schema = json.loads((ROOT / "schemas/action.schema.json").read_text())
        Draft202012Validator.check_schema(schema)
        self._validator = Draft202012Validator(schema)

    def _record(self, session: Session, kind: str, payload: dict) -> dict:
        event = {
            "event_schema_version": "0.1", "event_id": str(uuid4()),
            "run_id": session.run_id, "session_id": session.session_id,
            "seq": len(session._events) + 1,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            "actor": "engine", "type": kind, "payload": session.redact(payload),
        }
        if session.event_sink is not None:
            session.event_sink(deepcopy(event))
        session._events.append(event)
        return deepcopy(event)

    def record_provider_event(self, session: Session, kind: str, payload: dict) -> dict:
        if kind not in {"provider_request", "provider_response", "provider_error"}:
            raise ValueError("Unsupported provider event")
        if session.status != "active":
            raise ValueError("Cannot append to a closed session")
        self.start(session)
        return self._record(session, kind, payload)

    def close_technical(self, session: Session, reason: str) -> None:
        if reason not in {"provider_error", "call_limit", "interrupted"}:
            raise ValueError("Unsupported technical closure")
        if session.status == "active":
            self.start(session)
            self._record(session, "session_closed", {"reason": reason, "turn": session.turn})
            session.status = reason

    def start(self, session: Session) -> None:
        if any(event["type"] == "session_started" for event in session._events):
            return
        scenario = session.scenario
        self._record(session, "session_started", {
            "scenario_id": scenario.scenario_id, "scenario_version": scenario.scenario_version,
            "scenario_sha256": session.scenario_sha256, "scene_seed": session.scene_seed,
            "participant_id": session.participant_id, "provider": session.provider,
            "model_id": session.model_id, "prompt_version": session.prompt_version,
            "citizen_model_id": CITIZEN_VERSION, "sampling_settings": {},
            "max_turns": scenario.max_turns, "initial_context": session.public_context(),
            "max_output_tokens": session.max_output_tokens, "max_calls": session.max_calls,
            "max_retries": session.max_retries, "timeout_seconds": session.timeout_seconds,
            "sampling_mode": "provider_defaults" if session.provider != "local" else "deterministic",
        })

    def execute(self, session: Session, raw: dict | str, *, reviewed_tags: tuple[str, ...] = ()) -> dict:
        """Tags are supplied by the trusted reviewer, never read from agent JSON."""
        if session.status != "active":
            return {"ok": False, "error": "session_closed"}
        self.start(session)
        try:
            action = json.loads(raw) if isinstance(raw, str) else deepcopy(raw)
            if not self._validator.is_valid(action):
                raise ValueError("invalid_action")
        except (ValueError, TypeError):
            self._record(session, "agent_action_rejected", {"error": "invalid_action"})
            return {"ok": False, "error": "invalid_action"}

        scenario = session.scenario
        if "target" in action and action["target"] not in scenario.allowed_targets:
            self._record(session, "agent_action_rejected", {"error": "invalid_target"})
            return {"ok": False, "error": "invalid_target"}
        self._record(session, "agent_action_requested", action)
        kind = action["action"]
        result = {}
        event_kind = "tool_result"
        if kind in {"OBSERVE", "CHECK"}:
            entry = (scenario.observations[action["observation_id"]] if kind == "OBSERVE"
                     else scenario.checks[action["check_id"]])
            result = {"output": entry.output}
            if kind == "CHECK":
                result["available"] = entry.available
            if kind == "OBSERVE" or entry.available:
                for fact in entry.reveals:
                    if fact not in session.state.public_evidence:
                        session.state.public_evidence.append(fact)
                if kind == "CHECK" and action["check_id"] == "witness_contact":
                    session.state.witness_contacted = True
        elif kind in {"ASK", "SPEAK"}:
            result = respond(scenario, action)
            event_kind = "citizen_utterance"
        elif kind in {"REQUEST_SUPPORT", "DECIDE"}:
            result = {"recorded": True, "material_effect": False}
        elif kind == "CLOSE":
            result = {"closure": action}
            session.status = "agent_close"
            event_kind = "state_transition"
        self._record(session, event_kind, result)
        self._apply_tags(session, action, reviewed_tags)
        session.turn += 1
        self._record(session, "turn_completed", {"turn": session.turn})
        if session.status == "active" and session.turn >= scenario.max_turns:
            session.status = "max_turns"
        if session.status != "active":
            self._record(session, "session_closed", {"reason": session.status, "turn": session.turn})
        return {"ok": True, "result": deepcopy(result), "turn": session.turn, "status": session.status}

    def _apply_tags(self, session: Session, action: dict, tags: tuple[str, ...]):
        if action["action"] not in {"ASK", "SPEAK"}:
            return
        rules = session.scenario.state_rules
        changes = []
        name = "constructive_contact_A"
        if action["target"] == "A" and set(rules.constructive_contact_A.requires) <= set(tags):
            changes.append((name, "A", rules.constructive_contact_A.tension_delta_A,
                            rules.constructive_contact_A.cooperation_delta_A))
        name = "categorical_accusation_without_evidence"
        if action["target"] == "B" and name in tags:
            changes.append((name, "B", rules.categorical_accusation_without_evidence.tension_delta_B, 0))
        for name, actor, tension, cooperation in changes:
            if name in session.applied_rules:
                continue
            for field, delta in (("tension", tension), ("cooperation", cooperation)):
                values = getattr(session.state, field)
                values[actor] = max(rules.bounds.minimum, min(rules.bounds.maximum, values[actor] + delta))
            session.applied_rules.add(name)
            self._record(session, "state_transition", {"rule": name, "reviewed_tags": list(tags),
                         "target": actor, "tension": session.state.tension[actor],
                         "cooperation": session.state.cooperation[actor]})
