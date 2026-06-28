# ADR-002: Adopt Anthropic Skills Standard for Plugins

**Status:** Accepted
**Date:** 2026-06-28

## Context

INFINI needs an adapter system. Agent frameworks (LangGraph, CrewAI,
Mastra, etc.) should be pluggable without touching core code.

The initial design used hardcoded `adapters/` directories with
`adapter.yaml` manifests. This works but has problems:
- Adapters must live inside the INFINI repo (or be pip-installed)
- No standard format for adapter instructions (just YAML metadata)
- Users can't install third-party adapters from git URLs
- The system is INFINI-specific, not interoperable with other tools

## Decision

Adopt the Anthropic Skills standard: each adapter is a directory
containing a `SKILL.md` file with YAML frontmatter + markdown body.

```markdown
---
name: hermes-adapter
description: Executes Hermes agent workflows
version: 1.0.0
entrypoint: python -m infini.runtimes.hermes
allowed_tools: [bash, python, http]
---

# Hermes Runtime
Full instructions for the LLM on how to behave when this skill is active...
```

Skills are installed to `~/.infini/skills/` via:
```bash
infini skill install https://github.com/awesome/skill-repo
```

## Consequences

**Positive:**
- Users install skills from any git URL — no pip required.
- SKILL.md contains both metadata (YAML) and instructions (markdown),
  so the LLM can read the skill's behavior directly.
- Interoperable: any tool that reads Anthropic Skills can use the same
  skill files.
- Third-party developers can publish skills without touching INFINI core.

**Negative:**
- No strict versioning. A skill cloned from git is whatever's at HEAD.
  Mitigation: users can pin to a commit hash or tag in the URL.
- No dependency management. A skill can't declare "requires
  anthropic>=0.20". Mitigation: the SKILL.md frontmatter could
  include a `dependencies` field in a future revision.
- Security: cloning arbitrary git repos runs arbitrary code.
  Mitigation: document the risk; recommend only installing skills
  from trusted sources.

## Attribution

The SKILL.md format is from
[Anthropic Skills](https://github.com/anthropics/skills).
