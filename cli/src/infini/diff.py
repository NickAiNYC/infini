"""Semantic diff — `infini diff`.

Produces a semantic diff between two Loopfiles or two traces, not a
line diff. Highlights changes to OBJECTIVE, AGENTS, STEPS, VERIFY,
BUDGET, STOP_WHEN.
"""
from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .parse import parse_file
from .trace import load_trace

console = Console()


def diff(v1: str | Path, v2: str | Path) -> None:
    """Diff two Loopfiles or two traces. Auto-detects which."""
    p1, p2 = Path(v1), Path(v2)

    # Auto-detect: is this a Loopfile (YAML) or a trace (JSON)?
    is_trace_1 = _is_trace(p1)
    is_trace_2 = _is_trace(p2)

    if is_trace_1 and is_trace_2:
        _diff_traces(p1, p2)
    elif not is_trace_1 and not is_trace_2:
        _diff_loopfiles(p1, p2)
    else:
        console.print("[red]Cannot diff a Loopfile against a trace. Both arguments must be the same type.[/red]")


def _is_trace(path: Path) -> bool:
    """Heuristic: is this file a trace (JSON with 'loopfile' key) or a Loopfile (YAML)?"""
    if not path.exists():
        return False
    text = path.read_text()
    try:
        data = json.loads(text)
        return isinstance(data, dict) and "loopfile" in data
    except json.JSONDecodeError:
        return False


def _diff_loopfiles(v1: Path, v2: Path) -> None:
    """Diff two Loopfiles."""
    lf1 = parse_file(v1)
    lf2 = parse_file(v2)

    console.print(f"\n[bold]INFINI diff[/bold] — Loopfiles")
    console.print(f"  [dim]v1: {v1}[/dim]")
    console.print(f"  [dim]v2: {v2}[/dim]\n")

    changes: list[str] = []

    # Objective
    if lf1.objective != lf2.objective:
        changes.append(f"[red]OBJECTIVE changed[/red]")
        console.print(f"  [red]- OBJECTIVE: {lf1.objective}[/red]")
        console.print(f"  [green]+ OBJECTIVE: {lf2.objective}[/green]")
    else:
        console.print(f"  [dim]OBJECTIVE: unchanged[/dim]")

    # Agents
    agents1 = {a.name: a for a in lf1.agents}
    agents2 = {a.name: a for a in lf2.agents}
    added = set(agents2) - set(agents1)
    removed = set(agents1) - set(agents2)
    if added:
        changes.append(f"[green]+{len(added)} agent(s) added[/green]")
        console.print(f"  [green]+ AGENTS: {', '.join(added)}[/green]")
    if removed:
        changes.append(f"[red]-{len(removed)} agent(s) removed[/red]")
        console.print(f"  [red]- AGENTS: {', '.join(removed)}[/red]")
    if not added and not removed:
        console.print(f"  [dim]AGENTS: unchanged[/dim]")

    # Steps
    steps1 = {s.id: s for s in lf1.steps}
    steps2 = {s.id: s for s in lf2.steps}
    added_s = set(steps2) - set(steps1)
    removed_s = set(steps1) - set(steps2)
    if added_s:
        changes.append(f"[green]+{len(added_s)} step(s) added[/green]")
        console.print(f"  [green]+ STEPS: {', '.join(added_s)}[/green]")
    if removed_s:
        changes.append(f"[red]-{len(removed_s)} step(s) removed[/red]")
        console.print(f"  [red]- STEPS: {', '.join(removed_s)}[/red]")
    if not added_s and not removed_s:
        console.print(f"  [dim]STEPS: unchanged[/dim]")

    # Verify
    v1_checks = set(lf1.verify.syntactic + lf1.verify.semantic)
    v2_checks = set(lf2.verify.syntactic + lf2.verify.semantic)
    added_v = v2_checks - v1_checks
    removed_v = v1_checks - v2_checks
    if added_v:
        changes.append(f"[green]+{len(added_v)} verification check(s) added[/green]")
        console.print(f"  [green]+ VERIFY: {', '.join(added_v)}[/green]")
    if removed_v:
        changes.append(f"[red]-{len(removed_v)} verification check(s) removed[/red]")
        console.print(f"  [red]- VERIFY: {', '.join(removed_v)}[/red]")
    if lf1.verify.confidence_threshold != lf2.verify.confidence_threshold:
        changes.append(f"[yellow]~ confidence_threshold: {lf1.verify.confidence_threshold} → {lf2.verify.confidence_threshold}[/yellow]")
        console.print(f"  [yellow]~ confidence_threshold: {lf1.verify.confidence_threshold} → {lf2.verify.confidence_threshold}[/yellow]")
    if not added_v and not removed_v and lf1.verify.confidence_threshold == lf2.verify.confidence_threshold:
        console.print(f"  [dim]VERIFY: unchanged[/dim]")

    # Budget
    if lf1.budget.dollars != lf2.budget.dollars:
        changes.append(f"[yellow]~ BUDGET dollars: ${lf1.budget.dollars} → ${lf2.budget.dollars}[/yellow]")
        console.print(f"  [yellow]~ BUDGET dollars: ${lf1.budget.dollars} → ${lf2.budget.dollars}[/yellow]")
    if lf1.budget.minutes != lf2.budget.minutes:
        changes.append(f"[yellow]~ BUDGET minutes: {lf1.budget.minutes} → {lf2.budget.minutes}[/yellow]")
        console.print(f"  [yellow]~ BUDGET minutes: {lf1.budget.minutes}m → {lf2.budget.minutes}m[/yellow]")
    if lf1.budget.dollars == lf2.budget.dollars and lf1.budget.minutes == lf2.budget.minutes:
        console.print(f"  [dim]BUDGET: unchanged[/dim]")

    # Summary
    console.print(f"\n[bold]Summary[/bold]")
    if not changes:
        console.print(f"  [green]No semantic changes. The two Loopfiles are equivalent.[/green]")
    else:
        for c in changes:
            console.print(f"  {c}")

    # Compatibility classification
    if any("[red]" in c for c in changes):
        console.print(f"\n  [red]This is a BREAKING change.[/red]")
    elif any("[yellow]" in c for c in changes):
        console.print(f"\n  [yellow]This is a COMPATIBLE change.[/yellow]")
    elif added or added_s or added_v:
        console.print(f"\n  [green]This is an ADDITIVE change.[/green]")


def _diff_traces(v1: Path, v2: Path) -> None:
    """Diff two traces."""
    t1 = load_trace(v1)
    t2 = load_trace(v2)

    console.print(f"\n[bold]INFINI diff[/bold] — Traces")
    console.print(f"  [dim]v1: {v1}[/dim]")
    console.print(f"  [dim]v2: {v2}[/dim]\n")

    table = Table(show_header=True, header_style="bold")
    table.add_column("Metric")
    table.add_column("v1", justify="right")
    table.add_column("v2", justify="right")
    table.add_column("Delta", justify="right")

    b1, b2 = t1.get("budget", {}), t2.get("budget", {})
    d_cost = b2.get("spent_dollars", 0) - b1.get("spent_dollars", 0)
    d_time = b2.get("spent_minutes", 0) - b1.get("spent_minutes", 0)

    table.add_row("Outcome", t1.get("outcome", "?"), t2.get("outcome", "?"), "")
    table.add_row("Iterations", str(t1.get("iterations", 0)), str(t2.get("iterations", 0)), "")
    table.add_row("Steps", str(len(t1.get("steps", []))), str(len(t2.get("steps", []))), "")
    table.add_row("Cost", f"${b1.get('spent_dollars', 0):.2f}", f"${b2.get('spent_dollars', 0):.2f}",
                  f"[{'red' if d_cost > 0 else 'green'}]{'+' if d_cost > 0 else ''}${d_cost:.2f}[/]")
    table.add_row("Time", f"{b1.get('spent_minutes', 0):.1f}m", f"{b2.get('spent_minutes', 0):.1f}m",
                  f"[{'red' if d_time > 0 else 'green'}]{'+' if d_time > 0 else ''}{d_time:.1f}m[/]")

    console.print(table)
