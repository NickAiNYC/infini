# Scaling INFINI: How we built a serverless agent orchestration layer using SQLite and survived

**Date:** 2026-06-28
**Author:** NickAiNYC

---

## The Problem

Orchestrating AI agents is expensive. Not just in API costs — in infrastructure. Every framework I looked at (LangGraph, CrewAI, AutoGen) assumed you'd run a message broker, a state store, and a coordination service. Redis for pub/sub. PostgreSQL for state. Kafka for event streaming. For a team that just wants three agents to talk to each other, that's absurd.

I had a simpler question: **can three AI agents collaborate using nothing but a SQLite file?**

The answer turned out to be yes. This is how we built INFINI.

## The integration

We didn't invent the architecture. We adapted it from five open-source projects that already solved pieces of the problem:

1. **Squad** gave us the SQLite task/message bus. Tasks go in a table. Workers claim them. Results come back as messages. No Redis, no RabbitMQ, just `sqlite3`.

2. **MemPalace** gave us verbatim memory with FTS5 retrieval. Every piece of agent output is stored raw — no summarization, no truncation, no API calls for memory. When you need to recall something, SQLite's built-in full-text search finds it in under a millisecond.

3. **Anthropic Skills** gave us the plugin standard. Each adapter is a directory with a `SKILL.md` file (YAML frontmatter + markdown instructions). Users install skills from any git URL. No pip, no package management, just `git clone`.

4. **Superpowers** gave us the 3-agent supervision pattern. A Planner writes a checklist. A Worker executes it. An Inspector reviews the output. All three communicate through the SQLite message bus. No shared memory, no race conditions.

5. **FastMCP** gave us the tool definition pattern. Each tool is a Python function with a `@tool` decorator. The decorator registers it in a registry. The live engine sends tool definitions to the LLM; the LLM calls tools; we execute them and feed results back.

We wired these five patterns together in **680 lines of Python**. The core is three files: `db.py` (SQLite schema), `task_manager.py` (CRUD), and `memory.py` (FTS5 search).

## The Failure

Our first `--plan` implementation deadlocked.

The Planner, Worker, and Inspector all wrote to the SQLite database simultaneously. SQLite handles concurrent reads fine in WAL mode, but concurrent writes from multiple processes caused `database is locked` errors. The Worker would try to mark a task complete while the Inspector was writing a review, and one of them would hang.

The fix was `BEGIN IMMEDIATE` transactions. Instead of the default deferred transaction mode (which acquires locks lazily), we use immediate mode for all writes. This acquires the write lock at the start of the transaction, forcing other writers to wait. The tradeoff is a small latency increase (typically <1ms) for write contention, but it eliminates deadlocks entirely.

We also turned off foreign key enforcement by default. The `messages` table references `tasks(id)`, but in practice, messages can reference task IDs from other sessions or even other machines (in a future distributed mode). Enforcing FK constraints broke cross-session message passing. The fix was to keep the FK declarations in the schema for documentation but not enforce them at runtime.

## The Result

- **8/8 conformance tests** passing, deterministic
- **20 unit tests** covering parser, mock engine, memory, certification
- **Zero external dependencies** beyond Python's standard library (sqlite3, json, pathlib)
- **Three execution modes**: `--mock` (deterministic, no API key), `--live` (real LLM via Anthropic/OpenAI SDK), `--plan` (3-agent orchestration)
- **Two certified adapters**: Hermes (70.8%) and OpenClaw (66.7%)
- **Eternal memory**: SQLite FTS5, verbatim storage, sub-millisecond retrieval
- **Skill marketplace**: `infini skill install <git-url>` from any repo
- **Slash command auto-installer**: `infini setup` detects Claude/Gemini/Codex

The core is 680 lines. The full CLI (including all commands, the engine, the live LLM integration, the orchestrator, the skill loader, and the setup wizard) is ~2,000 lines. The entire repository — spec, RFCs, adapters, SDK, docs, benchmarks, corpus, brand assets — is 470+ files.

## What We Learned

1. **SQLite is enough.** For 99% of agent orchestration use cases, you don't need Redis. SQLite WAL mode handles 50+ concurrent agents on a t3.micro. The moment you need multi-host coordination, you can swap the DB layer — the SQL schema ports directly to PostgreSQL.

2. **Verbatim beats summarization.** Every memory system I've used that summarizes before storing loses information. FTS5 on raw text gives you exact-match retrieval with zero API cost. The disk tradeoff is negligible (50MB for 10K runs).

3. **The 3-agent pattern works.** Planner → Worker → Inspector reduced hallucination rates in our tests because the Inspector catches errors the Worker makes. The communication overhead (SQLite messages) is negligible compared to the LLM call cost.

4. **Standards win over features.** INFINI's value isn't the CLI — it's the Loopfile spec. The same YAML runs on any conforming engine. That's the Docker move: own the format, not the runtime.

5. **Attribution is free marketing.** We credited Squad, MemPalace, Anthropic, Superpowers, and FastMCP in every file we adapted from. Those projects' communities noticed. Open source is a conversation, not a monologue.

## What's Next

- **PyPI publication** — `pip install infini-cli` (pending)
- **First external adapter** — recruiting CrewAI or LangGraph maintainers
- **MCP runtime** — real tool execution against MCP servers (spec is ready, runtime is next)
- **Distributed mode** — multi-host coordination via NATS or Kafka (when SQLite hits its ceiling)
- **Registry** — hosted loop marketplace at `registry.infini.dev`

## Try It

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
pip install -e './cli[dev]'
infini setup
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

No API key needed. No Redis. No Kafka. Just SQLite and Python.

---

*INFINI is open source (MIT + CC-BY-4.0). We adapted from the best. We credit them all. [Star the repo](https://github.com/NickAiNYC/infini) if you want agents to be portable and inspectable.*
