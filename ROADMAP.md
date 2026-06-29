# INFINI Roadmap

This roadmap describes the direction of the project, not a commitment. Dates
are targets, not promises. Items move up or down based on contributor
interest and real-world adoption.

The roadmap is organized by theme. Within each theme, work is grouped into
**Now** (next 90 days), **Next** (90–180 days), and **Later** (180+ days).

---

## Theme 1 — The Spec

The Loopfile spec is the project's core asset. Everything else exists to
serve it.

### Now
- **Spec v1.0 final.** Close open questions in [`spec/loopfile-v1.md`](spec/loopfile-v1.md). Target: end of Q3.
- **RFC-0001 through RFC-0010** reviewed and either accepted or rejected. See [`spec/rfcs/`](spec/rfcs/).
- **`infini validate`** shipped as a stable command in the reference CLI.

### Next
- **Spec v1.1** (additive): `PACKS:`, `METRICS:`, `HOOKS:` blocks. Tracked in RFC-0011+.
- **First-class composition** (`CALLS:` block). The biggest open question in the spec.

### Later
- **Spec v2.0** (breaking): typed `OBJECTIVE`, structured verification, composition as a primitive.

---

## Theme 2 — The Reference Engine

The INFINI Reference Engine is the canonical conformance implementation. It
exists to make the spec concrete, not to compete with other engines.

### Now
- **`infini run`** end-to-end on the reference engine for every canonical loop.
- **`infini inspect`** with the full Loop Observatory UI (currently preview).
- **`infini replay`** time-travel debugger.
- **`infini diff`** semantic diff between Loopfile versions.

### Next
- **`infini ci`** stable GitHub Action with the diff-comment feature.
- **`infini trace`** export to OpenTelemetry for cross-engine observability.
- **`infini benchmark`** standardized benchmark runner.

### Later
- **`infini verify`** standalone verifier (no run, just verify a trace).
- **`infini migrate`** spec version migrator.

---

## Theme 3 — Adapters

Adapters make the spec real for ecosystems that already have runtimes.

### Now
- **Hermes adapter** — full conformance (Parse / Run / Verify / Inspect / Replay).
- **OpenClaw adapter** — full conformance minus Replay (planned for next release).
- **Adapter SDK** (`sdk/`) so third parties can implement adapters without reading the CLI source.

### Next
- **LangGraph adapter** — community-led, INFINI-maintained.
- **OpenAI Agents SDK adapter** — community-led.
- **Claude Code adapter** — community-led.

### Later
- **CrewAI, AutoGen, Gemini** adapters — community-led, tracked in [`spec/compatibility.md`](spec/compatibility.md).

---

## Theme 4 — The Registry

The registry is what makes Loopfiles shareable.

### Now
- **Local registry** — `infini publish` and `infini install` against a local path.
- **Registry protocol** — final, open for feedback. See [`registry/protocol.md`](registry/protocol.md).
- **Signing** — Ed25519 keypairs, content-addressed storage.

### Next
- **Public registry** at `registry.infini.dev`.
- **Web UI** for browsing Loopfiles.
- **Search** by name, tag, capability, engine.

### Later
- **Loop Registry** with categories, contributor profiles, verification badges.
  Mock exists at [`loops/`](loops/); real one is gated on registry launch.

---

## Theme 5 — The Loop Engineer Discipline

The discipline is what makes loops different from chains.

### Now
- **Loop Engineer prompt** ([`prompts/loop-engineer.md`](prompts/loop-engineer.md)) — runtime-agnostic.
- **12 canonical loops** ([`loops/`](loops/)) — each with a real Loopfile + essay.
- **Handbook** ([`docs/handbook/`](docs/handbook/)) — teaching the discipline.

### Next
- **Loop Engineer Handbook** as a single book-length document.
- **Benchmarks** comparing canonical loops across engines.
- **Loop Quality Score** surfaced in `infini validate` and the registry.

### Later
- **Certification** — a self-paced Loop Engineer curriculum. Not a credentialing body; just a clear path from "I can write a Loopfile" to "I can ship loops in production."

---

## Theme 6 — Community

### Now
- **GitHub Discussions** as the primary support channel.
- **RFC process** open to all contributors.
- **Office hours** — weekly, once Discord is live.

### Next
- **Discord** for synchronous discussion.
- **Adopters page** ([`docs/adopters.md`](docs/adopters.md)) populated.
- **First INFINI meetup** at a major conference.

### Later
- **Foundation governance** — move the project to a foundation once adoption warrants it.
- **Working groups** for spec, adapters, registry, observability.

---

## What's not on the roadmap

These come up regularly and are intentionally not planned:

- **A hosted INFINI service.** INFINI is a standard, not a SaaS. Anyone can host a registry; we won't sell a managed loop runner.
- **A proprietary "INFINI Pro."** The spec, CLI, adapters, and registry will always be open source.
- **Vertical integrations with specific model providers.** INFINI is model-agnostic. `model_tier` is engine-resolved for a reason.
- **Certification programs that charge money.** If a curriculum ever exists, it will be free.

---

## How to influence the roadmap

1. **Open an RFC** for spec changes. See [`spec/rfcs/README.md`](spec/rfcs/README.md).
2. **Open a Discussion** for adapter requests or feature requests.
3. **List yourself in [`docs/adopters.md`](docs/adopters.md)** — adopters shape the roadmap more than any other input.
4. **Run a benchmark** and post the results — data moves the roadmap faster than opinions.

The roadmap is reviewed quarterly. The next review is end of Q3 2026.
