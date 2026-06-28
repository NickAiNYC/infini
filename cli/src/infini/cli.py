"""INFINI CLI — the entry point.

Usage:
    infini validate <loopfile>
    infini run <loopfile> [--mock] [--output <dir>]
    infini inspect <run_dir> [--web]
    infini replay <run_dir> [--step <id>] [--freeze-model-calls]
    infini diff <v1> <v2>
    infini ui [<trace>]
    infini engines
    infini init [--target <dir>] [--filename <name>]
    infini new <name>
    infini graph <loopfile>
    infini benchmark <loopfile>
    infini --version
"""
from __future__ import annotations

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from . import __version__
from .parse import parse_file, ParseError
from .engine import run as run_loop
from .inspect import inspect as inspect_trace
from .replay import replay as replay_trace
from .diff import diff as diff_cmd
from .ui import launch_ui
from .adapters import detect_adapters
from .conformance import run_conformance
from .certify import certify as certify_adapter, print_report as print_cert_report

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
@click.option("--web", is_flag=True, help="Open the Observatory UI in the browser (coming soon).")
def inspect(run_dir: str, web: bool):
    """Inspect a run trace. Use --web to open the Observatory UI (coming soon)."""
    inspect_trace(run_dir)
    if web:
        console.print("[blue]Observatory UI support is coming soon.[/blue]")
        console.print("[dim]For now, run `infini ui` separately to launch the Next.js dashboard.[/dim]")


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
    """List installed adapters and their capabilities (from adapter.yaml manifests)."""
    console.rule("[bold]Engines / Adapters (detected)")
    adapters = detect_adapters()
    if not adapters:
        console.print("[yellow]No adapters found under adapters/.[/yellow]")
        console.print("[dim]Adapters are discovered by scanning for adapter.yaml manifests.[/dim]")
        return
    table = Table(box=box.SIMPLE)
    table.add_column("Adapter", style="cyan")
    table.add_column("Version")
    table.add_column("Type")
    table.add_column("Capabilities", style="green")
    for a in adapters:
        m = a.get("manifest") or {}
        adapter_info = m.get("adapter", {}) if isinstance(m, dict) else {}
        name = adapter_info.get("name", a["name"])
        version = adapter_info.get("version", "?")
        atype = adapter_info.get("type", "?")
        caps = a.get("capabilities", [])
        caps_str = ", ".join(caps) if caps else "(none declared)"
        table.add_row(name, version, atype, caps_str)
    console.print(table)
    console.print("\n[dim]Full compatibility matrix: spec/compatibility.md[/dim]")
    console.print("[dim]Adapters without adapter.yaml are not listed.[/dim]")


@cli.command()
@click.argument("conformance_dir", type=click.Path(exists=True))
@click.option("--engine", default="infini", help="Engine to test against.")
@click.option("--mock/--live", default=True, help="Use mock mode (default).")
def conformance(conformance_dir: str, engine: str, mock: bool):
    """Run the conformance test suite against an engine."""
    exit_code = run_conformance(conformance_dir, engine=engine, mock=mock)
    if exit_code != 0:
        sys.exit(exit_code)


@cli.command()
@click.argument("adapter_path", type=click.Path(exists=True))
@click.option("--engine", default="infini", help="Engine to certify against.")
@click.option("--mock/--live", default=True, help="Use mock mode (default).")
@click.option("--conformance-dir", default=None, help="Conformance test directory (default: tests/conformance/).")
@click.option("-o", "--output", default=None, help="Output directory for certification report (default: registry/certifications/).")
def certify(adapter_path: str, engine: str, mock: bool, conformance_dir: str | None, output: str | None):
    """Certify an adapter against the INFINI spec."""
    report = certify_adapter(
        adapter_path,
        engine=engine,
        mock=mock,
        conformance_dir=conformance_dir,
        output_dir=output,
    )
    print_cert_report(report)
    console.print(f"\n[dim]JSON: registry/certifications/{report.adapter_name}.json[/dim]")
    console.print(f"[dim]Markdown: registry/certifications/{report.adapter_name}.md[/dim]")


@cli.command()
@click.option("--target", "-t", default=".", help="Directory to initialize.")
@click.option("--filename", "-f", default="Loopfile", help="Starter Loopfile name.")
def init(target: str, filename: str):
    """Scaffold a minimal loop project: Loopfile, loops/, state/, runs/."""
    target_path = Path(target).resolve()
    for d in ("loops", "state", "runs"):
        (target_path / d).mkdir(parents=True, exist_ok=True)
    lf = target_path / filename
    if not lf.exists():
        lf.write_text(
            'LOOPFILE: "1.0"\n'
            'name: my-loop\n'
            'version: 1.0.0\n'
            'OBJECTIVE: "Describe the objective here."\n'
            'AGENTS:\n'
            '  - { name: builder, role: builder, model_tier: sonnet }\n'
            'STEPS: []\n'
            'VERIFY:\n'
            '  syntactic: []\n'
            '  semantic: []\n'
            '  confidence_threshold: 80\n'
            'BUDGET: { dollars: 5, minutes: 15 }\n'
            'STOP_WHEN: ["all_verify_passed"]\n'
        )
    console.print(Panel.fit(
        f"Initialized at [cyan]{target_path}[/cyan]\nLoopfile: [green]{lf}[/green]",
        title="infini init",
    ))


@cli.command()
@click.argument("name")
def new(name: str):
    """Create a new loop project scaffold: <name>/Loopfile, state/, runs/, artifacts/.

    NAME is used both as the directory name and the Loopfile's name field.
    Use a simple slug (e.g. 'my-loop'), not a full path.
    """
    # Derive a clean slug from the name (last path component, lowercased)
    slug = Path(name).name.lower().replace(" ", "-")
    base = Path.cwd() / name
    base.mkdir(parents=True, exist_ok=True)
    for d in ("state", "runs", "artifacts"):
        (base / d).mkdir(exist_ok=True)
    lf = base / "Loopfile"
    if not lf.exists():
        lf.write_text(
            f'LOOPFILE: "1.0"\n'
            f'name: {slug}\n'
            f'version: 1.0.0\n'
            f'OBJECTIVE: "Describe the objective."\n'
            f'AGENTS:\n'
            f'  - {{ name: builder, role: builder, model_tier: sonnet }}\n'
            f'STEPS: []\n'
            f'VERIFY:\n'
            f'  syntactic: []\n'
            f'  semantic: []\n'
            f'  confidence_threshold: 80\n'
            f'BUDGET: {{ dollars: 5, minutes: 15 }}\n'
            f'STOP_WHEN: ["all_verify_passed"]\n'
        )
    console.print(Panel.fit(
        f"Created new project at [cyan]{base}[/cyan]\nLoopfile: [green]{lf}[/green]",
        title="infini new",
    ))


@cli.command()
@click.argument("loopfile", type=click.Path(exists=True))
def graph(loopfile: str):
    """Render a simple ASCII graph of the Loopfile's steps."""
    try:
        lf = parse_file(loopfile)
    except ParseError as e:
        console.print(f"[red]✗ invalid Loopfile[/red]")
        console.print(str(e))
        sys.exit(1)
    console.rule("[bold]Loop Graph")
    if not lf.steps:
        console.print("[yellow]No steps found to graph.[/yellow]")
        return
    for idx, s in enumerate(lf.steps):
        console.print(f"  [cyan]{s.id}[/cyan]  [bold]{s.name}[/bold]")
        if idx < len(lf.steps) - 1:
            console.print("  [dim]│[/dim]")
            console.print("  [dim]▼[/dim]")


@cli.command()
@click.argument("loopfile", type=click.Path(exists=True))
def benchmark(loopfile: str):
    """Produce a benchmark estimate (preview — real profiling coming later)."""
    try:
        lf = parse_file(loopfile)
    except ParseError as e:
        console.print(f"[red]✗ invalid Loopfile[/red]")
        console.print(str(e))
        sys.exit(1)
    n = len(lf.steps)
    console.rule("[bold]Benchmark Estimate — Preview")
    console.print("[dim]This is a preview. Real profiling requires running the loop.[/dim]\n")
    console.print(f"  Steps detected:     [bold]{n}[/bold]")
    console.print(f"  Runtime:            [yellow]Unknown[/yellow]  [dim](run `infini run` to measure)[/dim]")
    console.print(f"  Cost:               [yellow]Unknown[/yellow]  [dim](run `infini run` to measure)[/dim]")
    console.print(f"  Iterations:         [yellow]Unknown[/yellow]  [dim](depends on verification)[/dim]")
    console.print(f"  Confidence:         [yellow]Unknown[/yellow]  [dim](depends on semantic checks)[/dim]")
    console.print(f"\n  To get real numbers:\n    infini run {loopfile} --mock")


def main():
    """Entry point."""
    cli()


if __name__ == "__main__":
    main()
