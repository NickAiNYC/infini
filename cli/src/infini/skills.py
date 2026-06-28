"""Skill loader — scan ~/.infini/skills/ for SKILL.md files.

Attribution: SKILL.md folder structure from Anthropic Skills
(https://github.com/anthropics/skills). Each skill is a directory
containing a SKILL.md with YAML frontmatter + markdown instructions.
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Optional

import yaml

SKILLS_DIR = Path.home() / ".infini" / "skills"


def get_skills_dir() -> Path:
    """Get the skills directory, creating it if needed."""
    SKILLS_DIR.mkdir(parents=True, exist_ok=True)
    return SKILLS_DIR


def parse_skill_md(path: Path) -> dict | None:
    """Parse a SKILL.md file. Returns dict with frontmatter + body."""
    try:
        content = path.read_text()
    except Exception:
        return None

    # Parse YAML frontmatter
    if not content.startswith("---"):
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        return None

    try:
        frontmatter = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    return {
        **frontmatter,
        "body": parts[2].strip(),
        "path": str(path.parent),
    }


def list_skills() -> list[dict]:
    """Scan ~/.infini/skills/ for SKILL.md files. Returns list of skill dicts."""
    skills = []
    skills_dir = get_skills_dir()

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir():
            continue
        skill_md = d / "SKILL.md"
        if skill_md.exists():
            skill = parse_skill_md(skill_md)
            if skill:
                skill["name"] = skill.get("name", d.name)
                skill["dir"] = d.name
                skills.append(skill)

    return skills


def install_skill(git_url: str) -> dict:
    """Clone a git repo into ~/.infini/skills/.

    Returns dict with name and path.
    """
    skills_dir = get_skills_dir()

    # Derive directory name from URL
    name = git_url.rstrip("/").split("/")[-1]
    if name.endswith(".git"):
        name = name[:-4]

    target = skills_dir / name
    if target.exists():
        return {"name": name, "path": str(target), "status": "already_installed"}

    result = subprocess.run(
        ["git", "clone", "--depth", "1", git_url, str(target)],
        capture_output=True, text=True, timeout=60,
    )

    if result.returncode != 0:
        return {"name": name, "path": str(target), "status": "failed", "error": result.stderr}

    # Check for SKILL.md
    if not (target / "SKILL.md").exists():
        return {"name": name, "path": str(target), "status": "no_skill_md"}

    return {"name": name, "path": str(target), "status": "installed"}


def get_skill(name: str) -> dict | None:
    """Get a single skill by name."""
    skill_md = get_skills_dir() / name / "SKILL.md"
    if not skill_md.exists():
        return None
    skill = parse_skill_md(skill_md)
    if skill:
        skill["name"] = name
        skill["dir"] = name
    return skill


def skill_to_adapter_entry(skill: dict) -> dict:
    """Convert a skill to the adapter entry format used by infini engines."""
    return {
        "name": skill.get("name", "unknown"),
        "version": skill.get("version", "0.0.0"),
        "type": skill.get("type", "skill"),
        "description": skill.get("description", ""),
        "capabilities": skill.get("capabilities", {}),
        "entrypoint": skill.get("entrypoint", ""),
        "source": "skill",
        "path": skill.get("path", ""),
    }
