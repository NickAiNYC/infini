"""Conformance test runner — `infini conformance`.

Runs every conformance test loop, compares the trace to expected.json,
and reports pass/fail per loop. This is the certification layer.
"""
from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from .parse import parse_file, ParseError
from .engine import run as run_loop

console = Console()


def run_conformance(
    conformance_dir: str | Path,
    engine: str = "infini",
    mock: bool = True,
    verbose: bool = True,
) -> int:
    """Run the conformance suite. Returns exit code (0 = all pass, 1 = some fail)."""
    conformance_dir = Path(conformance_dir)
    if not conformance_dir.exists():
        console.print(f"[red]Conformance directory not found: {conformance_dir}[/red]")
        return 2

    # Find all conformance test loops
    test_dirs = sorted(
        d for d in conformance_dir.iterdir()
        if d.is_dir() and (d / "Loopfile.yaml").exists()
    )

    if not test_dirs:
        console.print(f"[yellow]No conformance tests found in {conformance_dir}[/yellow]")
        return 0

    console.rule(f"[bold]INFINI Conformance Suite — {len(test_dirs)} tests[/bold]")
    console.print(f"[dim]  engine: {engine}  ·  mock: {mock}  ·  deterministic: True[/dim]\n")

    results = []
    for test_dir in test_dirs:
        loopfile_path = test_dir / "Loopfile.yaml"
        expected_path = test_dir / "expected.json"
        test_name = test_dir.name

        # Parse the Loopfile
        try:
            lf = parse_file(loopfile_path)
        except ParseError as e:
            results.append((test_name, "FAIL", f"parse error: {e}"))
            console.print(f"  [red]✗[/red] {test_name} — parse error")
            continue

        # Run the loop in deterministic mock mode
        run_dir = Path("runs/conformance") / test_name
        try:
            trace = run_loop(
                lf,
                output_dir=run_dir,
                mock=mock,
                max_iterations=5,
                verbose=False,
                deterministic=True,
            )
        except Exception as e:
            results.append((test_name, "FAIL", f"run error: {e}"))
            console.print(f"  [red]✗[/red] {test_name} — run error: {e}")
            continue

        # Compare against expected.json if it exists
        failures = []
        if expected_path.exists():
            try:
                expected = json.loads(expected_path.read_text())
            except json.JSONDecodeError as e:
                failures.append(f"expected.json invalid: {e}")
                expected = {}
        else:
            expected = {}

        # Check outcome
        expected_outcome = expected.get("expected_outcome", "verified")
        if trace.outcome != expected_outcome:
            failures.append(f"outcome: got {trace.outcome}, expected {expected_outcome}")

        # Check step count
        expected_steps = expected.get("expected_steps")
        if expected_steps is not None:
            actual_steps = len(trace.steps)
            if actual_steps != expected_steps:
                failures.append(f"steps: got {actual_steps}, expected {expected_steps}")

        # Check iterations within range
        max_iters = expected.get("max_iterations", 5)
        if trace.iterations > max_iters:
            failures.append(f"iterations: got {trace.iterations}, max {max_iters}")

        if failures:
            results.append((test_name, "FAIL", "; ".join(failures)))
            console.print(f"  [red]✗[/red] {test_name} — {'; '.join(failures)}")
        else:
            results.append((test_name, "PASS", f"outcome={trace.outcome}, steps={len(trace.steps)}, iters={trace.iterations}"))
            console.print(f"  [green]✓[/green] {test_name} — outcome={trace.outcome}, steps={len(trace.steps)}, iters={trace.iterations}")

    # Summary table
    console.print()
    table = Table(title="Conformance Results", show_lines=False)
    table.add_column("Test", style="bold")
    table.add_column("Result")
    table.add_column("Detail", style="dim")
    for name, result, detail in results:
        result_str = f"[green]PASS[/green]" if result == "PASS" else f"[red]FAIL[/red]"
        table.add_row(name, result_str, detail)
    console.print(table)

    passed = sum(1 for _, r, _ in results if r == "PASS")
    failed = sum(1 for _, r, _ in results if r == "FAIL")
    console.print(f"\n[bold]{passed} passed, {failed} failed[/bold]")

    return 0 if failed == 0 else 1
