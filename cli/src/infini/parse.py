"""Loopfile parser and validator.

Reads a YAML Loopfile, validates it against the INFINI JSON Schema,
and returns a structured Loopfile object.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

_SCHEMA_PATH = Path(__file__).parent / "schema.json"


@dataclass
class Agent:
    name: str
    role: str
    model_tier: str
    tools: list[str] = field(default_factory=list)


@dataclass
class Step:
    id: str
    name: str
    action: str
    uses: str
    produces: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)
    retry: dict | None = None


@dataclass
class Verify:
    syntactic: list[str]
    semantic: list[str]
    confidence_threshold: int


@dataclass
class Budget:
    dollars: float
    minutes: float
    tokens: int | None = None


@dataclass
class Loopfile:
    spec_version: str
    name: str
    version: str
    description: str | None
    objective: str
    agents: list[Agent]
    steps: list[Step]
    verify: Verify
    budget: Budget
    stop_when: list[str]
    lessons: dict | None = None
    state: dict | None = None
    engine: dict | None = None
    raw: dict = field(default_factory=dict, repr=False)


class ParseError(Exception):
    """Raised when a Loopfile is invalid."""

    def __init__(self, message: str, errors: list[dict] | None = None):
        super().__init__(message)
        self.errors = errors or []


def _load_schema() -> dict:
    with open(_SCHEMA_PATH) as f:
        return json.load(f)


def parse(yaml_str: str) -> Loopfile:
    """Parse a YAML string into a Loopfile. Raises ParseError on invalid input."""
    try:
        raw = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        raise ParseError(f"YAML parse error: {e}")

    if not isinstance(raw, dict):
        raise ParseError("Loopfile must be a YAML mapping at the top level.")

    # Validate against JSON Schema
    schema = _load_schema()
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(raw), key=lambda e: list(e.absolute_path))
    if errors:
        msgs = []
        for err in errors:
            path = ".".join(str(p) for p in err.absolute_path) or "<root>"
            msgs.append(f"  {path}: {err.message}")
        raise ParseError(
            f"Loopfile failed schema validation ({len(errors)} error(s)):\n" + "\n".join(msgs),
            errors=[{"path": list(e.absolute_path), "message": e.message} for e in errors],
        )

    # Build structured object
    return _build_loopfile(raw)


def parse_file(path: str | Path) -> Loopfile:
    """Parse a Loopfile from a file path."""
    path = Path(path)
    if not path.exists():
        raise ParseError(f"File not found: {path}")
    return parse(path.read_text())


def _build_loopfile(raw: dict) -> Loopfile:
    agents = [
        Agent(
            name=a["name"],
            role=a["role"],
            model_tier=a["model_tier"],
            tools=a.get("tools", []),
        )
        for a in raw["AGENTS"]
    ]

    steps = []
    for s in raw["STEPS"]:
        steps.append(
            Step(
                id=s["id"],
                name=s["name"],
                action=s["action"],
                uses=s["uses"],
                produces=s.get("produces", []),
                depends_on=s.get("depends_on", []),
                retry=s.get("retry"),
            )
        )

    verify = Verify(
        syntactic=raw["VERIFY"]["syntactic"],
        semantic=raw["VERIFY"]["semantic"],
        confidence_threshold=raw["VERIFY"]["confidence_threshold"],
    )

    budget = Budget(
        dollars=raw["BUDGET"]["dollars"],
        minutes=raw["BUDGET"]["minutes"],
        tokens=raw["BUDGET"].get("tokens"),
    )

    return Loopfile(
        spec_version=raw["LOOPFILE"],
        name=raw["name"],
        version=raw["version"],
        description=raw.get("description"),
        objective=raw["OBJECTIVE"],
        agents=agents,
        steps=steps,
        verify=verify,
        budget=budget,
        stop_when=raw["STOP_WHEN"],
        lessons=raw.get("LESSONS"),
        state=raw.get("STATE"),
        engine=raw.get("ENGINE"),
        raw=raw,
    )


def to_dict(loopfile: Loopfile) -> dict:
    """Serialize a Loopfile back to a dict (for trace emission)."""
    return {
        "LOOPFILE": loopfile.spec_version,
        "name": loopfile.name,
        "version": loopfile.version,
        "description": loopfile.description,
        "OBJECTIVE": loopfile.objective,
        "AGENTS": [
            {"name": a.name, "role": a.role, "model_tier": a.model_tier, "tools": a.tools}
            for a in loopfile.agents
        ],
        "STEPS": [
            {
                "id": s.id, "name": s.name, "action": s.action, "uses": s.uses,
                "produces": s.produces, "depends_on": s.depends_on, "retry": s.retry,
            }
            for s in loopfile.steps
        ],
        "VERIFY": {
            "syntactic": loopfile.verify.syntactic,
            "semantic": loopfile.verify.semantic,
            "confidence_threshold": loopfile.verify.confidence_threshold,
        },
        "BUDGET": {
            "dollars": loopfile.budget.dollars,
            "minutes": loopfile.budget.minutes,
            "tokens": loopfile.budget.tokens,
        },
        "STOP_WHEN": loopfile.stop_when,
        "LESSONS": loopfile.lessons,
        "STATE": loopfile.state,
        "ENGINE": loopfile.engine,
    }
