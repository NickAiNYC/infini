"""Trace emission and loading.

A trace is the `run.json` file every execution produces. It's the
portable record of what happened — the Observatory reads it, `infini
replay` reads it, `infini diff` reads it.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


@dataclass
class StepTrace:
    id: str
    name: str
    status: str  # ok | failed | retried | skipped
    started_at: str
    ended_at: str
    cost: dict  # {dollars, minutes, tokens: {input, output, total}}
    artifacts: list[str]
    agent: str
    action: str
    retry_attempt: int | None = None
    extensions: dict = field(default_factory=dict)


@dataclass
class CheckResult:
    check: str
    status: str  # pass | fail
    confidence: float | None = None
    detail: str | None = None


@dataclass
class Trace:
    loopfile: str
    loopfile_hash: str
    engine: dict
    started_at: str
    ended_at: str | None
    iterations: int
    steps: list[StepTrace]
    verifications: list[CheckResult]
    budget: dict
    outcome: str  # verified | unverified | budget_exceeded | escalated | error
    lessons: list[str]
    provenance: dict
    extensions: dict = field(default_factory=dict)
    replay_of: str | None = None
    replay_from_step: str | None = None

    def to_dict(self) -> dict:
        return {
            "loopfile": self.loopfile,
            "loopfile_hash": self.loopfile_hash,
            "engine": self.engine,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "iterations": self.iterations,
            "steps": [asdict(s) for s in self.steps],
            "verifications": [asdict(v) for v in self.verifications],
            "budget": self.budget,
            "outcome": self.outcome,
            "lessons": self.lessons,
            "provenance": self.provenance,
            "extensions": self.extensions,
            "replay_of": self.replay_of,
            "replay_from_step": self.replay_from_step,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def new_trace(loopfile_name: str, loopfile_yaml: str, engine_type: str = "infini-reference") -> Trace:
    """Create a fresh Trace at the start of a run."""
    return Trace(
        loopfile=loopfile_name,
        loopfile_hash=_sha256(loopfile_yaml.encode()),
        engine={"type": engine_type, "version": "1.0.0"},
        started_at=_now_iso(),
        ended_at=None,
        iterations=0,
        steps=[],
        verifications=[],
        budget={"spent_dollars": 0.0, "spent_minutes": 0.0},
        outcome="running",
        lessons=[],
        provenance={
            "engine_signature": "ed25519:placeholder",
            "artifact_hashes": {},
        },
    )


def add_step(
    trace: Trace,
    step_id: str,
    step_name: str,
    agent: str,
    action: str,
    artifacts: list[str],
    cost_dollars: float = 0.0,
    cost_minutes: float = 0.0,
    tokens_in: int = 0,
    tokens_out: int = 0,
    status: str = "ok",
    retry_attempt: int | None = None,
) -> None:
    """Append a step to the trace."""
    started = _now_iso()
    time.sleep(0.001)  # ensure ended > started
    ended = _now_iso()
    trace.steps.append(
        StepTrace(
            id=step_id, name=step_name, status=status,
            started_at=started, ended_at=ended,
            cost={
                "dollars": round(cost_dollars, 4),
                "minutes": round(cost_minutes, 2),
                "tokens": {"input": tokens_in, "output": tokens_out, "total": tokens_in + tokens_out},
            },
            artifacts=artifacts, agent=agent, action=action,
            retry_attempt=retry_attempt,
        )
    )
    trace.budget["spent_dollars"] = round(trace.budget["spent_dollars"] + cost_dollars, 4)
    trace.budget["spent_minutes"] = round(trace.budget["spent_minutes"] + cost_minutes, 2)


def finalize_trace(trace: Trace, outcome: str, lessons: list[str] | None = None) -> None:
    """Mark the trace as complete."""
    trace.ended_at = _now_iso()
    trace.outcome = outcome
    if lessons:
        trace.lessons = lessons


def add_verification(trace: Trace, check: str, passed: bool, confidence: float | None = None, detail: str | None = None) -> None:
    trace.verifications.append(
        CheckResult(
            check=check,
            status="pass" if passed else "fail",
            confidence=confidence,
            detail=detail,
        )
    )


def save_trace(trace: Trace, path: str | Path) -> Path:
    """Save a trace to a file (run.json or run.trace)."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(trace.to_json())
    return path


def load_trace(path: str | Path) -> dict:
    """Load a trace from a file. Returns the raw dict."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Trace not found: {path}")
    return json.loads(path.read_text())
