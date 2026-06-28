# Engine Compatibility Matrix

Which engines can parse a Loopfile, run it, verify it, inspect the trace, replay it, and diff versions?

> **INFINI runs Loopfiles.** Any engine that conforms to [`spec/loopfile-v1.md`](loopfile-v1.md) can claim conformance. This document tracks real, tested conformance.

---

## Conformance levels

A conforming engine implements six capabilities. An engine is **fully conformant** when all six are ✅ shipped. Partial conformance is allowed and tracked.

| Capability       | Description |
| ---------------- | ----------- |
| **Parse Loopfile** | Accept any v1.0 Loopfile; reject invalid ones per [`schema.json`](schema.json). |
| **Run Loop**       | Execute the `STEPS` DAG with declared `AGENTS`. |
| **Verify**         | Run `VERIFY.syntactic` and `VERIFY.semantic` checks; report confidence. |
| **Inspect Trace**  | Emit a `run.json` trace per spec §10; `infini inspect` reads it. |
| **Replay**         | Resume from any step using saved `STATE`. |
| **Diff**           | Produce a semantic diff between two Loopfile versions or two run traces. |

Legend: ✅ shipped · 🚧 adapter in progress · ❌ not yet supported

---

## The matrix

Updated quarterly as engine adapters mature. Last review: 2026-06-28.

| Engine                  | Parse Loopfile | Run Loop | Verify | Inspect Trace | Replay | Diff |
| ----------------------- | :------------: | :------: | :----: | :-----------: | :----: | :--: |
| INFINI Reference Engine |       ✅       |    ✅    |   ✅   |      ✅       |   ✅   |  ✅  |
| LangGraph               |       ✅       |    🚧    |   🚧   |      🚧       |   🚧   |  🚧  |
| CrewAI                  |       🚧       |    🚧    |   ❌   |      ❌       |   ❌   |  ❌  |
| AutoGen                 |       🚧       |    🚧    |   🚧   |      🚧       |   ❌   |  ❌  |
| OpenAI Agents SDK       |       🚧       |    🚧    |   🚧   |      🚧       |   ❌   |  🚧  |
| Claude Code             |       🚧       |    🚧    |   🚧   |      🚧       |   🚧   |  🚧  |
| Gemini                  |       🚧       |    ❌    |   ❌   |      ❌       |   ❌   |  ❌  |
| OpenClaw                |       ✅       |    🚧    |   🚧   |      🚧       |   🚧   |  🚧  |

The **INFINI Reference Engine** is the canonical implementation. All other engines are adapters that conform to the same Loopfile contract but live in their own repos.

---

## Adapter authoring guide

Want to add your engine to this matrix? The minimum bar for an entry is **Parse Loopfile** ✅.

### 1. Implement the parser

Use [`schema.json`](schema.json) to validate. The parser must:

- Accept any v1.0 Loopfile.
- Reject invalid Loopfiles with a structured error pointing to the offending field.
- Preserve key order from the source file (some engines care).

### 2. Implement the runner (for Run Loop ✅)

Execute `STEPS` as a DAG. Honor `depends_on`. Enforce `BUDGET`. Emit a `run.json` trace per spec §10.

### 3. Implement verify (for Verify ✅)

Run `syntactic` checks as subprocesses (exit-code based). Run `semantic` checks as model-judged calls producing a 0–100 confidence. Compute the mean; compare to `confidence_threshold`.

### 4. Implement inspect (for Inspect Trace ✅)

Persist the trace to `runs/<id>/run.json`. The `infini inspect` command reads this format and renders the Loop Observatory.

### 5. Implement replay (for Replay ✅)

Persist `STATE` per step. On `infini replay --step <id>`, load state, allow input mutation, re-run from that step.

### 6. Implement diff (for Diff ✅)

Produce a semantic diff (not a line diff) between two Loopfile versions. Highlight changes to `OBJECTIVE`, `STEPS`, `VERIFY`, `BUDGET`, `STOP_WHEN`.

---

## Reporting conformance

Open a PR against this file with your engine's row updated. Include:

1. The adapter repo URL.
2. A pointer to the conformance test suite results.
3. The Loopfile spec version tested against.

We re-review the matrix quarterly. Stale entries (no commits to the adapter in 90 days) are downgraded one level.

---

## FAQ

**Why isn't `<engine>` listed?**
Open a PR. We add any engine that ships at least `Parse Loopfile` ✅.

**Can an engine be partially conformant?**
Yes. Partial conformance is the norm during early adoption. The matrix is honest about it.

**Does the INFINI Reference Engine have special privileges?**
No. It's the reference implementation, but it conforms to the same spec as everyone else. The only asymmetry: it ships first with new spec features, since the spec is developed against it.

**What happens when the spec revs?**
Engines have 90 days to update their matrix entry after a spec release. Entries that haven't updated are marked stale.

---

## History

| Date       | Change |
| ---------- | ------ |
| 2026-06-28 | Initial matrix published with 8 engines. |
