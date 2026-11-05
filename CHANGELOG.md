# Changelog

All notable changes to INFINI, the Loopfile spec, and the `infini` CLI are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] — 2026-11-04

### Added
- **OpenTelemetry GenAI Semantic Conventions Exporter:** `infini export-otel` and `--otel` flag for `infini run`. Maps execution traces to OTel ResourceSpans with experimental `gen_ai.*` attributes and stable trace envelopes.
- **Cross-Engine Step Divergence Diffing:** Enhanced `infini diff` to detect and name the exact first step where two execution engine runs diverge in step ID, status, action, or artifacts.
- **Reproducible Benchmark Suite:** Added `benchmarks/run_benchmarks.py` (`make bench`) measuring replay determinism (100% byte-identical over N=100 runs) and reference engine per-step overhead (1.824 ms mean latency), committed with machine specs in `benchmarks/results.json`.
- **Local Ed25519 Trace Signing & Offline Verification:** Added pure-Python RFC 8032 Ed25519 signing (`infini run --sign`) and offline signature verification command (`infini verify-trace`) with zero external dependencies.
- **Minimal Working Quickstart:** Added `examples/quickstart.yaml` guaranteeing execution in < 60s on clean installations.
- **Formalized Scoring Methodology:** Added `docs/scoring.md` defining formulas for Project Readiness Audit Score (0-100 across 12 signals) and Adapter Compatibility Score (Hermes 70.8%, OpenClaw 66.7%).
- **Automated Docs Verification CI:** Added GitHub Actions job running README quick start verbatim on a clean runner.

### Changed
- Reconciled adapter statuses to three honest tiers: `working`, `mock-only`, `not built`.
- Made unbuilt engines (`--engine crewai`, `--engine autogen`, etc.) fail cleanly with descriptive error messages instead of tracebacks.
- Consolidated `STATUS.md`, `STATE.md`, and `ROADMAP.md` into a single status section in `README.md`.
- Archived unproven claims (50+ agents on a t3.micro, on-chain escrow payments, 3D observatory) to `docs/ideas.md`.
- Pinned Python version to >=3.11 across all project configurations.

---

### Added — Milestone 3: The Standard Scales

#### Community Adapter SDK
- **`sdk/`** restructured with 6 files: README, adapter-interface, minimal-adapter/, testing-guide, certification-guide, publishing-guide
- Minimal adapter: ~50-line PARSE-only adapter as a copy-and-extend starting point
- Build an adapter in under 30 minutes

#### Community Registry
- **`registry/official/`** — hermes + openclaw with manifest.yaml, metadata.json, README, compatibility.json
- **`registry/community/`** — ready for community adapters
- **`registry/experimental/`** — for adapters in development
- Git-based, no hosted service

#### Marketplace Structure
- 12 category pages: Research, Coding, DevOps, Security, Compliance, Marketing, Sales, Legal, Healthcare, Finance, Infrastructure, Education
- Submission template with: Loopfile, diagram, benchmark, essay, verification, replay, license, tags, difficulty, runtime, capabilities

#### Official Design Language
- **`brand/`** directory: logo.svg, wordmark.svg, favicon.svg, social-banner.svg (1280×640)
- palette.md, typography.md, diagram-style.md
- One visual identity across all docs

#### Documentation Upgrade
- Handbook expanded to 17 cross-linked chapters
- New: getting-started, architecture, mcp-roadmap, adapter-development, certification, marketplace, community
- Cross-reference map in handbook README

#### Benchmark Suite
- 8 benchmark specs: browser-automation, coding, research, planning, refactoring, compliance, hybrid-agent, cost-optimization
- Each defines: goal, success criteria, artifacts, budget, verification rubric

#### Contributor Experience
- CODEOWNERS file for code ownership guidance
- RELEASE_CHECKLIST.md for release process
- Issue templates (bug, feature, RFC) — already existed
- PR template with spec-impact checklist — already existed

### Changed
- README polished: full-width banner, certification badges, corpus section, certification section

---

## [0.1.0] — 2026-06-28

### Added — protocol-grade expansion

#### RFC system
- **`spec/rfcs/README.md`** — RFC process (modeled on Rust, Kubernetes KEPs, Python PEPs).
- **10 RFCs:** RFC-0001 Loopfile, RFC-0002 Verification, RFC-0003 Replay, RFC-0004 Memory, RFC-0005 Registry, RFC-0006 Marketplace, RFC-0007 Adapter Interface, RFC-0008 Observatory, RFC-0009 Provenance, RFC-0010 Cost Accounting.

#### Adapter SDK
- **`sdk/README.md`** — Adapter SDK overview: 6 capabilities, install, anatomy.
- **`sdk/adapter-interface.md`** — Normative interface reference: types, base class, capability contracts, hybrid mode, conformance testing.
- **`sdk/examples/minimal-adapter.md`** — Smallest possible adapter (PARSE only).

#### Handbook (10 chapters)
- **`docs/handbook/`** — Why Loopfiles · Design Philosophy · Loop Engineering · Verification · Memory · Observability · Replay · Governance · Portability · Standards.

#### Design Patterns (13 patterns)
- **`docs/patterns/`** — Retry · Human Approval · Budget Guard · Parallel Workers · Fan Out · Fan In · Verification Gate · Reflection Loop · Research Loop · Planning Loop · Memory Update · Escalation · Self Improvement.

#### Anti-Patterns (9 anti-patterns)
- **`docs/anti-patterns/`** — Infinite Loops · Hallucination Chains · Missing Verification · Unbounded Costs · Hidden State · Tool Spam · Prompt Soup · Over-Planning · No Exit Condition.

#### Canonical loop expansion (12 loops × 5 new files each)
- Every canonical loop now ships with: `Loopfile.yaml`, `README.md`, `essay.md`, `diagram.svg`, `trace.json`, `verification.md`, `benchmark.md`, `replay.md`.

#### Marketplace (preview)
- **`marketplace/`** — 12 category pages (Research, Coding, Compliance, Security, Sales, SEO, Marketing, Healthcare, Finance, Legal, Education, Infrastructure). Clearly labeled Preview.

#### Benchmark suite
- **`benchmarks/`** — 5 benchmark specs: coding-loop, research-loop, compliance-loop, browser-loop, hybrid-loop. Methodology + reporting standards.

#### Registry metadata
- **`registry/metadata-schema.md`** — Loop Quality Score (8 sub-scores, weighted to 100) + registry metadata fields schema.

#### Loop Observatory expansion
- **`assets/observatory.png`** — swimlane trace (existing).
- **`assets/loop-graph.png`** — decision graph view (new).
- **`assets/verification-dashboard.png`** — verification dashboard view (new).
- **`assets/replay-timeline.png`** — replay timeline view (new).
- **`assets/marketplace.png`** — marketplace mockup (new).

#### GitHub Excellence
- **`.github/ISSUE_TEMPLATE/`** — bug report, feature request, RFC proposal, config.
- **`.github/PULL_REQUEST_TEMPLATE.md`** — PR template with spec-impact checklist.
- **`SECURITY.md`** — supported versions, disclosure process, scope, signing.
- **`CODE_OF_CONDUCT.md`** — Contributor Covenant 2.1.
- **`.github/FUNDING.yml`** — funding policy (not currently accepting sponsorship).
- **`ROADMAP.md`** — themed roadmap: Spec, Reference Engine, Adapters, Registry, Discipline, Community.

### Added — initial INFINI drop
- **INFINI × Hermes adapter** (`adapters/hermes/`) — governance brain: policy, memory, escalation, audit trails.
- **INFINI × OpenClaw adapter** (`adapters/openclaw/`) — execution runtime: browser, GitHub, terminal, filesystem tools.
- **Hybrid mode** — a Loopfile can declare `ENGINE.delegates.execution` to combine Hermes governance with OpenClaw execution.
- Three runnable demos:
  - `examples/claim-audit/` — claim-audit loop with policy, budget, escalation, audit.
  - `examples/github-pr-review/` — coding loop with file edits, tests, PR.
  - `examples/hybrid-hermes-openclaw/` — the killer demo: Hermes governs, OpenClaw executes, INFINI records.
- **Loop Observatory** section in README. Status: preview.
- Lineage statement in README: *Docker standardized containers. … INFINI standardizes autonomous work.*

### Changed
- **Rebrand: Loom → INFINI.** CLI command is now `infini`. Registry namespace is `infini/`.
- **Spec key: `LOOM:` → `LOOPFILE:`.** The top-level version key in every Loopfile is now `LOOPFILE: "1.0"`.
- **README logo** — replaced with the INFINI logo at `assets/logo.png`.
- **README restructured** — Docker-style ordering: Vision · Demo · Architecture · Observatory · Hermes · OpenClaw · Loopfile · Examples · Marketplace · Registry · Specification · Adapters · Roadmap · Contributing · License · Community.
- **Compatibility matrix** — Hermes and OpenClaw added as first-class rows.

### Removed
- **"Why this is viral"** section from README. Replaced with the calmer, factual lineage statement.

---

## [1.0.0] — 2026-06-28

### Added
- Initial public release.
- Loopfile Specification v1.0 (`spec/loopfile-v1.md`), including:
  - `LOOPFILE`, `name`, `version`, `OBJECTIVE`, `AGENTS`, `STEPS`, `VERIFY`, `BUDGET`, `STOP_WHEN` fields.
  - Formal grammar (`spec/grammar.ebnf`).
  - JSON Schema (`spec/schema.json`).
  - Migration guide (`spec/migration.md`).
  - Engine compatibility matrix (`spec/compatibility.md`).
- `infini` CLI reference implementation:
  - `infini validate`, `infini inspect`, `infini replay`, `infini diff`, `infini ci` shipped.
  - `infini run`, `infini publish`, `infini install` require an engine adapter.
- The 12 canonical loops (Loopfile + essay + fixtures):
  `coding-loop`, `refactor-loop`, `test-gen-loop`, `debug-loop`, `review-loop`, `research-loop`, `content-loop`, `outreach-loop`, `migration-loop`, `doc-sync-loop`, `oncall-loop`, `sre-loop`.
- The **Loop Engineer Prompt** (`prompts/loop-engineer.md`).
- INFINI CI GitHub Action (`ci/`).
- MANIFESTO: *Loops > Chains*.

### Known limitations
- `infini run` requires an engine adapter. The INFINI Reference Engine ships first; Hermes and OpenClaw adapters ship in the same release.
- The Loop Observatory UI is in preview. The Inspector (`infini inspect`) ships; the full annotated timeline, cost waterfall, and replay studio are in active development.
- The public registry (`registry.infini.dev`) is coming soon. Local registry operations work today.

---

## Versioning

- **Spec versions** follow `MAJOR.MINOR` (`1.0`, `1.1`, `2.0`). Minor versions are additive; major versions may break conformance.
- **CLI versions** follow semver independently of the spec.
- **Registry versions** are immutable. Once `infini/coding-loop@1.2` is published, it cannot be republished.

See [`spec/migration.md`](spec/migration.md) for upgrade paths between spec versions.
