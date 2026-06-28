"""Trace inspector — `infini inspect`.

Prints a human-readable summary of a trace to the terminal.
The Observatory UI (infini ui) provides the full visual experience.
"""
from __future__ import annotations

from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from .trace import load_trace

console = Console()


def inspect(run_dir: str | Path) -> None:
    """Inspect a run trace. Prints a summary to stdout."""
    run_dir = Path(run_dir)
    trace_path = run_dir / "run.json" if (run_dir / "run.json").exists() else run_dir
    trace = load_trace(trace_path)

    # Header
    console.print(Panel.fit(
        f"[bold]{trace.get('loopfile', 'unknown')}[/bold]\n"
        f"engine: {trace.get('engine', {}).get('type', '?')}  ·  "
        f"outcome: {_outcome_color(trace.get('outcome', '?'))}  ·  "
        f"iterations: {trace.get('iterations', 0)}",
        border_style="bright_blue",
    ))

    # Budget
    budget = trace.get("budget", {})
    console.print(f"\n[bold]Budget[/bold]")
    console.print(f"  dollars: ${budget.get('spent_dollars', 0):.2f}")
    console.print(f"  minutes: {budget.get('spent_minutes', 0):.1f}m")

    # Steps
    steps = trace.get("steps", [])
    if steps:
        table = Table(title="\nSteps", show_lines=False)
        table.add_column("ID", style="dim")
        table.add_column("Name", style="bold")
        table.add_column("Status")
        table.add_column("Cost", justify="right")
        table.add_column("Time", justify="right")
        table.add_column("Artifacts", style="dim")

        for s in steps:
            status = s.get("status", "?")
            status_str = f"[green]✓ {status}[/green]" if status == "ok" else f"[yellow]⚠ {status}[/yellow]"
            cost = s.get("cost", {})
            table.add_row(
                s.get("id", ""),
                s.get("name", ""),
                status_str,
                f"${cost.get('dollars', 0):.2f}",
                f"{cost.get('minutes', 0):.1f}m",
                ", ".join(s.get("artifacts", [])) or "—",
            )
        console.print(table)

    # Verifications
    verifs = trace.get("verifications", [])
    if verifs:
        vtable = Table(title="\nVerification")
        vtable.add_column("Check", style="bold")
        vtable.add_column("Status")
        vtable.add_column("Confidence", justify="right")
        for v in verifs:
            status = v.get("status", "?")
            status_str = f"[green]PASS[/green]" if status == "pass" else f"[red]FAIL[/red]"
            conf = v.get("confidence")
            conf_str = f"{conf:.0f}" if conf is not None else "—"
            vtable.add_row(v.get("check", ""), status_str, conf_str)
        console.print(vtable)

    # Lessons
    lessons = trace.get("lessons", [])
    if lessons:
        console.print(f"\n[bold]Lessons[/bold]")
        for l in lessons:
            console.print(f"  • {l}")

    # Footer
    console.print(f"\n[dim]Trace: {trace_path}[/dim]")
    console.print(f"[dim]Open in Observatory: infini ui {trace_path}[/dim]")


def _outcome_color(outcome: str) -> str:
    colors = {
        "verified": "[green]verified[/green]",
        "unverified": "[red]unverified[/red]",
        "budget_exceeded": "[red]budget_exceeded[/red]",
        "escalated": "[yellow]escalated[/yellow]",
        "error": "[red]error[/red]",
        "running": "[blue]running[/blue]",
    }
    return colors.get(outcome, outcome)
