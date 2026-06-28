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
) -> tuple[bool, float | None]:
    """Mock a verification check. Returns (passed, confidence).

    Syntactic checks (no 'judge:' prefix) mostly pass.
    Semantic checks return a confidence score; iteration 1 is usually
    below threshold, iteration 2+ usually passes.
    """
    rng = random.Random(_seed_from(loopfile_name, check, iteration))

    if check.startswith("judge:") or check.startswith("rubric:"):
        # Semantic check
        if iteration == 1:
            # First iteration: likely below threshold
            conf = rng.randint(max(0, confidence_threshold - 15), confidence_threshold - 1)
        else:
            # Subsequent iterations: likely above threshold
            conf = rng.randint(confidence_threshold, min(100, confidence_threshold + 12))
        passed = conf >= confidence_threshold
        return passed, float(conf)
    else:
        # Syntactic check: 95% pass rate
        passed = rng.random() < 0.95
        return passed, None
