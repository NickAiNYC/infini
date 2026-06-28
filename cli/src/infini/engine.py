"""INFINI Reference Engine.

Executes a Loopfile: runs the STEPS DAG, enforces BUDGET, runs VERIFY,
and emits a trace. In mock mode (default for V1), uses the mock LLM
engine so no API key is required.
"""
from __future__ import annotations

from pathlib import Path

from .parse import Loopfile, Step
from .trace import Trace, add_step, add_verification, finalize_trace, save_trace, new_trace
from .mock import mock_execute, mock_verify


class BudgetExceeded(Exception):
    pass


def run(
    loopfile: Loopfile,
    output_dir: str | Path = "runs/latest",
    mock: bool = True,
    max_iterations: int = 5,
    verbose: bool = True,
    deterministic: bool = False,
) -> Trace:
    """Execute a Loopfile. Returns the completed Trace.

    Args:
        loopfile: Parsed Loopfile to run.
        output_dir: Where to save the trace (run.json).
        mock: If True, use mock LLM (no API key needed).
        max_iterations: Hard cap on iterations (overrides STOP_WHEN if lower).
        verbose: Print progress to stdout.
        deterministic: If True, all verifiers pass on iteration 1 (for conformance).
    """
    trace = new_trace(loopfile.name, _serialize(loopfile))

    # Parse iterations>=N from STOP_WHEN to use as the run cap
    stop_when_cap = max_iterations
    for pred in loopfile.stop_when:
        if pred.startswith("iterations>="):
            try:
                stop_when_cap = min(stop_when_cap, int(pred.split(">=")[1]))
            except (ValueError, IndexError):
                pass
    effective_max = min(max_iterations, stop_when_cap)

    if verbose:
        _log(f"▶ engine: infini-reference {'(mock)' if mock else '(live)'}")
        _log(f"▶ reading state... none found, starting fresh")
        _log(f"▶ objective: {loopfile.objective}")
        _log(f"▶ budget: ${loopfile.budget.dollars} / {loopfile.budget.minutes}m")

    outcome = "unverified"
    lessons: list[str] = []

    for iteration in range(1, effective_max + 1):
        trace.iterations = iteration
        if verbose:
            _log(f"▶ iteration {iteration}")

        # Execute all steps
        for step in loopfile.steps:
            result = _execute_step(loopfile, step, iteration, mock)

            if result.status == "failed" and step.retry:
                # Retry
                for attempt in range(1, step.retry.get("max", 3) + 1):
                    if verbose:
                        _log(f"  ⚠ {step.id} {step.name} failed, retry {attempt}/{step.retry.get('max', 3)}")
                    result = _execute_step(loopfile, step, iteration, mock, retry_attempt=attempt)
                    if result.status == "ok":
                        break

            add_step(
                trace, step.id, step.name,
                agent=step.uses, action=step.action,
                artifacts=result.artifacts,
                cost_dollars=result.cost_dollars,
                cost_minutes=result.cost_minutes,
                tokens_in=result.tokens_in,
                tokens_out=result.tokens_out,
                status=result.status,
                retry_attempt=result.retry_attempt,
            )

            if verbose:
                status_icon = "✓" if result.status == "ok" else "⚠"
                _log(f"  {status_icon} {step.id} {step.name}  ${result.cost_dollars:.2f} · {result.cost_minutes:.1f}m")

            # Check budget
            if trace.budget["spent_dollars"] >= loopfile.budget.dollars:
                outcome = "budget_exceeded"
                if verbose:
                    _log(f"  ✗ budget exceeded (${trace.budget['spent_dollars']:.2f} / ${loopfile.budget.dollars})")
                finalize_trace(trace, outcome, lessons)
                save_trace(trace, Path(output_dir) / "run.json")
                return trace

            if trace.budget["spent_minutes"] >= loopfile.budget.minutes:
                outcome = "budget_exceeded"
                if verbose:
                    _log(f"  ✗ budget exceeded ({trace.budget['spent_minutes']:.1f}m / {loopfile.budget.minutes}m)")
                finalize_trace(trace, outcome, lessons)
                save_trace(trace, Path(output_dir) / "run.json")
                return trace

        # Run verification
        if verbose:
            _log(f"▶ verification:")
        all_passed = True
        confidences: list[float] = []

        for check in loopfile.verify.syntactic:
            passed, _ = mock_verify(check, loopfile.name, iteration, loopfile.verify.confidence_threshold, deterministic=deterministic) if mock else (True, None)
            add_verification(trace, check, passed, confidence=None)
            if verbose:
                _log(f"  {'✓' if passed else '✗'} {check}")
            if not passed:
                all_passed = False

        for check in loopfile.verify.semantic:
            passed, conf = mock_verify(check, loopfile.name, iteration, loopfile.verify.confidence_threshold, deterministic=deterministic) if mock else (True, 90.0)
            add_verification(trace, check, passed, confidence=conf)
            if conf is not None:
                confidences.append(conf)
            if verbose:
                _log(f"  {'✓' if passed else '✗'} {check} (conf {conf})" if conf else f"  {'✓' if passed else '✗'} {check}")
            if not passed:
                all_passed = False

        # Check confidence threshold
        if confidences:
            mean_conf = sum(confidences) / len(confidences)
            if mean_conf < loopfile.verify.confidence_threshold:
                all_passed = False
                if verbose:
                    _log(f"  ✗ mean confidence {mean_conf:.1f} < threshold {loopfile.verify.confidence_threshold}")

        if all_passed:
            outcome = "verified"
            lesson = f"{loopfile.name} shipped at iteration {iteration} with mean confidence {sum(confidences)/len(confidences):.1f}." if confidences else f"{loopfile.name} shipped at iteration {iteration}."
            lessons.append(lesson)
            if verbose:
                _log(f"✓ shipped. state saved. lessons appended.")
            break

        # Check stop conditions — effective_max already accounts for STOP_WHEN iterations>=N
        if iteration >= effective_max:
            break

    finalize_trace(trace, outcome, lessons)
    save_trace(trace, Path(output_dir) / "run.json")

    if verbose:
        _log(f"▶ cost: ${trace.budget['spent_dollars']:.2f} / ${loopfile.budget.dollars} · {trace.budget['spent_minutes']:.1f}m / {loopfile.budget.minutes}m")
        _log(f"▶ outcome: {outcome}")
        _log(f"▶ trace: {Path(output_dir) / 'run.json'}")

    return trace


def _execute_step(
    loopfile: Loopfile,
    step: Step,
    iteration: int,
    mock: bool,
    retry_attempt: int = 0,
):
    """Execute a single step. Returns a MockResult (or equivalent)."""
    if mock:
        # Find the agent
        agent = next((a for a in loopfile.agents if a.name == step.uses), None)
        model_tier = agent.model_tier if agent else "sonnet"
        role = agent.role if agent else "builder"
        return mock_execute(
            step_id=step.id, step_name=step.name, action=step.action,
            agent_role=role, model_tier=model_tier, produces=step.produces,
            loopfile_name=loopfile.name, iteration=iteration,
            retry_attempt=retry_attempt,
        )
    else:
        # Live mode: not implemented in V1 (requires adapter)
        raise NotImplementedError(
            "Live execution requires an engine adapter. Use --mock for now, "
            "or install infini-cli[hermes] / infini-cli[openclaw] when adapters ship."
        )


def _serialize(loopfile: Loopfile) -> str:
    """Serialize a Loopfile back to YAML for hashing."""
    import yaml
    from .parse import to_dict
    return yaml.dump(to_dict(loopfile), sort_keys=False, default_flow_style=False)


def _log(msg: str) -> None:
    """Print to stdout."""
    print(msg)
