"""Observatory UI launcher — `infini ui`.

Launches the local Observatory web app. In V1, this serves the static
HTML mockups from assets/ and lets you drop a trace file to visualize it.
"""
from __future__ import annotations

import json
import webbrowser
from pathlib import Path

from rich.console import Console

console = Console()

# Path to the Observatory UI (Next.js app in observatory-ui/)
_UI_DIR = Path(__file__).parent.parent.parent.parent / "observatory-ui"


def launch_ui(trace_path: str | None = None, port: int = 3000) -> None:
    """Launch the Observatory UI.

    In V1, if the Next.js app is built, serve it. Otherwise, print
    instructions for running it manually.
    """
    console.print(f"[bold cyan]╔══════════════════════════════════════════════════════╗[/bold cyan]")
    console.print(f"[bold cyan]║[/bold cyan]  [bold]INFINI Loop Observatory[/bold]                          [bold cyan]║[/bold cyan]")
    console.print(f"[bold cyan]╚══════════════════════════════════════════════════════╝[/bold cyan]")
    console.print()

    if _UI_DIR.exists() and (_UI_DIR / "package.json").exists():
        # Next.js app exists — try to launch it
        console.print(f"[green]▶ Observatory UI found at {_UI_DIR}[/green]")
        console.print(f"[dim]  Starting Next.js dev server on port {port}...[/dim]")
        console.print()
        console.print(f"  [bold]Open:[/bold] [link=http://localhost:{port}]http://localhost:{port}[/link]")
        if trace_path:
            console.print(f"  [bold]Trace:[/bold] {trace_path}")
        console.print()
        console.print(f"[dim]  Press Ctrl+C to stop.[/dim]")

        import subprocess
        try:
            env = {"PORT": str(port), "PATH": __import__("os").environ.get("PATH", "")}
            import os
            env = {**os.environ, "PORT": str(port)}
            if trace_path:
                env["INFINI_TRACE"] = str(Path(trace_path).resolve())
            subprocess.run(
                ["npm", "run", "dev", "--", "--port", str(port)],
                cwd=str(_UI_DIR),
                env=env,
            )
        except KeyboardInterrupt:
            console.print("\n[yellow]Observatory stopped.[/yellow]")
        except FileNotFoundError:
            console.print("[yellow]npm not found. Install Node.js to run the Observatory UI.[/yellow]")
            console.print(f"[dim]  Or open the mockup directly: file://{_UI_DIR}/../assets/observatory.html[/dim]")
    else:
        # No Next.js app — serve the static mockup
        console.print(f"[yellow]▶ Observatory UI not built. Showing static mockup.[/yellow]")
        console.print()
        mockup = Path(__file__).parent.parent.parent.parent / "assets" / "observatory.html"
        if mockup.exists():
            console.print(f"  [bold]Open:[/bold] [link=file://{mockup}]file://{mockup}[/link]")
            webbrowser.open(f"file://{mockup}")
        else:
            console.print(f"  [red]Mockup not found at {mockup}[/red]")
        console.print()
        console.print(f"[dim]  To build the full UI: cd observatory-ui && npm install && npm run dev[/dim]")
