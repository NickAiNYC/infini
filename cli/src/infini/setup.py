"""Slash command installer.

Attribution: installer pattern from Squad (https://github.com/mco-org/squad).
Detects Claude Code, Gemini CLI, or Codex and creates slash command files
so users can type /infini inside their AI terminal.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from .db import init_db
from rich.console import Console

console = Console()


def detect_terminals() -> list[str]:
    """Detect which AI terminals are installed."""
    terminals = []
    for name, cmd in [("claude", "claude"), ("gemini", "gemini"), ("codex", "codex")]:
        if shutil.which(cmd):
            terminals.append(name)
    return terminals


CLAUDE_COMMAND = """---
description: Run an INFINI Loopfile
---

Run `infini run $ARGUMENTS` and stream the output. After completion, run `infini inspect runs/latest/` to show the trace summary.
"""

GEMINI_COMMAND = """# INFINI
Run `infini run $ARGUMENTS` and show the output. Then run `infini inspect runs/latest/` for the trace.
"""

CODEX_COMMAND = """# INFINI
Run `infini run $ARGUMENTS` and show the output. Then run `infini inspect runs/latest/` for the trace.
"""


def setup_claude() -> dict:
    """Create the /infini slash command for Claude Code."""
    cmd_dir = Path.home() / ".claude" / "commands"
    cmd_dir.mkdir(parents=True, exist_ok=True)
    cmd_file = cmd_dir / "infini.md"
    cmd_file.write_text(CLAUDE_COMMAND)
    return {"terminal": "claude", "path": str(cmd_file), "status": "installed"}


def setup_gemini() -> dict:
    """Create the /infini slash command for Gemini CLI."""
    cmd_dir = Path.home() / ".gemini" / "commands"
    cmd_dir.mkdir(parents=True, exist_ok=True)
    cmd_file = cmd_dir / "infini.md"
    cmd_file.write_text(GEMINI_COMMAND)
    return {"terminal": "gemini", "path": str(cmd_file), "status": "installed"}


def setup_codex() -> dict:
    """Create the /infini slash command for Codex."""
    cmd_dir = Path.home() / ".codex" / "commands"
    cmd_dir.mkdir(parents=True, exist_ok=True)
    cmd_file = cmd_dir / "infini.md"
    cmd_file.write_text(CODEX_COMMAND)
    return {"terminal": "codex", "path": str(cmd_file), "status": "installed"}


def download_qwythos() -> dict:
    """Download the Qwythos GGUF model for local inference."""
    import urllib.request
    import json

    models_dir = Path.home() / ".infini" / "models"
    models_dir.mkdir(parents=True, exist_ok=True)

    model_path = models_dir / "qwythos-9b-q4_k_m.gguf"

    if model_path.exists():
        size_mb = model_path.stat().st_size / (1024 * 1024)
        return {"model": str(model_path), "size_mb": round(size_mb), "status": "exists"}

    url = "https://huggingface.co/Qwythos/Qwythos-9B-Claude-Mythos-5-1M-GGUF/resolve/main/Qwythos-9B-Claude-Mythos-5-1M-Q4_K_M.gguf"
    console.print(f"[yellow]Downloading Qwythos-9B GGUF (~5.6GB)...[/yellow]")
    console.print(f"[dim]  from: {url}[/dim]")
    console.print(f"[dim]  to:   {model_path}[/dim]")

    try:
        urllib.request.urlretrieve(url, model_path)
        size_mb = model_path.stat().st_size / (1024 * 1024)
        console.print(f"[green]✓ Downloaded: {model_path} ({round(size_mb)} MB)[/green]")
        return {"model": str(model_path), "size_mb": round(size_mb), "status": "downloaded"}
    except Exception as e:
        return {"model": str(model_path), "status": "error", "error": str(e)}


SETUP_FUNCTIONS = {
    "claude": setup_claude,
    "gemini": setup_gemini,
    "codex": setup_codex,
    "qwythos": setup_qwythos,
}


def run_setup() -> dict:
    """Run full setup: init DB + detect terminals + create slash commands.

    Returns a summary dict.
    """
    # Initialize the SQLite DB
    db_path = init_db()

    # Detect terminals
    terminals = detect_terminals()

    # Create slash commands for each detected terminal
    commands = []
    for t in terminals:
        if t in SETUP_FUNCTIONS:
            commands.append(SETUP_FUNCTIONS[t]())

    # Always create the skills directory
    skills_dir = Path.home() / ".infini" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    return {
        "db_path": str(db_path),
        "skills_dir": str(skills_dir),
        "terminals_detected": terminals,
        "commands_created": commands,
        "status": "complete" if commands else "no_terminals_found",
    }
