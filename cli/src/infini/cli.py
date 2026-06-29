"""INFINI CLI — the entry point.

Usage:
    infini validate <loopfile>
    infini run <loopfile> [--mock] [--plan] [--output <dir>]
    infini inspect <run_dir> [--web]
    infini replay <run_dir> [--step <id>] [--freeze-model-calls]
    infini diff <v1> <v2>
    infini ui [<trace>]
    infini engines
    infini task <create|ack|complete|list|wait> ...
    infini skill <list|install> ...
    infini setup
    infini init [--target <dir>] [--filename <name>]
    infini new <name>
    infini graph <loopfile>
    infini benchmark <loopfile>
    infini conformance <dir>
    infini certify <adapter>
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
from .db import init_db
from . import task_manager
from . import memory
from . import skills
from . import orchestrator
from . import setup as setup_mod
from .registry_cli import register_registry_commands

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
@click.option("--plan", is_flag=True, help="Use 3-agent orchestration (Planner/Worker/Inspector).")
@click.option("--engine", "-e", default="infini",
              type=click.Choice(["infini", "reference", "langgraph", "crewai", "autogen", "mastra", "openai-agents", "codemap"]),
              help="Execution engine: infini (default), reference, langgraph, crewai, autogen, mastra, openai-agents, codemap.")
@click.option("-o", "--output", default="runs/latest", help="Output directory for the trace.")
@click.option("--max-iterations", default=5, help="Hard cap on iterations.")
@click.option("--work-dir", default=".", type=click.Path(file_okay=False),
              help="Working directory for real filesystem verification. Defaults to current directory. "
                   "When set, syntactic VERIFY checks run against real files/subprocesses.")
@click.option("-q", "--quiet", is_flag=True, help="Suppress progress output.")
def run(loopfile: str, mock: bool, plan: bool, engine: str, output: str, max_iterations: int, work_dir: str | None, quiet: bool):
    """Run a Loopfile. Use --engine langgraph/crewai/autogen/mastra/openai-agents for adapters."""
    try:
        lf = parse_file(loopfile)
    except ParseError as e:
        console.print(f"[red]✗ invalid Loopfile[/red]")
        console.print(str(e))
        sys.exit(1)

    # Initialize DB on first run (best-effort)
    try:
        init_db()
    except Exception:
        pass

    # ── Engine routing ──
    if engine == "langgraph":
        import sys as _sys
        from pathlib import Path as _Path
        # Add adapters/langgraph to path
        _repo_root = _Path(__file__).parent.parent.parent.parent
        _sys.path.insert(0, str(_repo_root / "adapters" / "langgraph"))
        from langgraph_adapter import LangGraphAdapter

        adapter = LangGraphAdapter()
        trace = adapter.run(
            lf, mock=mock, output_dir=output,
            max_iterations=max_iterations, verbose=not quiet,
        )

        # Store to memory
        try:
            for step_trace in trace.steps:
                memory.store_run_output(
                    lf.name, step_trace.id, step_trace.name,
                    f"status={step_trace.status} cost=${step_trace.cost['dollars']:.2f}"
                )
        except Exception:
            pass

        if trace.outcome == "verified":
            console.print(f"\n[green]✓ shipped (langgraph).[/green] trace: {Path(output) / 'run.json'}")
        elif trace.outcome == "budget_exceeded":
            console.print(f"\n[red]✗ budget exceeded.[/red] trace: {Path(output) / 'run.json'}")
            sys.exit(1)
        else:
            console.print(f"\n[yellow]⚠ unverified.[/yellow] trace: {Path(output) / 'run.json'}")
            sys.exit(1)
        return

    if engine == "codemap":
        import sys as _sys
        from pathlib import Path as _Path
        _repo_root = _Path(__file__).parent.parent.parent.parent
        _sys.path.insert(0, str(_repo_root / "adapters" / "codemap"))
        from codemap_adapter import CodemapAdapter

        from .parse import to_dict
        lf_dict = to_dict(lf)
        adapter = CodemapAdapter()
        trace = adapter.execute(lf_dict)

        console.print(f"\n[green]✓ context-aware (codemap).[/green] trace: {Path(output) / 'run.json'}")
        console.print(f"[dim]  intent: {trace.get('metadata', {}).get('intent', '?')}[/dim]")
        skills = trace.get("metadata", {}).get("skills", [])
        if skills:
            console.print(f"[dim]  matched skills: {', '.join(s['name'] for s in skills[:3])}[/dim]")
        return

    if plan:
        # 3-agent orchestration mode
        from .parse import to_dict
        steps_raw = to_dict(lf).get("STEPS", [])
        result = orchestrator.run_planned(
            loopfile_name=lf.name,
            objective=lf.objective,
            steps=steps_raw,
            output_dir=output,
            verbose=not quiet,
        )
        console.print(f"\n[green]✓ orchestrated.[/green] plan: {result['plan']}")
        console.print(f"[dim]  output: {result['output']}[/dim]")
        console.print(f"[dim]  review: {result['review']}[/dim]")
        return

    if not mock:
        # Live execution via MCP — talks to real LLMs
        from .live_engine import run_live
        try:
            trace = run_live(
                lf,
                output_dir=output,
                max_iterations=max_iterations,
                verbose=not quiet,
            )
        except RuntimeError as e:
            console.print(f"[red]✗ {e}[/red]")
            sys.exit(1)

        # Store to memory
        try:
            for step_trace in trace.steps:
                memory.store_run_output(
                    lf.name, step_trace.id, step_trace.name,
                    f"status={step_trace.status} cost=${step_trace.cost['dollars']:.2f}"
                )
        except Exception:
            pass

        if trace.outcome == "verified":
            console.print(f"\n[green]✓ shipped (live).[/green] trace: {Path(output) / 'run.json'}")
        elif trace.outcome == "budget_exceeded":
            console.print(f"\n[red]✗ budget exceeded.[/red] trace: {Path(output) / 'run.json'}")
            sys.exit(1)
        else:
            console.print(f"\n[yellow]⚠ unverified.[/yellow] trace: {Path(output) / 'run.json'}")
            sys.exit(1)
        return

    trace = run_loop(
        lf,
        output_dir=output,
        mock=mock,
        max_iterations=max_iterations,
        verbose=not quiet,
        working_dir=work_dir,
    )

    # Store run output to memory (best-effort, doesn't affect trace)
    try:
        for step_trace in trace.steps:
            memory.store_run_output(
                lf.name, step_trace.id, step_trace.name,
                f"status={step_trace.status} cost=${step_trace.cost['dollars']:.2f}"
            )
    except Exception:
        pass

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

    # Also list installed skills
    try:
        installed_skills = skills.list_skills()
        if installed_skills:
            console.print(f"\n[bold]Installed skills[/bold] (~/.infini/skills/)")
            stable = Table(box=box.SIMPLE)
            stable.add_column("Name", style="cyan")
            stable.add_column("Version")
            stable.add_column("Description")
            for s in installed_skills:
                stable.add_row(
                    s.get("name", "—"),
                    s.get("version", "—"),
                    s.get("description", "—")[:60],
                )
            console.print(stable)
    except Exception:
        pass


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
@click.option("--filename", "-f", default="Loopfile.yaml", help="Loopfile name.")
@click.option("--pattern", "-p", default=None,
              help="Scaffold from a canonical pattern (daily-triage, pr-babysitter, ci-sweeper, issue-triage, changelog-drafter).")
def init(target: str, filename: str, pattern: str | None):
    """Scaffold a loop project: Loopfile + supporting files.

    \b
    Without --pattern: creates a minimal starter Loopfile.
    With --pattern: scaffolds a full working loop from a canonical pattern.

    \b
    Examples:
      infini init                              # minimal starter
      infini init --pattern daily-triage       # full daily-triage loop
      infini init --pattern ci-sweeper -t ./my-sweeper
    """
    from .patterns import get_pattern, list_patterns, pattern_names

    target_path = Path(target).resolve()
    target_path.mkdir(parents=True, exist_ok=True)

    if pattern:
        p = get_pattern(pattern)
        if p is None:
            console.print(f"[red]✗ unknown pattern: {pattern}[/red]")
            console.print(f"[dim]  available: {', '.join(pattern_names())}[/dim]")
            sys.exit(1)
        created = p.scaffold(target_path)
        console.print(Panel.fit(
            f"Pattern: [cyan]{p.name}[/cyan]\n"
            f"Cadence: [dim]{p.cadence}[/dim]\n"
            f"Target:  [cyan]{target_path}[/cyan]\n\n"
            f"[green]Created {len(created)} file(s):[/green]",
            title="infini init --pattern",
        ))
        for f in created:
            console.print(f"  ✓ {f.relative_to(target_path) if f.is_relative_to(target_path) else f}")
        console.print(f"\n[dim]Next: infini run {target_path / 'Loopfile.yaml'} --mock[/dim]")
        console.print(f"[dim]      infini audit {target_path}[/dim]")
    else:
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
            f"Initialized at [cyan]{target_path}[/cyan]\nLoopfile: [green]{lf}[/green]\n\n"
            f"[dim]Tip: use --pattern for a full working loop:[/dim]\n"
            f"[dim]  infini init --pattern daily-triage[/dim]",
            title="infini init",
        ))


@cli.command()
@click.argument("project_dir", required=False, default=".")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON instead of human-readable.")
def audit(project_dir: str, as_json: bool):
    """Audit a project for loop readiness — returns a 0-100 score with fixes.

    \b
    Scans for 12 infrastructure signals:
      Loopfile, STATE.md, verifier agent, safety docs, MCP config,
      budget docs, LOOP.md, AGENTS.md, CI workflows, recent activity,
      lessons file, replay trace.

    \b
    Maturity levels:
      L0 Draft       (0-24)   — aspirational, no infrastructure
      L1 Report-only  (25-49) — runs but no durable artifacts
      L2 Assisted    (50-74)  — has state, verification, replay
      L3 Unattended  (75-100) — production-ready with CI + safety

    \b
    Examples:
      infini audit                    # audit current directory
      infini audit ./my-project       # audit a specific project
      infini audit --json             # machine-readable output
    """
    from .audit import audit_project

    result = audit_project(project_dir)

    if as_json:
        import json as _json
        print(_json.dumps(result.to_dict(), indent=2))
        return

    console.rule(f"[bold]INFINI Audit — {result.project_dir}[/bold]")
    console.print()

    score_color = "green" if result.score >= 75 else "yellow" if result.score >= 50 else "red"
    console.print(f"  Score:    [{score_color}]{result.score}/{result.max_score}[/{score_color}] ({result.percentage}%)")
    console.print(f"  Maturity: [bold]{result.maturity_level}[/bold]")
    console.print()

    console.print(f"[green]✓ Found ({len(result.found_signals)}):[/green]")
    for s in result.found_signals:
        console.print(f"  [green]+{s.points:>2}[/green] {s.name:20s} [dim]{s.detail}[/dim]")

    console.print()

    if result.missing_signals:
        console.print(f"[red]✗ Missing ({len(result.missing_signals)}):[/red]")
        for s in result.missing_signals:
            console.print(f"  [red]-{s.points:>2}[/red] {s.name:20s} [dim]{s.fix}[/dim]")
    else:
        console.print("[green]All signals present. Production-ready.[/green]")

    console.print()

    if result.missing_signals:
        console.print("[bold]Suggested next steps:[/bold]")
        for s in result.missing_signals[:3]:
            console.print(f"  → {s.fix}")
        if len(result.missing_signals) > 3:
            console.print(f"  [dim]...and {len(result.missing_signals) - 3} more[/dim]")

    sys.exit(0 if result.score >= 50 else 1)


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


# ════════════════════════════════════════════════════════════
# Phase 1: Task management (adapted from Squad)
# ════════════════════════════════════════════════════════════

@cli.group()
def task():
    """Manage tasks on the SQLite coordination bus."""
    pass


@task.command(name="create")
@click.argument("title")
@click.option("--body", default="", help="Task body/instructions.")
@click.option("--assign", default="", help="Assign to a worker role.")
def task_create(title: str, body: str, assign: str):
    """Create a new task."""
    t = task_manager.create_task(title, body, assign)
    console.print(f"[green]✓[/green] Task {t['id']} created: {title}")
    console.print(f"[dim]  status: {t['status']}  assigned: {t.get('assigned_to', '—')}[/dim]")


@task.command(name="ack")
@click.argument("task_id")
@click.option("--worker", default="", help="Worker name claiming the task.")
def task_ack(task_id: str, worker: str):
    """Acknowledge a task."""
    t = task_manager.ack_task(task_id, worker)
    if t:
        console.print(f"[green]✓[/green] Task {task_id} acked by {t.get('assigned_to', '—')}")
    else:
        console.print(f"[red]✗[/red] Task {task_id} not found")


@task.command(name="complete")
@click.argument("task_id")
@click.option("--summary", default="done", help="Completion summary.")
def task_complete(task_id: str, summary: str):
    """Mark a task complete."""
    t = task_manager.complete_task(task_id, summary)
    if t:
        console.print(f"[green]✓[/green] Task {task_id} complete: {summary}")
    else:
        console.print(f"[red]✗[/red] Task {task_id} not found")


@task.command(name="list")
@click.option("--status", default="pending", help="Filter by status (pending|acked|in_progress|complete|failed|all).")
def task_list(status: str):
    """List tasks by status."""
    tasks = task_manager.list_tasks(status)
    if not tasks:
        console.print(f"[dim]No {status} tasks.[/dim]")
        return
    table = Table(box=box.SIMPLE)
    table.add_column("ID", style="cyan")
    table.add_column("Title")
    table.add_column("Status")
    table.add_column("Assigned")
    table.add_column("Summary", style="dim")
    for t in tasks:
        table.add_row(
            t["id"], t["title"], t["status"],
            t.get("assigned_to") or "—",
            (t.get("summary") or "")[:50],
        )
    console.print(table)


@task.command(name="wait")
@click.argument("task_id")
@click.option("--timeout", default=300, help="Timeout in seconds.")
def task_wait(task_id: str, timeout: int):
    """Block until a task reaches complete or failed."""
    console.print(f"[dim]Waiting for task {task_id} (timeout: {timeout}s)...[/dim]")
    result = task_manager.wait_task(task_id, timeout=timeout)
    if result:
        console.print(f"[green]✓[/green] Task {task_id}: {result['status']}")
        if result.get("summary"):
            console.print(f"[dim]  {result['summary']}[/dim]")
    else:
        console.print(f"[red]✗[/red] Timed out waiting for task {task_id}")


# ════════════════════════════════════════════════════════════
# Phase 3: Skill management (adapted from Anthropic Skills)
# ════════════════════════════════════════════════════════════

@cli.group()
def skill():
    """Manage skills from ~/.infini/skills/."""
    pass


@skill.command(name="list")
def skill_list():
    """List installed skills."""
    installed = skills.list_skills()
    if not installed:
        console.print("[dim]No skills installed. Use `infini skill install <git-url>` to add one.[/dim]")
        return
    table = Table(box=box.SIMPLE)
    table.add_column("Name", style="cyan")
    table.add_column("Version")
    table.add_column("Description")
    for s in installed:
        table.add_row(
            s.get("name", "—"),
            s.get("version", "—"),
            s.get("description", "—")[:60],
        )
    console.print(table)


@skill.command(name="install")
@click.argument("git_url")
def skill_install(git_url: str):
    """Install a skill from a git URL."""
    console.print(f"[dim]Cloning {git_url}...[/dim]")
    result = skills.install_skill(git_url)
    if result["status"] == "installed":
        console.print(f"[green]✓[/green] Skill '{result['name']}' installed to {result['path']}")
    elif result["status"] == "already_installed":
        console.print(f"[yellow]⚠[/yellow] Skill '{result['name']}' already installed at {result['path']}")
    elif result["status"] == "no_skill_md":
        console.print(f"[red]✗[/red] Cloned, but no SKILL.md found. Not a valid skill.")
    else:
        console.print(f"[red]✗[/red] Failed: {result.get('error', 'unknown')}")


# ════════════════════════════════════════════════════════════
# Phase 5: Setup (adapted from Squad installer)
# ════════════════════════════════════════════════════════════

@cli.command()
@click.option("--download-qwythos", is_flag=True, help="Download the Qwythos GGUF model for local inference (~5.6GB).")
def setup(download_qwythos: bool):
    """Initialize INFINI: create DB, detect AI terminals, install slash commands.

    Use --download-qwythos to download the local LLM model for --engine local mode.
    """
    console.rule("[bold]INFINI Setup[/bold]")

    if download_qwythos:
        console.print("[bold]Downloading Qwythos model...[/bold]")
        result = setup_mod.download_qwythos()
        if result.get("status") == "error":
            console.print(f"[red]✗ Download failed: {result.get('error')}[/red]")
            sys.exit(1)
        console.print(f"[green]✓ Model ready: {result['model']} ({result.get('size_mb', '?')} MB)[/green]")
        console.print(f"[dim]  Run: infini run loop.yaml --engine local --live[/dim]")
        return

    result = setup_mod.run_setup()

    console.print(f"\n[green]✓[/green] Database: {result['db_path']}")
    console.print(f"[green]✓[/green] Skills dir: {result['skills_dir']}")

    if result["terminals_detected"]:
        console.print(f"\n[green]✓[/green] Terminals detected: {', '.join(result['terminals_detected'])}")
        for cmd in result["commands_created"]:
            console.print(f"  [dim]→ {cmd['terminal']}: {cmd['path']}[/dim]")
        console.print(f"\n[bold]You can now type `/infini run loop.yaml` inside your AI terminal.[/bold]")
    else:
        console.print(f"\n[yellow]⚠[/yellow] No AI terminals detected (claude, gemini, codex).")
        console.print(f"[dim]  Install one to enable slash commands.[/dim]")

    console.print(f"\n[green]Setup complete.[/green]")


def main():
    """Entry point."""
    # Initialize DB on first CLI run (best-effort)
    try:
        init_db()
    except Exception:
        pass
    # Register registry commands
    register_registry_commands(cli)
    cli()


if __name__ == "__main__":
    main()
