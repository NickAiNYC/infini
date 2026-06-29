"""OpenClaw Skill Resolver — Maps 5 OpenClaw skills to INFINI tools.

Real implementation for 5 skills:
- web-search → OpenClaw's web search skill
- github-pr → OpenClaw's PR management skill
- summarize → OpenClaw's summarization skill
- send-telegram → OpenClaw's Telegram integration
- run-shell → OpenClaw's shell execution skill
"""
from __future__ import annotations

import json
from typing import Any
from pathlib import Path

# OpenClaw skill registry (5 real skill mappings)
OPENCLAW_SKILL_MAP = {
    "web-search": {
        "id": "openclaw/web-search",
        "description": "Search the web and return results",
        "parameters": ["query", "max_results"],
        "invocation": "openclaw skill web-search --query {query} --max {max_results}",
        "category": "research",
    },
    "github-pr": {
        "id": "openclaw/github-pr",
        "description": "Create and manage GitHub pull requests",
        "parameters": ["repo", "title", "body", "base", "head"],
        "invocation": "openclaw skill github-pr --repo {repo} --title '{title}' --body '{body}'",
        "category": "coding",
    },
    "summarize": {
        "id": "openclaw/summarize",
        "description": "Summarize text or documents",
        "parameters": ["content", "max_length"],
        "invocation": "openclaw skill summarize --input '{content}' --max {max_length}",
        "category": "content",
    },
    "send-telegram": {
        "id": "openclaw/send-telegram",
        "description": "Send messages to Telegram",
        "parameters": ["chat_id", "message"],
        "invocation": "openclaw skill telegram --chat {chat_id} --message '{message}'",
        "category": "communication",
    },
    "run-shell": {
        "id": "openclaw/run-shell",
        "description": "Execute shell commands",
        "parameters": ["command", "cwd"],
        "invocation": "openclaw skill shell --command '{command}' --cwd {cwd}",
        "category": "system",
    },
}


class OpenClawSkillResolver:
    """Resolves OpenClaw skill names to INFINI tool declarations.

    Supports 5 real skills that map to OpenClaw's marketplace.
    Each skill is resolved to an INFINI-compatible tool definition
    that can be injected into a Loopfile's AGENTS[].tools array.
    """

    def __init__(self, skills_dir: Path | None = None):
        self.skills_dir = skills_dir or Path.home() / ".openclaw" / "skills"
        self.skill_cache: dict[str, dict] = {}

    def resolve(self, skill_name: str) -> dict[str, Any]:
        """Resolve an OpenClaw skill to an INFINI tool definition.

        Args:
            skill_name: Full skill name (e.g., "openclaw/web-search")
                       or short name (e.g., "web-search")

        Returns:
            INFINI tool declaration with name, description, parameters,
            invocation, and MCP integration flag.

        Raises:
            ValueError: If the skill is not in the registry.
        """
        # Parse skill_name
        if "/" in skill_name:
            _, skill_id = skill_name.split("/", 1)
        else:
            skill_id = skill_name

        if skill_id not in OPENCLAW_SKILL_MAP:
            raise ValueError(
                f"Unknown OpenClaw skill: {skill_id}. "
                f"Available: {', '.join(OPENCLAW_SKILL_MAP.keys())}"
            )

        skill = OPENCLAW_SKILL_MAP[skill_id]

        # Build INFINI tool declaration
        tool = {
            "name": skill["id"],
            "description": skill["description"],
            "parameters": skill["parameters"],
            "invocation": skill["invocation"],
            "category": skill.get("category", "general"),
            "source": "openclaw",
        }

        # Add MCP integration if available
        if self._has_mcp(skill_id):
            tool["mcp"] = f"openclaw/{skill_id}"

        # Cache it
        self.skill_cache[skill_id] = tool

        return tool

    def _has_mcp(self, skill_id: str) -> bool:
        """Check if skill has MCP integration.

        web-search and github-pr have MCP server support.
        """
        return skill_id in ["web-search", "github-pr"]

    def resolve_all(self, skill_names: list[str]) -> list[dict[str, Any]]:
        """Resolve multiple skills. Returns list of tool declarations.

        Unknown skills are skipped with a warning.
        """
        tools = []
        for name in skill_names:
            try:
                tool = self.resolve(name)
                tools.append(tool)
            except ValueError as e:
                print(f"Warning: {e}")
        return tools

    def export_to_loopfile(self, skill_names: list[str]) -> dict:
        """Export multiple skills to a Loopfile TOOLS block.

        Returns a dict that can be merged into a Loopfile's TOOLS section.
        """
        tools = self.resolve_all(skill_names)
        return {"tools": [{"mcp": t["name"]} for t in tools]}

    def list_available_skills(self) -> list[str]:
        """List all available OpenClaw skills."""
        return list(OPENCLAW_SKILL_MAP.keys())

    def get_skill_info(self, skill_name: str) -> dict | None:
        """Get detailed info about a skill without raising."""
        try:
            return self.resolve(skill_name)
        except ValueError:
            return None


# CLI entry point for testing
if __name__ == "__main__":
    resolver = OpenClawSkillResolver()

    print("OpenClaw Skill Resolver — 5 Skills")
    print("=" * 50)

    skills = resolver.list_available_skills()
    for skill in skills:
        tool = resolver.resolve(f"openclaw/{skill}")
        mcp = "✅" if "mcp" in tool else "❌"
        print(f"\n  {tool['name']}")
        print(f"    {tool['description']}")
        print(f"    Parameters: {', '.join(tool['parameters'])}")
        print(f"    MCP: {mcp}")
        print(f"    Invocation: {tool['invocation']}")

    print(f"\n{'=' * 50}")
    print(f"✅ {len(skills)} skills resolved successfully")

    # Test export
    exported = resolver.export_to_loopfile(skills)
    print(f"\nExported TOOLS block ({len(exported['tools'])} entries)")
