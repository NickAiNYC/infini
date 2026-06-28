"""Replay engine — `infini replay`.

Replays a run from a specific step. In V1 (mock mode), this re-executes
from the named step using the same mock engine. The original trace is
preserved; the replay produces a new trace with `replay_of` pointing
back to the original.
"""
from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console

from .parse import parse_file
from .trace import load_trace, save_trace, new_trace, add_step, add_verification, finalize_trace
from .mock import mock_execute, mock_verify

console = Console()


def replay(
    run_dir: str | Path,
    from_step: str | None = None,
    mutations: dict | None = None,
    output_dir: str | Path | None = None,
    freeze_model_calls: bool = False,
) -> dict:
    """Replay a run from a specific step.

    Args:
        run_dir: Path to the original run directory (containing run.json).
        from_step: Step ID to replay from. If None, replays the whole run.
        mutations: Optional dict of input mutations.
        output_dir: Where to save the replay trace. Defaults to runs/replay-<timestamp>/.
        freeze_model_calls: If True, reuse the original model responses (bit-exact).

    Returns:
        The replay trace as a dict.
    """
    run_dir = Path(run_dir)
    trace_path = run_dir / "run.json" if (run_dir / "run.json").exists() else run_dir
    original = load_trace(trace_path)

    if from_step is None:
        from_step = original["steps"][0]["id"] if original.get("steps") else "s1"

    console.print(f"[bold]▶ replay[/bold] {original.get('loopfile', '?')} from step [cyan]{from_step}[/cyan]")

    if freeze_model_calls:
        console.print("[dim]  --freeze-model-calls: using cached model responses[/dim]")

    if mutations:
        console.print("[dim]  input mutations:[/dim]")
        for k, v in mutations.items():
            console.print(f"[dim]    {k}: {v}[/dim]")

    # In V1 mock mode: re-execute from the named step
    # A real implementation would restore state and resume; the mock just re-runs.
    replay_steps = []
    found_step = False
    for s in original.get("steps", []):
        if s["id"] == from_step:
            found_step = True
        if found_step:
            replay_steps.append(s)

    if not found_step:
        console.print(f"[red]Step {from_step} not found in trace[/red]")
        return {}

    # Create replay trace
    replay_trace = new_trace(
        original.get("loopfile", "replay"),
        json.dumps(original, default=str),
        engine_type="infini-reference-replay",
    )
    replay_trace.replay_of = str(trace_path)
    replay_trace.replay_from_step = from_step

    console.print(f"[dim]  re-executing {len(replay_steps)} step(s)[/dim]")
    for s in replay_steps:
        # In freeze mode, copy the original step's result
        if freeze_model_calls:
            from .trace import StepTrace
            replay_trace.steps.append(StepTrace(
                id=s["id"], name=s["name"], status=s.get("status", "ok"),
                started_at=s.get("started_at", ""), ended_at=s.get("ended_at", ""),
                cost=s.get("cost", {}),
                artifacts=s.get("artifacts", []),
                agent=s.get("agent", "builder"),
                action=s.get("action", ""),
                retry_attempt=s.get("retry_attempt"),
            ))
            replay_trace.budget["spent_dollars"] += s.get("cost", {}).get("dollars", 0)
            replay_trace.budget["spent_minutes"] += s.get("cost", {}).get("minutes", 0)
        else:
            # Re-execute (mock)
            result = mock_execute(
                step_id=s["id"], step_name=s["name"], action=s.get("action", ""),
                agent_role="builder", model_tier="sonnet",
                produces=s.get("artifacts", []),
                loopfile_name=original.get("loopfile", "replay"),
                iteration=original.get("iterations", 1),
            )
            add_step(
                replay_trace, s["id"], s["name"],
                agent=s.get("agent", "builder"), action=s.get("action", ""),
                artifacts=result.artifacts,
                cost_dollars=result.cost_dollars, cost_minutes=result.cost_minutes,
                tokens_in=result.tokens_in, tokens_out=result.tokens_out,
            )

        status_icon = "✓" if s.get("status") == "ok" else "⚠"
        console.print(f"  {status_icon} {s['id']} {s['name']}")

    # Copy verifications
    for v in original.get("verifications", []):
        from .trace import CheckResult
        replay_trace.verifications.append(CheckResult(
            check=v.get("check", ""), status=v.get("status", "pass"),
            confidence=v.get("confidence"), detail=v.get("detail"),
        ))

    finalize_trace(replay_trace, original.get("outcome", "verified"))
    replay_trace.iterations = 1

    # Save
    if output_dir is None:
        output_dir = f"runs/replay-{from_step}"
    out_path = save_trace(replay_trace, Path(output_dir) / "run.json")
    console.print(f"\n[green]✓ replay complete[/green]")
    console.print(f"[dim]  original: {trace_path}[/dim]")
    console.print(f"[dim]  replay:   {out_path}[/dim]")
    console.print(f"[dim]  diff:     infini diff {trace_path} {out_path}[/dim]")

    return replay_trace
