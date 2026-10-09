from hashlib import sha256
from pathlib import Path

import yaml

from .models import Scenario

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SCENARIO = ROOT / "scenarios/PL-001.yaml"


def load_scenario(path: str | Path = DEFAULT_SCENARIO) -> tuple[Scenario, str]:
    """Return validated private data and the hash of the original YAML bytes."""
    raw = Path(path).read_bytes()
    return Scenario.model_validate(yaml.safe_load(raw)), sha256(raw).hexdigest()
