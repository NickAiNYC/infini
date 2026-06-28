# INFINI Docs

Essays, benchmarks, and community documentation for the INFINI ecosystem.

> The spec lives in [`../spec/`](../spec/). The Loop Engineer prompt lives in [`../prompts/`](../prompts/). This directory is for the *discourse* around them.

---

## Essays

Long-form writing on loop design. Submit a PR to add yours.

| Essay | Topic |
| --- | --- |
| `loop-design-patterns.md`      | When to use a verify-heavy loop vs. a plan-heavy loop. *(planned)* |
| `anti-patterns.md`             | What *not* to do, and why. *(planned)* |
| `verification-bible.md`        | Patterns for writing good `VERIFY` blocks. *(planned)* |
| `cost-optimization.md`         | How to write loops that cost less without sacrificing correctness. *(planned)* |
| `loop-psychology.md`           | The human side of working with autonomous loops. *(planned)* |
| `hermes-vs-openclaw-vs-both.md`| When to govern, when to execute, when to do both. *(planned)* |

See [`CONTRIBUTING.md`](../CONTRIBUTING.md) for the bar an essay must clear.

---

## Benchmarks

Comparative runs of canonical loops across engines. Every benchmark must include the raw `run.json` traces so others can verify.

| Benchmark | Loop | Engines | Last run |
| --- | --- | --- | --- |
| `coding-loop-bench.md` | `infini/coding-loop@1.0` | INFINI Reference, Hermes, OpenClaw, LangGraph | *(planned)* |
| `research-loop-bench.md` | `infini/research-loop@1.0` | INFINI Reference, OpenClaw | *(planned)* |
| `governance-overhead-bench.md` | `infini/claim-audit-loop@1.0` | Hermes-only vs. hybrid | *(planned)* |

Each benchmark reports: iterations, runtime, dollar cost, verification rate, failure count, and artifacts produced.

---

## Community

- [`community.md`](community.md) — office hours schedule, agenda doc, Discord invite. *(planned)*
- [`governance.md`](governance.md) — how RFCs are decided, who maintains what. *(planned)*
- [`adopters.md`](adopters.md) — who's using INFINI in production. Open a PR to add yourself. *(planned)*

---

## The Loop Engineer Handbook

A book-length guide to the discipline. Planned chapters:

1. What is a Loop Engineer?
2. Writing your first Loopfile.
3. Verification: the heart of the discipline.
4. Budgets and escalation.
5. Inspecting and replaying runs.
6. Loop composition and packs.
7. Engine selection and portability.
8. The Loop Observatory as a daily tool.
9. On-call loops and incident response.
10. Teaching loops to your team.

This is the "Google SRE Book" move for agents. Drafts land in `docs/handbook/` as they're written.

---

## License

CC-BY-4.0. See [repository LICENSE](../LICENSE).
