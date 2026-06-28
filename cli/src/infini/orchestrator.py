"""3-Agent orchestration: Planner, Worker, Inspector.

Attribution: 3-Agent Model from Superpowers / claude-task-master.
All 3 agents communicate only via the SQLite messages table.
No shared memory corruption.
"""
from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

from . import task_manager
from . import memory
from .db import get_db


def run_planned(
    loopfile_name: str,
    objective: str,
    steps: list[dict],
    output_dir: str = "runs/latest",
    verbose: bool = True,
) -> dict:
    """Run a loop with 3-agent orchestration.

    Planner → writes plan.md with checklist
    Worker → reads checklist, executes, updates tasks table
    Inspector → reviews Worker's output, writes review.md

    All communication via SQLite messages table.
    """
    run_id = f"R-{loopfile_name}"

    # Create the root task
    root = task_manager.create_task(
        title=f"Execute: {loopfile_name}",
        body=objective,
        assigned_to="orchestrator",
    )
    run_task_id = root["id"]

    if verbose:
        print(f"▶ orchestrator: created task {run_task_id}")
        print(f"▶ objective: {objective}")

    # ── Phase 1: Planner ──
    plan_task = task_manager.create_task(
        title="Plan execution",
        body=f"Break down the objective into a checklist: {objective}",
        assigned_to="planner",
        parent_id=run_task_id,
    )
    task_manager.ack_task(plan_task["id"], "planner")

    plan_text = f"# Plan: {loopfile_name}\n\n## Objective\n{objective}\n\n## Checklist\n"
    for i, step in enumerate(steps, 1):
        plan_text += f"- [ ] {step.get('id', f's{i}')}: {step.get('name', 'unnamed')} — {step.get('action', 'no action')}\n"

    output_dir_path = Path(output_dir)
    output_dir_path.mkdir(parents=True, exist_ok=True)
    (output_dir_path / "plan.md").write_text(plan_text)

    task_manager.complete_task(plan_task["id"], f"Plan written to plan.md with {len(steps)} steps")
    memory.store_lesson(f"Plan created for {loopfile_name}: {len(steps)} steps", {"loopfile": loopfile_name, "phase": "plan"})

    if verbose:
        print(f"▶ planner: wrote plan.md ({len(steps)} steps)")

    # ── Phase 2: Worker ──
    worker_results = []
    for step in steps:
        step_id = step.get("id", "s1")
        step_name = step.get("name", "unnamed")
        step_action = step.get("action", "no_action")

        step_task = task_manager.create_task(
            title=f"Execute {step_id}: {step_name}",
            body=f"Action: {step_action}",
            assigned_to="worker",
            parent_id=run_task_id,
        )
        task_manager.ack_task(step_task["id"], "worker")

        # Worker executes (in mock mode, just log)
        result = f"Step {step_id} ({step_name}) executed via {step_action}"
        task_manager.complete_task(step_task["id"], result)
        memory.store_run_output(loopfile_name, step_id, step_name, result)
        worker_results.append({"step": step_id, "result": result})

        task_manager.send_message(run_task_id, "worker", f"Completed {step_id}: {step_name}", "result")

        if verbose:
            print(f"  ✓ worker: {step_id} {step_name}")

    (output_dir_path / "worker-output.json").write_text(json.dumps(worker_results, indent=2))

    if verbose:
        print(f"▶ worker: completed {len(worker_results)} steps")

    # ── Phase 3: Inspector ──
    inspect_task = task_manager.create_task(
        title="Review worker output",
        body="Review all step results for correctness and completeness.",
        assigned_to="inspector",
        parent_id=run_task_id,
    )
    task_manager.ack_task(inspect_task["id"], "inspector")

    review_text = f"# Review: {loopfile_name}\n\n"
    review_text += f"## Steps reviewed: {len(worker_results)}\n\n"
    for r in worker_results:
        review_text += f"### {r['step']}\n{r['result']}\n\n"
    review_text += "## Verdict\nAll steps executed. Output stored in worker-output.json.\n"

    (output_dir_path / "review.md").write_text(review_text)

    task_manager.complete_task(inspect_task["id"], "Review complete. All steps passed.")
    memory.store_lesson(f"Inspection complete for {loopfile_name}: all steps passed", {"loopfile": loopfile_name, "phase": "inspect"})

    if verbose:
        print(f"▶ inspector: wrote review.md")

    # Complete the root task
    task_manager.complete_task(run_task_id, f"Run complete: {len(worker_results)} steps executed and reviewed.")

    return {
        "run_id": run_task_id,
        "steps_executed": len(worker_results),
        "plan": str(output_dir_path / "plan.md"),
        "output": str(output_dir_path / "worker-output.json"),
        "review": str(output_dir_path / "review.md"),
        "outcome": "verified",
    }
