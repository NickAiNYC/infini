# RFC-0008: Loop Observatory

- Start date: 2026-06-28
- Status: draft
- Spec version: N/A (UI on top of trace)
- PR: TBD
- Implementation: `infini inspect` ships in 1.0; full Observatory in 1.1

## Summary

Defines the Loop Observatory: the signature feature of INFINI, the DevTools
for autonomous systems. Every execution leaves behind a visual trace — the
Observatory is how you read it.

## Motivation

Agent runs are opaque. You can see the final output; you can't see *how*
the agent got there. This makes agent systems hard to debug, hard to
trust, and hard to improve.

The Observatory must be:

- **Universal.** It works on any `run.json`, regardless of which engine
  produced it.
- **Visual.** Decisions are graphs; cost is a waterfall; iterations are
  diffs. Text logs are not enough.
- **Replayable.** The Observatory is the entry point for replay. You see
  the trace; you click a step; you replay from there.
- **Comparable.** You can diff two runs side by side — across engines,
  across versions, across iterations.

## Detailed design

### Views

The Observatory has eight views, each addressable by URL fragment:

1. **Timeline** (`#timeline`). The default. A horizontal swimlane of every
   step, colored by engine lane (Hermes = blue, OpenClaw = orange, etc.).
   Each step shows cost, duration, status. Failures and retries are
   flagged.

2. **Decision graph** (`#graph`). A DAG view of the STEPS, with edges
   showing `depends_on`. Each node is clickable; clicking opens the step
   detail panel. Cycles (loops) are rendered with a curved arrow.

3. **Iteration diff** (`#diff`). If the loop ran multiple iterations, this
   view shows what changed between iterations. Added/removed/modified
   steps are highlighted.

4. **Memory snapshots** (`#memory`). For loops with `LESSONS` or `MEMORY`,
   this view shows the lessons recalled before the run and the lessons
   appended after.

5. **Cost** (`#cost`). A waterfall chart of token and dollar cost by step.
   The total is shown against the BUDGET ceiling. Steps that consumed
   more than expected are flagged.

6. **Verification** (`#verify`). Every check in the VERIFY block, with its
   status, confidence score, and threshold. Failed checks are expandable
   to show why.

7. **Artifacts** (`#artifacts`). Every file the loop produced, organized
   by step. Clicking opens the artifact in a viewer. Signed artifacts
   show the signature.

8. **Replay** (`#replay`). The replay studio. Pick a step, mutate inputs,
   re-run. The result is shown side-by-side with the original.

### Trace shape

The Observatory reads `run.json` per spec §10. Engines that emit richer
traces (Hermes governance events, OpenClaw tool calls) get richer views;
engines that emit only the minimum get the minimum views.

### Comparison

`infini diff runs/<id1>/ runs/<id2>/` opens a comparison view. The two
runs are shown side by side: timelines aligned, costs compared, outcomes
diffed. This is how you answer "did this loop get better or worse between
versions?"

### Open format

The Observatory is a static web app. It reads `run.json` from disk or
from a URL. There is no backend. You can open any trace, from any engine,
in any Observatory instance.

## Alternatives considered

- **LangSmith-style hosted UI.** Rejected — couples the UI to a backend.
  The Observatory is local-first.
- **Text-only (`infini inspect` as a CLI).** Shipped as the floor. The
  full UI is the ceiling.
- **Per-engine UIs.** Rejected — the whole point of INFINI is that one
  tool works on any engine's trace.
- **Real-time observability (streaming).** Rejected for v1 — replay is
  the model. Real-time is a v1.2 candidate.

## Backwards compatibility

N/A — the Observatory is additive. `infini inspect` (CLI) shipped in
v1.0; the full UI is in preview.

## Conformance impact

Engines must emit `run.json` per spec §10 to be `Inspect Trace` ✅. The
Observatory renders any conformant trace; richer traces get richer views.

## Open questions

- Should the Observatory be a standalone Electron app, a web app, or both?
  Current answer: web app first, Electron later.
- Should traces be shareable via URL? Current answer: yes, via
  `run.json` pasted into a query string or hosted on a gist.
- How are very large traces (1000+ steps) handled? Current answer:
  virtualized rendering, with summary views for collapsed sections.

## Future possibilities

- v1.1: full Observatory UI (all eight views).
- v1.2: real-time streaming for in-progress runs.
- v2.0: collaborative Observatory — multiple engineers viewing the same
  trace simultaneously, with shared annotations.

## Acknowledgements

The Observatory is modeled on Chrome DevTools (the timeline view), GitHub
Actions (the step-by-step run view), Jaeger (distributed tracing), and
LangSmith (the agent-trace concept). The difference: the Observatory is
engine-agnostic and works on any conformant trace.
