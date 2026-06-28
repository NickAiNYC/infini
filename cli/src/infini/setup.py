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


SETUP_FUNCTIONS = {
    "claude": setup_claude,
    "gemini": setup_gemini,
    "codex": setup_codex,
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
