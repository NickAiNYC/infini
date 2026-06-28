"""INFINI CLI — the entry point.

Usage:
    infini validate <loopfile>
    infini run <loopfile> [--mock] [--output <dir>]
    infini inspect <run_dir>
    infini replay <run_dir> [--step <id>] [--freeze-model-calls]
    infini diff <v1> <v2>
    infini ui [<trace>]
    infini engines
    infini --version
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console

from . import __version__
from .parse import parse_file, ParseError
from .engine import run as run_loop
from .inspect import inspect as inspect_trace
from .replay import replay as replay_trace
from .diff import diff as diff_cmd
from .ui import launch_ui

console = Console()


@click.group(invoke_without_command=True)
@click.version_option(__version__, prog_name="infini")
def cli():
    """INFINI — the open standard for agent loops.

    Write a Loopfile, run it on any engine.

    \b
    Quickstart:
        infini validate loop.yaml
        infini run loop.yaml --mock
        infini inspect runs/latest/
        infini replay runs/latest/ --step s3
        infini ui runs/latest/run.json
    """


@cli.command()
@click.argument("loopfile", type=click.Path(exists=True))
def validate(loopfile: str):
    """Validate a Loopfile against the spec."""
    try:
        lf = parse_file(loopfile)
        console.print(f"[green]✓ valid[/green]  {lf.name}@{lf.version}  (LOOPFILE-{lf.spec_version})")
        console.print(f"  [dim]objective: {lf.objective}[/dim]")
        console.print(f"  [dim]agents: {len(lf.agents)}  steps: {len(lf.steps)}  verify: {len(lf.verify.syntactic)} syntactic + {len(lf.verify.semantic)} semantic[/dim]")
        console.print(f"  [dim]budget: ${lf.budget.dollars} / {lf.budget.minutes}m[/dim]")
    except ParseError as e:
        console.print(f"[red]✗ invalid[/red]")
        console.print(str(e))
        sys.exit(1)


@cli.command()
@click.argument("loopfile", type=click.Path(exists=True))
@click.option("--mock/--live", default=True, help="Use mock LLM (default) or live execution.")
@click.option("-o", "--output", default="runs/latest", help="Output directory for the trace.")
@click.option("--max-iterations", default=5, help="Hard cap on iterations.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress progress output.")
def run(loopfile: str, mock: bool, output: str, max_iterations: int, quiet: bool):
    """Run a Loopfile."""
    try:
        lf = parse_file(loopfile)
    except ParseError as e:
        console.print(f"[red]✗ invalid Loopfile[/red]")
        console.print(str(e))
        sys.exit(1)

    trace = run_loop(
        lf,
        output_dir=output,
        mock=mock,
        max_iterations=max_iterations,
        verbose=not quiet,
    )

    if trace.outcome == "verified":
        console.print(f"\n[green]✓ shipped.[/green] trace: {Path(output) / 'run.json'}")
    elif trace.outcome == "budget_exceeded":
        console.print(f"\n[red]✗ budget exceeded.[/red] trace: {Path(output) / 'run.json'}")
        sys.exit(1)
    else:
        console.print(f"\n[yellow]⚠ unverified.[/yellow] trace: {Path(output) / 'run.json'}")
        sys.exit(1)


@cli.command()
@click.argument("run_dir", type=click.Path(exists=True))
def inspect(run_dir: str):
    """Inspect a run trace."""
    inspect_trace(run_dir)


@cli.command()
@click.argument("run_dir", type=click.Path(exists=True))
@click.option("--step", default=None, help="Step ID to replay from.")
@click.option("--freeze-model-calls", is_flag=True, help="Reuse original model responses (bit-exact).")
@click.option("-o", "--output", default=None, help="Output directory for the replay trace.")
def replay(run_dir: str, step: str | None, freeze_model_calls: bool, output: str | None):
    """Replay a run from a specific step."""
    replay_trace(run_dir, from_step=step, freeze_model_calls=freeze_model_calls, output_dir=output)


@cli.command()
@click.argument("v1", type=click.Path(exists=True))
@click.argument("v2", type=click.Path(exists=True))
def diff(v1: str, v2: str):
    """Semantic diff between two Loopfiles or two traces."""
    diff_cmd(v1, v2)


@cli.command()
@click.argument("trace", required=False, type=click.Path(exists=True))
@click.option("--port", default=3000, help="Port for the Observatory UI.")
def ui(trace: str | None, port: int):
    """Launch the Loop Observatory UI."""
    launch_ui(trace_path=trace, port=port)


@cli.command()
def engines():
    """List compatible engines."""
    console.print("[bold]Compatible engines[/bold]\n")
    engines = [
        ("INFINI Reference", "1.0.0", "✅", "✅", "✅", "✅", "✅", "✅"),
        ("Hermes", "1.0.0", "✅", "✅", "✅", "✅", "✅", "🚧"),
        ("OpenClaw", "1.0.0", "✅", "✅", "✅", "✅", "🚧", "🚧"),
        ("LangGraph", "—", "✅", "🚧", "🚧", "🚧", "🚧", "🚧"),
        ("CrewAI", "—", "🚧", "🚧", "❌", "❌", "❌", "❌"),
        ("AutoGen", "—", "🚧", "🚧", "🚧", "🚧", "❌", "❌"),
        ("OpenAI Agents SDK", "—", "🚧", "🚧", "🚧", "🚧", "❌", "🚧"),
        ("Claude Code", "—", "🚧", "🚧", "🚧", "🚧", "🚧", "🚧"),
        ("Gemini", "—", "🚧", "❌", "❌", "❌", "❌", "❌"),
    ]
    console.print(f"  {'Engine':<22} {'Version':<8} {'Parse':<6} {'Run':<5} {'Verify':<7} {'Inspect':<8} {'Replay':<7} {'Diff':<5}")
    console.print(f"  {'─'*22} {'─'*8} {'─'*6} {'─'*5} {'─'*7} {'─'*8} {'─'*7} {'─'*5}")
    for e in engines:
        console.print(f"  {e[0]:<22} {e[1]:<8} {e[2]:<6} {e[3]:<5} {e[4]:<7} {e[5]:<8} {e[6]:<7} {e[7]:<5}")
    console.print(f"\n[dim]See spec/compatibility.md for the full matrix.[/dim]")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
