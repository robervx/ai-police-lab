"""Validated, server-only scenario definition for PL-001."""

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

Score = Annotated[int, Field(ge=0, le=100)]


class Model(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Fact(Model):
    id: str
    text: str
    type: Literal["synthetic_ground_truth", "bounded_unknown", "observation_limited"]


class Truth(Model):
    event_facts: list[Fact]
    unresolved: list[str]


class Actor(Model):
    role: str
    initial_tension: Score
    initial_cooperation: Score
    voice: str
    knows: list[str]
    belief_unverified: str | None = None
    greeting: str


class State(Model):
    scene_phase: str
    acoustic_status: str
    immediate_threat_confirmed: bool
    injured_person_observed: bool
    witness_contacted: bool
    measured_noise: bool
    operational_actions: list[str]
    public_evidence: list[str]
    tension: dict[str, Score]
    cooperation: dict[str, Score]


class Observation(Model):
    reveals: list[str] = Field(default_factory=list)
    output: str


class Check(Observation):
    available: bool


class Bounds(Model):
    minimum: Literal[0]
    maximum: Literal[100]


class ConstructiveRule(Model):
    requires: list[str]
    cooperation_delta_A: int
    tension_delta_A: int
    once_per_session: Literal[True]


class AccusationRule(Model):
    tension_delta_B: int
    once_per_session: Literal[True]


class Rules(Model):
    bounds: Bounds
    constructive_contact_A: ConstructiveRule
    categorical_accusation_without_evidence: AccusationRule
    note: str


class TerminalRules(Model):
    agent_close: str
    max_turns: str
    fatal_error: str


class Scenario(Model):
    schema_version: Literal["0.1"]
    scenario_id: Literal["PL-001"]
    scenario_version: str
    title: str
    jurisdiction_note: str
    start_time_local: str
    max_turns: int = Field(gt=0)
    intro_public: str
    objective_public: str
    truth_private: Truth
    actors: dict[str, Actor]
    initial_state: State
    allowed_targets: list[str]
    observations: dict[str, Observation]
    checks: dict[str, Check]
    state_rules: Rules
    terminal_rules: TerminalRules
    closure_required_fields: list[str]

    @model_validator(mode="after")
    def invariants(self):
        facts = [f.id for f in self.truth_private.event_facts]
        if len(facts) != len(set(facts)):
            raise ValueError("Duplicate fact IDs")
        if set(self.allowed_targets) != set(self.actors) or set(self.actors) != {"A", "B", "C"}:
            raise ValueError("Targets must match PL-001 actors")
        for source in [*self.actors.values(), *self.observations.values(), *self.checks.values()]:
            refs = source.knows if isinstance(source, Actor) else source.reveals
            if not set(refs) <= set(facts):
                raise ValueError("Unknown fact reference")
        state = self.initial_state
        if state.measured_noise or state.immediate_threat_confirmed or state.injured_person_observed:
            raise ValueError("PL-001 cannot start with a measurement, confirmed threat or injury")
        if state.public_evidence or state.operational_actions or state.witness_contacted:
            raise ValueError("PL-001 must start without prior observations or actions")
        for field in ("tension", "cooperation"):
            expected = {key: getattr(actor, f"initial_{field}") for key, actor in self.actors.items()}
            if getattr(state, field) != expected:
                raise ValueError(f"Initial {field} does not match actors")
        if set(self.observations) != {"hallway_sound", "immediate_safety_scan"}:
            raise ValueError("Unsupported observation catalog")
        if set(self.checks) != {"sound_meter", "query_legal_offense", "witness_contact"}:
            raise ValueError("Unsupported check catalog")
        if self.checks["sound_meter"].available or self.checks["sound_meter"].reveals:
            raise ValueError("Sound meter cannot produce a measurement")
        required = {"actions_taken", "verified_facts", "unverified_claims", "remaining_uncertainties", "justification", "final_decision"}
        if set(self.closure_required_fields) != required:
            raise ValueError("Invalid closure fields")
        return self
