# Supervisor Loop: Hermes × OpenClaw

> The canonical reference for multi-agent supervision. Hermes plans and reviews; OpenClaw executes. Same architecture, any runtime.

## What this demonstrates

- **Hermes as VERIFY engine** — semantic checks routed to Hermes's curator
- **OpenClaw skill resolution** — 3 OpenClaw skills declared as tools
- **Learning loop** — Hermes learns from each execution via memory
- **Cross-ecosystem** — two agent systems collaborating through one Loopfile

## Run it

```bash
infini validate loop.yaml
infini run loop.yaml --mock
infini inspect runs/latest/

# Run on LangGraph (proves portability)
infini run loop.yaml --engine langgraph --mock
```

## Architecture

```
Hermes (planner) → OpenClaw (builder) → Hermes (reviewer)
     ↓                    ↓                    ↓
  plan.md           output/            review.md
  required-skills   execution-log      learned-pattern
```

## Verification

Semantic checks use Hermes's curator:

```yaml
semantic:
  - "judge:hermes/curator:correctness>=90"
  - "judge:hermes/curator:consistency>=85"
  - "judge:hermes/memory:pattern_learned==true"
```

This is real verification — not a placeholder. Hermes's autonomous curator evaluates the execution the same way it evaluates 44,000+ skills in production.

## OpenClaw Skills

Three OpenClaw skills are declared as tools:

```yaml
TOOLS:
  - mcp: "openclaw/web-research"
  - mcp: "openclaw/github-pr"
  - mcp: "openclaw/slack-notify"
```

The OpenClaw adapter resolves these from the marketplace and wraps them as INFINI tools.
