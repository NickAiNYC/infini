"""Deterministic step executors for the portability proof.

These are the *agents'* actual work. They are pure, deterministic functions
over real files on disk — no LLM, no network, no randomness. Both the INFINI
reference runtime and the LangGraph runtime call THESE SAME functions, so any
difference in the produced artifacts can only come from the orchestration
engine, not from nondeterministic model output.

This is the whole point of the proof: isolate workflow portability from LLM
behaviour. See proof/README.md ("What this does NOT prove").
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

# Conventional-commit type -> CHANGELOG section heading. Order is significant
# and identical for both runtimes (deterministic rendering).
SECTION_ORDER = [
    ("feat", "Features"),
    ("fix", "Bug Fixes"),
    ("perf", "Performance"),
    ("refactor", "Refactoring"),
    ("docs", "Documentation"),
    ("test", "Tests"),
    ("chore", "Chores"),
]
_HEADER_RE = re.compile(r"^(?P<type>\w+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$")


def sha256_file(path: str | Path) -> str:
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_json(path: Path, obj) -> None:
    # Canonical JSON: sorted keys, fixed separators, trailing newline.
    # Guarantees byte-identical output across runtimes and machines.
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


# ── Step implementations ─────────────────────────────────────────────────────

def parse_commits(work: Path) -> list[str]:
    """s1: read the fixture, parse conventional-commit headers -> normalized.json"""
    raw = json.loads((work / "fixtures" / "commits.json").read_text(encoding="utf-8"))
    parsed = []
    for c in raw["commits"]:
        m = _HEADER_RE.match(c["message"].strip())
        if m:
            parsed.append({
                "sha": c["sha"],
                "type": m.group("type"),
                "scope": m.group("scope") or "",
                "breaking": bool(m.group("breaking")),
                "subject": m.group("subject").strip(),
            })
        else:
            parsed.append({"sha": c["sha"], "type": "other", "scope": "",
                           "breaking": False, "subject": c["message"].strip()})
    out = {"release": raw["release"], "commits": parsed}
    _write_json(work / "normalized.json", out)
    return ["normalized.json"]


def categorize(work: Path) -> list[str]:
    """s2: group normalized commits by type -> categories.json"""
    data = json.loads((work / "normalized.json").read_text(encoding="utf-8"))
    buckets: dict[str, list] = {}
    breaking: list = []
    for c in data["commits"]:
        buckets.setdefault(c["type"], []).append(c)
        if c["breaking"]:
            breaking.append(c)
    # Deterministic ordering inside each bucket: by sha.
    for k in buckets:
        buckets[k].sort(key=lambda x: x["sha"])
    out = {"release": data["release"], "breaking": sorted(breaking, key=lambda x: x["sha"]),
           "categories": buckets}
    _write_json(work / "categories.json", out)
    return ["categories.json"]


def render_changelog(work: Path) -> list[str]:
    """s3: render CHANGELOG.md. Conditional logic: empty sections are omitted."""
    data = json.loads((work / "categories.json").read_text(encoding="utf-8"))
    rel = data["release"]
    lines = [f"# Changelog", "", f"## {rel['version']} ({rel['date']})", ""]
    if data["breaking"]:
        lines.append("### ⚠ BREAKING CHANGES")
        lines.append("")
        for c in data["breaking"]:
            scope = f"**{c['scope']}**: " if c["scope"] else ""
            lines.append(f"- {scope}{c['subject']} ({c['sha']})")
        lines.append("")
    for key, heading in SECTION_ORDER:
        items = data["categories"].get(key)
        if not items:               # ← conditional: skip empty sections
            continue
        lines.append(f"## {heading}")
        lines.append("")
        for c in items:
            scope = f"**{c['scope']}**: " if c["scope"] else ""
            lines.append(f"- {scope}{c['subject']} ({c['sha']})")
        lines.append("")
    (work / "CHANGELOG.md").write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    return ["CHANGELOG.md"]


def render_summary(work: Path) -> list[str]:
    """s4: machine-readable counts -> summary.json"""
    data = json.loads((work / "categories.json").read_text(encoding="utf-8"))
    counts = {k: len(v) for k, v in data["categories"].items()}
    out = {
        "version": data["release"]["version"],
        "date": data["release"]["date"],
        "counts": counts,
        "breaking": len(data["breaking"]),
        "total": sum(counts.values()),
    }
    _write_json(work / "summary.json", out)
    return ["summary.json"]


# Dispatch table shared by both runtimes.
STEP_FUNCS = {
    "parse_commits": parse_commits,
    "categorize": categorize,
    "render_changelog": render_changelog,
    "render_summary": render_summary,
}


def execute_action(action: str, work: Path) -> list[str]:
    """Run a step's action deterministically. Returns the list of artifacts written."""
    if action == "verify":
        return []  # handled by the verifier, not here
    fn = STEP_FUNCS.get(action)
    if fn is None:
        raise ValueError(f"unknown action: {action}")
    return fn(work)
