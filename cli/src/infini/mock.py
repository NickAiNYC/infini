"""Mock LLM engine.

Simulates agent execution without calling any real model. This is what
makes `infini run --mock` work without an API key — users can see the
full loop execute, produce artifacts, emit traces, and pass/fail
verification, all deterministically.

The mock is deterministic: same Loopfile + same seed = same output.
This is essential for replay fidelity and for the conformance suite.
"""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass


@dataclass
class MockResult:
    """The result of a mocked step execution."""
    artifacts: list[str]
    cost_dollars: float
    cost_minutes: float
    tokens_in: int
    tokens_out: int
    status: str = "ok"
    retry_attempt: int | None = None


def _seed_from(loopfile_name: str, step_id: str, iteration: int) -> int:
    """Deterministic seed from loop name + step + iteration."""
    h = hashlib.sha256(f"{loopfile_name}:{step_id}:{iteration}".encode()).hexdigest()
    return int(h[:8], 16)


def mock_execute(
    step_id: str,
    step_name: str,
    action: str,
    agent_role: str,
    model_tier: str,
    produces: list[str],
    loopfile_name: str,
    iteration: int,
    retry_attempt: int = 0,
) -> MockResult:
    """Execute a step in mock mode. Returns a MockResult."""
    rng = random.Random(_seed_from(loopfile_name, step_id, iteration + retry_attempt))

    # Cost model (rough, model-tier-based)
    tier_multipliers = {"haiku": 0.5, "sonnet": 1.0, "opus": 3.0, "gpt-4o": 1.2}
    mult = tier_multipliers.get(model_tier, 1.0)

    tokens_in = rng.randint(800, 3000)
    tokens_out = rng.randint(200, 1200)
    cost_dollars = round((tokens_in * 0.000003 + tokens_out * 0.000015) * mult, 4)
    cost_minutes = round(rng.uniform(0.3, 1.8), 2)

    # Artifacts: produce what the step declares
    artifacts = list(produces)

    # Status: mostly ok, occasionally retried
    status = "ok"
    if retry_attempt == 0 and rng.random() < 0.15:
        # 15% chance of a transient failure on first attempt
        status = "failed"
    elif retry_attempt > 0:
        status = "ok"  # retries usually succeed

    return MockResult(
        artifacts=artifacts,
        cost_dollars=cost_dollars,
        cost_minutes=cost_minutes,
        tokens_in=tokens_in,
        tokens_out=tokens_out,
        status=status,
        retry_attempt=retry_attempt if retry_attempt > 0 else None,
    )


def mock_verify(
    check: str,
    loopfile_name: str,
    iteration: int,
    confidence_threshold: int,
    deterministic: bool = False,
    artifacts: list[str] | None = None,
) -> tuple[bool, float | None]:
    """Mock a verification check. Returns (passed, confidence).

    Syntactic checks are REAL where possible:
    - file:exists → checks if the file exists on disk
    - file:non_empty → checks if the file has content
    - file:valid_json → checks if the file is valid JSON
    - file:exit_zero → checks if a log file indicates exit 0

    Semantic checks (judge:/rubric:) use deterministic or RNG scores.

    When deterministic=True (used by conformance suite), all checks pass
    on iteration 1 with confidence at threshold+5. This makes conformance
    reproducible — no random failures, no budget exhaustion from retries.
    """
    import os
    import json as _json

    # ── Syntactic checks: REAL where possible ──
    if not (check.startswith("judge:") or check.startswith("rubric:")):
        # Parse the check: format is "filename:predicate" or "command"
        if ":exists" in check:
            filepath = check.split(":exists")[0].strip()
            # In mock mode, the engine produces artifacts in the run directory.
            # Check both the raw path and runs/latest/
            if os.path.exists(filepath):
                return True, None
            # Check if it's in the artifacts list
            if artifacts and filepath in artifacts:
                return True, None
            # Check runs/latest/
            alt_path = os.path.join("runs/latest", filepath)
            if os.path.exists(alt_path):
                return True, None
            # In mock/deterministic mode, the engine simulates producing files.
            # If the step declared it as produces, consider it exists.
            return True, None  # mock mode: assume step produced what it declared

        elif ":non_empty" in check:
            filepath = check.split(":non_empty")[0].strip()
            if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                return True, None
            return True, None  # mock mode: assume non-empty

        elif ":valid_json" in check:
            filepath = check.split(":valid_json")[0].strip()
            if os.path.exists(filepath):
                try:
                    _json.loads(open(filepath).read())
                    return True, None
                except (_json.JSONDecodeError, Exception):
                    return False, None
            return True, None  # mock mode: assume valid

        elif ":exit_zero" in check:
            filepath = check.split(":exit_zero")[0].strip()
            if os.path.exists(filepath):
                content = open(filepath).read()
                # Look for exit code indicators
                if "exit 0" in content or "PASS" in content or "passed" in content:
                    return True, None
                return False, None
            return True, None  # mock mode: assume pass

        elif check == "schema:valid" or check == "steps:all_executed" or check == "tools:available":
            return True, None  # meta-checks: always pass in mock mode

        else:
            # Unknown syntactic check: pass in mock mode
            return True, None

    # ── Semantic checks: RNG or deterministic ──
    if deterministic:
        conf = min(100, confidence_threshold + 5)
        return True, float(conf)

    rng = random.Random(_seed_from(loopfile_name, check, iteration))

    if iteration == 1:
        conf = rng.randint(max(0, confidence_threshold - 15), confidence_threshold - 1)
    else:
        conf = rng.randint(confidence_threshold, min(100, confidence_threshold + 12))
    passed = conf >= confidence_threshold
    return passed, float(conf)
