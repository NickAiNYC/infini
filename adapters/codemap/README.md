# Codemap Adapter (Context-Aware Engine)

> First engine that gives INFINI real project context.
> File trees, dependencies, handoff artifacts, and skills — injected
> into every step.

## Status: Preview — live mode working with Codemap CLI

This adapter calls `codemap context` to inject structured project
intelligence into Loopfile steps. It makes INFINI context-aware
rather than a blind executor.

## What this unlocks

- **Context-aware steps** — each step receives file tree, dependency
  flow, intent classification, and matched skills
- **Skills injection** — Codemap skills (refactor, test-first, hub-safety)
  are automatically matched and injected into step context
- **Handoff artifacts** — agent_history tracking across runs
- **No API keys** — Codemap runs locally, no cloud dependencies

## Setup

```bash
# 1. Install Codemap
brew tap JordanCoin/tap && brew install codemap

# 2. Verify context works
cd /path/to/your/project
codemap context --for "refactor auth" --json | head

# 3. Run an INFINI Loopfile with Codemap context
infini run loop.yaml --engine codemap --live
```

## Engine matrix

| Engine | Mock | Live | Context-Aware | Skills | Handoff |
|--------|------|------|---------------|--------|---------|
| Reference | ✅ | ⚠️ | ❌ | ❌ | ❌ |
| LangGraph | ✅ | ✅ | ❌ | ❌ | ❌ |
| Local (Qwythos) | ❌ | ✅ | ❌ | ❌ | ❌ |
| **Codemap** | ❌ | **✅** | **✅** | **✅** | **✅** |

## Portability

```bash
infini run loop.yaml --engine infini --trace ref.json
infini run loop.yaml --engine codemap --trace codemap.json
infini diff ref.json codemap.json
# → Same trace schema. Codemap adds context metadata.
```

## How it works

1. Adapter extracts intent from the Loopfile's OBJECTIVE or step params
2. Calls `codemap context --for <intent> --json` in the project root
3. Parses ContextEnvelope (file tree, deps, skills, handoff reference)
4. Injects context into each step's input
5. Builds INFINI trace with step outputs + codemap metadata

## Limitations

- Requires Codemap CLI installed (`brew install codemap`)
- Project root must be detected or passed explicitly
- Codemap must be in the project root for hooks/config to resolve
