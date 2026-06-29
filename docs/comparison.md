# INFINI vs. Other Agent Frameworks

A fair, specific comparison. INFINI doesn't compete with these
frameworks — it **complements** them by making your workflow portable
across them.

---

## Quick comparison

| Feature | INFINI | LangGraph | CrewAI | AutoGen | OpenAI Agents | Mastra |
|---------|--------|-----------|--------|---------|---------------|--------|
| Declarative workflows | ✅ Loopfile YAML | ❌ Code-only | ❌ Code-only | ❌ Code-only | ❌ Code-only | ❌ Code-only |
| Engine-agnostic | ✅ 4 engines | ❌ LangGraph only | ❌ CrewAI only | ❌ AutoGen only | ❌ OpenAI only | ❌ Mastra only |
| Portable traces | ✅ Identical shape | ❌ Framework-specific | ❌ Framework-specific | ❌ Framework-specific | ❌ Framework-specific | ❌ Framework-specific |
| Time-travel replay | ✅ `infini replay` | ⚠️ Checkpointing only | ❌ | ❌ | ❌ | ❌ |
| Real verification | ✅ `:exists`, `:exit_zero` | ❌ | ❌ | ❌ | ❌ | ❌ |
| Local engine | ✅ Qwythos (offline) | ❌ | ❌ | ❌ | ❌ | ❌ |
| MCP integration | ✅ Loopfile tools: | ❌ | ❌ | ❌ | ⚠️ | ❌ |
| GitHub Action | ✅ INFINI Guard | ❌ | ❌ | ❌ | ❌ | ❌ |
| Open standard | ✅ CC-BY-4.0 spec | ❌ Proprietary | ❌ Proprietary | ✅ MIT | ✅ MIT | ❌ Proprietary |
| Budget enforcement | ✅ BUDGET block | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## When to use INFINI

- **You want to avoid framework lock-in.** Write one Loopfile, run it
  on LangGraph today, CrewAI tomorrow, or a local model next week.

- **You need to verify agent outputs.** INFINI's `VERIFY` block checks
  real files and process exit codes. No other framework has this.

- **You want time-travel debugging.** `infini replay --step s3` replays
  any step with identical inputs. Useful for debugging without
  re-running the whole workflow.

- **You care about cost.** INFINI's `BUDGET` block caps cost and time.
  The local engine runs for $0.

- **You want a portable format for your tools.** The Loopfile spec is
  a CC-BY-4.0 open standard, not proprietary to any runtime.

---

## When to use each framework

### LangGraph

**Best for:** Complex graph-based workflows with conditional branching
and cycles. LangGraph's state machine model is more expressive than
INFINI's linear DAG for advanced use cases.

**INFINI's role:** Define the workflow in a Loopfile, run it on
LangGraph as one engine option. Get portability without losing
LangGraph's capabilities.

### CrewAI

**Best for:** Role-based multi-agent teams with delegation. CrewAI's
agent roles and task assignment model is a good fit for simulations
and team-based workflows.

**INFINI's role:** Loopfiles can define the same agent roles and tasks.
Run the same workflow on CrewAI or any other engine.

### AutoGen

**Best for:** Conversational multi-agent systems with dynamic
agent-to-agent interaction. AutoGen's chat-based agent model is
unique.

**INFINI's role:** Loopfiles can orchestrate AutoGen agents as steps
in a larger portable workflow.

### OpenAI Agents API

**Best for:** Teams already in the OpenAI ecosystem who want the
simplest possible agent setup.

**INFINI's role:** Wrap OpenAI Agents calls in a Loopfile for
portability. Run the same workflow locally with Qwythos when you
don't want API costs.

### Mastra

**Best for:** TypeScript-first agent development with built-in tools
and memory.

**INFINI's role:** Loopfiles provide a language-agnostic workflow
definition that can orchestrate Mastra agents.

---

## Can they work together?

**Yes.** That's the point.

INFINI is not a replacement for these frameworks. It's a **portability
layer** that sits above them:

```
        ┌──────────────────┐
        │    Loopfile       │
        │  (your workflow)  │
        └────────┬─────────┘
                 │
      ┌──────────┼──────────┐
      ↓          ↓          ↓
  LangGraph   CrewAI    Local LLM
  (graph)     (teams)   (offline)
```

Write the Loopfile once. Run it on LangGraph for complex graphs,
CrewAI for team simulations, or the local engine for offline dev.
Same workflow. Identical traces.

---

## Why this matters

Every framework claims portability. None delivers it, because none
has a workflow format that's independent of the runtime.

INFINI's Loopfile is that format. It's a **CC-BY-4.0 open standard**,
not proprietary to any vendor. You can adopt it today without locking
into a new ecosystem.

[Back to tutorial](tutorial.md) · [Demo](demo.md) · [Spec](../spec/loopfile-v1.md)
