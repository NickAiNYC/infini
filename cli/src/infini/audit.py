"""Project-readiness audit engine for INFINI.

Inspired by loop-engineering's loop-audit CLI. Scans a project directory
for loop-infrastructure signals and returns a 0-100 Loop Readiness Score
with actionable fix suggestions.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any


@dataclass
class AuditSignal:
    """A single audit signal — one thing checked against the project."""
    name: str
    description: str
    points: int
    found: bool = False
    detail: str = ""
    fix: str = ""

    @property
    def score(self) -> int:
        return self.points if self.found else 0


@dataclass
class AuditResult:
    """The complete audit result for a project."""
    project_dir: str
    signals: list[AuditSignal] = field(default_factory=list)
    score: int = 0
    max_score: int = 100
    maturity_level: str = ""

    @property
    def percentage(self) -> float:
        return round(100.0 * self.score / self.max_score, 1) if self.max_score > 0 else 0.0

    @property
    def missing_signals(self) -> list[AuditSignal]:
        return [s for s in self.signals if not s.found]

    @property
    def found_signals(self) -> list[AuditSignal]:
        return [s for s in self.signals if s.found]

    def to_dict(self) -> dict:
        return {
            "project_dir": self.project_dir,
            "score": self.score,
            "max_score": self.max_score,
            "percentage": self.percentage,
            "maturity_level": self.maturity_level,
            "signals": [
                {
                    "name": s.name,
                    "found": s.found,
                    "points": s.score,
                    "max_points": s.points,
                    "detail": s.detail,
                    "fix": s.fix,
                }
                for s in self.signals
            ],
        }


def maturity_for_score(score: int) -> str:
    if score >= 75:
        return "L3 Unattended"
    if score >= 50:
        return "L2 Assisted"
    if score >= 25:
        return "L1 Report-only"
    return "L0 Draft"


_SIGNAL_DEFINITIONS = [
    ("loopfile",        "Loopfile.yaml present",                    15),
    ("state",           "STATE.md or state/ directory",             10),
    ("verifier",        "Separate verifier agent (maker/checker)",  12),
    ("safety",          "Safety documentation (SAFETY.md)",          8),
    ("mcp_config",      "MCP configuration (.mcp.json, mcp.yaml)",  10),
    ("budget",          "Budget documentation (loop-budget.md)",     7),
    ("loop_config",     "LOOP.md or loop config file",               8),
    ("conventions",     "AGENTS.md or CLAUDE.md",                    8),
    ("ci",              ".github/workflows/ CI integration",        10),
    ("activity",        "Recent loop activity (runs, commits)",      8),
    ("lessons",         "Lessons-learned file (memory)",             2),
    ("replay_trace",    "run.json trace for replay",                 2),
]


def audit_project(project_dir: str | Path) -> AuditResult:
    """Run a full project-readiness audit."""
    project_dir = Path(project_dir).resolve()
    result = AuditResult(project_dir=str(project_dir))

    for name, desc, points in _SIGNAL_DEFINITIONS:
        signal = AuditSignal(name=name, description=desc, points=points)
        check_fn = globals().get(f"_check_{name}")
        if check_fn:
            check_fn(signal, project_dir)
        result.signals.append(signal)

    result.score = sum(s.score for s in result.signals)
    result.max_score = sum(s.points for s in result.signals)
    result.maturity_level = maturity_for_score(result.score)
    return result


def _check_loopfile(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("Loopfile.yaml", "loop.yaml", "loop.yml"):
        p = project_dir / name
        if p.exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Create a Loopfile.yaml: `infini init --pattern daily-triage`"


def _check_state(signal: AuditSignal, project_dir: Path) -> None:
    if (project_dir / "STATE.md").exists():
        signal.found = True
        signal.detail = "Found: STATE.md"
        return
    if (project_dir / "state").is_dir():
        signal.found = True
        signal.detail = "Found: state/ directory"
        return
    signal.fix = "Add a STATE.md file or state/ directory for persistent run state"


def _check_verifier(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("Loopfile.yaml", "loop.yaml"):
        p = project_dir / name
        if p.exists():
            try:
                import yaml
                data = yaml.safe_load(p.read_text())
                agents = data.get("AGENTS", [])
                roles = {a.get("role") for a in agents}
                if "verifier" in roles or "critic" in roles:
                    signal.found = True
                    signal.detail = "Loopfile has a verifier/critic agent"
                    return
            except Exception:
                pass
    for name in ("verifier.md", "VERIFIER.md", "skills/verifier.md"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = ("Add a verifier agent (role: verifier) to your Loopfile "
                  "for maker/checker separation")


def _check_safety(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("SAFETY.md", "safety.md", "docs/SAFETY.md", "SECURITY.md"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Add a SAFETY.md documenting safety constraints and handoff procedures"


def _check_mcp_config(signal: AuditSignal, project_dir: Path) -> None:
    for name in (".mcp.json", "mcp.yaml", "mcp.json", ".mcp.yaml"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    for name in ("Loopfile.yaml", "loop.yaml"):
        p = project_dir / name
        if p.exists():
            try:
                import yaml
                data = yaml.safe_load(p.read_text())
                if data.get("TOOLS"):
                    signal.found = True
                    signal.detail = "Loopfile declares TOOLS block"
                    return
            except Exception:
                pass
    signal.fix = "Add MCP tool declarations: .mcp.json or a TOOLS block in your Loopfile"


def _check_budget(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("loop-budget.md", "BUDGET.md", "budget.md", "docs/budget.md"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Add a loop-budget.md documenting expected token spend and cost limits"


def _check_loop_config(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("LOOP.md", "loop.md", ".loop.yml", ".loop.yaml"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Add a LOOP.md with cadence, limits, and handoff configuration"


def _check_conventions(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("AGENTS.md", "CLAUDE.md", "agents.md", "claude.md"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Add an AGENTS.md or CLAUDE.md documenting project conventions for AI agents"


def _check_ci(signal: AuditSignal, project_dir: Path) -> None:
    workflows = project_dir / ".github" / "workflows"
    if workflows.is_dir():
        yml_files = list(workflows.glob("*.yml")) + list(workflows.glob("*.yaml"))
        if yml_files:
            signal.found = True
            signal.detail = f"Found {len(yml_files)} workflow file(s)"
            return
    signal.fix = "Add a GitHub Actions workflow in .github/workflows/ to run loops on schedule"


def _check_activity(signal: AuditSignal, project_dir: Path) -> None:
    runs_dir = project_dir / "runs"
    if runs_dir.is_dir():
        run_files = list(runs_dir.rglob("run.json"))
        if run_files:
            now = datetime.now(timezone.utc)
            for rf in run_files:
                try:
                    mtime = datetime.fromtimestamp(rf.stat().st_mtime, tz=timezone.utc)
                    if (now - mtime) < timedelta(days=7):
                        signal.found = True
                        signal.detail = f"Recent run: {rf.relative_to(project_dir)}"
                        return
                except Exception:
                    pass
            signal.found = True
            signal.detail = f"Found {len(run_files)} run trace(s) (none recent)"
            return
    git_dir = project_dir / ".git"
    if git_dir.exists():
        try:
            import subprocess
            result = subprocess.run(
                ["git", "log", "--oneline", "--since=7 days ago", "--format=%h"],
                cwd=str(project_dir), capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                commits = result.stdout.strip().split("\n")
                signal.found = True
                signal.detail = f"Recent git activity: {len(commits)} commit(s) in last 7 days"
                return
        except Exception:
            pass
    signal.fix = "Run a loop (`infini run Loopfile.yaml`) to generate activity proof, or commit to git"


def _check_lessons(signal: AuditSignal, project_dir: Path) -> None:
    for name in ("lessons.md", "LESSONS.md", "memory/lessons.md", "LESSONS.txt"):
        if (project_dir / name).exists():
            signal.found = True
            signal.detail = f"Found: {name}"
            return
    signal.fix = "Add a lessons.md file to accumulate learnings across loop runs"


def _check_replay_trace(signal: AuditSignal, project_dir: Path) -> None:
    for pattern in ("runs/latest/run.json", "runs/*/run.json"):
        matches = list(project_dir.glob(pattern))
        if matches:
            signal.found = True
            signal.detail = f"Found: {matches[0].relative_to(project_dir)}"
            return
    signal.fix = "Run a loop to generate a run.json trace for replay debugging"
