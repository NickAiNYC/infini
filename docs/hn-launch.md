# Show HN: INFINI - Docker for AI Agents (Open Portability Standard)

Hey HN,

For the last year, everyone's been building their own AI agent framework (LangGraph, CrewAI, AutoGen, Mastra, OpenAI SDK, etc.). If you write a multi-agent loop today, your business logic is locked into the execution engine you chose. If you want to switch from CrewAI to LangGraph to get better graph branching, you rewrite from scratch. 

That felt wrong, so I built **INFINI**, an open portability standard and "Docker for Agents."

It's a declarative spec (`Loopfile.yaml`) that separates your agent business logic from the runtime engine. You write your loop once, and then you can execute it across any supported framework. 

**What it gives you today:**
1. **Write Once, Run Anywhere**: We have working adapters for LangGraph and CrewAI, plus a native reference engine. You can `infini run loop.yaml --engine langgraph` or `--engine crewai` and get identical execution logic.
2. **Standardized Traces**: Every engine outputs a unified `run.json` schema. We built a 3D Observatory UI that lets you visualize and time-travel replay these traces no matter which underlying engine ran them.
3. **Real Verification**: Loopfiles have a `VERIFY` block where you can assert that a file actually exists, a script exits 0, or an LLM judge gave it a 90/100.
4. **Deterministic Mocking**: You can pass `--mock` to run thousands of iterations locally in seconds to verify loop topology and budgets without burning API credits.

We just got the CI pipeline green with conformance tests proving identical trace schemas across engines (LangGraph and CrewAI).

The spec is CC-BY-4.0. We aren't trying to replace LangGraph or CrewAI; we just think the orchestration layer shouldn't be proprietary.

Repo: https://github.com/NickAiNYC/infini
Docs & Spec: https://infini.dev

Would love your thoughts, especially from folks who've felt the pain of migrating an agent stack. What frameworks should we write adapters for next?
