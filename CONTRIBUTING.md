# Contributing to INFINI

INFINI is an open standard. We accept contributions in five categories. Read this file before opening a PR.

> **INFINI runs Loopfiles.** If you're contributing, you're either changing what a Loopfile can say, what an engine can do with one, or what the ecosystem looks like around both.

---

## Code of conduct

Be excellent to each other. Disagree about ideas, not about people. Reject contributions that are dismissive, hostile, or that waste maintainers' time. Sign your commits.

---

## What we accept

| Category | Where it lives | How to propose |
| --- | --- | --- |
| **Spec changes** | `spec/` | Open an RFC. See [`spec/migration.md`](spec/migration.md) for versioning rules. |
| **New canonical loops** | `loops/` | PR a Loopfile + essay + fixtures. |
| **Engine adapters** | `adapters/<name>/` | PR the adapter manifest + README + at least one example Loopfile. |
| **Inspector / replay / diff / CLI** | `cli/` | PR with tests against the conformance suite. |
| **Essays and benchmarks** | `docs/` | PR with a markdown essay and, where applicable, benchmark fixtures. |

---

## Help Wanted: Community Adapters

The easiest high-impact contribution is a new adapter. Each adapter makes
the portability claim real for one more runtime. These are scaffolded but
not yet implemented — pick one and become its maintainer:

| Adapter | Runtime | Status |
| --- | --- | --- |
| [`adapters/crewai/`](adapters/crewai/) | CrewAI | help wanted |
| [`adapters/langgraph/`](adapters/langgraph/) | LangGraph | help wanted |
| [`adapters/mastra/`](adapters/mastra/) | Mastra | help wanted |
| [`adapters/goose/`](adapters/goose/) | Goose (Block) | help wanted |
| [`adapters/codex/`](adapters/codex/) | Codex (OpenAI) | help wanted |

Each placeholder has a `README.md` with the exact steps to get started.
The [Adapter SDK](sdk/) gives you the base class; you implement the six
capabilities. Run `infini conformance` to verify.

If you build one, your name goes in [`CONTRIBUTORS.md`](CONTRIBUTORS.md)
as that adapter's maintainer.

---

## Local Development

```bash
git clone https://github.com/NickAiNYC/infini
cd infini

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e './cli[dev]'

# Initialize the SQLite database and skills directory
infini setup

# Run conformance tests
infini conformance tests/conformance/ --engine infini --mock

# Run unit tests
python -m pytest cli/tests/ -q

# Try an example
infini run examples/hello-world.yaml --mock

# Or use the Makefile
make setup    # creates venv + installs
make test     # runs pytest
make conformance  # runs conformance suite
make verify   # runs everything
```

---

## Spec changes (RFCs)

Spec changes are the highest-leverage and most carefully reviewed contributions.

1. Open an issue with `RFC:` in the title describing the problem.
2. A maintainer will assign you an RFC number (e.g., `RFC-0007`).
3. PR a file at `spec/rfcs/RFC-0007.md` with: problem, proposed change, alternatives, backwards-compatibility, conformance impact.
4. The RFC is discussed in GitHub Discussions. Two-week minimum review.
5. Once accepted, the spec is updated and a migration entry is added to [`spec/migration.md`](spec/migration.md).

Spec changes that break conformance require a major version bump (`1.x → 2.0`).

---

## New canonical loops

Canonical loops are the **Design Patterns book** for agent work. They are curated, not crowdsourced.

A canonical loop PR must include:

- `loops/<name>/Loopfile.yaml` — the Loopfile itself.
- `loops/<name>/essay.md` — a 500–1500 word essay explaining *why* this loop exists, *when* to use it, and *when not* to.
- `loops/<name>/fixtures/` — at least one fixture set the loop can be tested against.
- `loops/<name>/expected/` — the expected trace shape, for CI.

The bar is high. A loop that's just "another coding loop with a twist" is not canonical — it's an example. Examples go in `examples/`.

---

## Engine adapters

An engine adapter PR must include:

- `adapters/<name>/README.md` — what the adapter does, when to use it.
- `adapters/<name>/adapter.yaml` — the adapter manifest (capabilities, engine type, trace extensions).
- `adapters/<name>/examples/<loop>.yaml` — at least one runnable example.
- A conformance row in [`spec/compatibility.md`](spec/compatibility.md).

Adapters must implement at least **Parse Loopfile** ✅. Full conformance (Run, Verify, Inspect, Replay, Diff) is encouraged but not required for merge.

Adapters whose repos go 90 days without a commit are marked stale in the compatibility matrix.

---

## CLI and tooling

CLI changes (`cli/`) must:

- Include tests against the conformance suite in `cli/tests/`.
- Not break the `run.json` trace schema without a spec RFC.
- Pass `infini validate` on every example Loopfile in the repo.

---

## Essays and benchmarks

Essays (`docs/`) are how the ecosystem learns. We accept:

- **Loop design patterns** — when to use a verify-heavy loop vs. a plan-heavy loop, etc.
- **Anti-patterns** — what *not* to do, and why.
- **Verification bible** — patterns for writing good `VERIFY` blocks.
- **Cost optimization guide** — how to write loops that cost less without sacrificing correctness.
- **Loop psychology** — the human side of working with autonomous loops.
- **Benchmarks** — comparative runs of canonical loops across engines. Must include raw `run.json` traces.

---

## Commit and PR conventions

- Sign your commits (`git commit -S`).
- Use [Conventional Commits](https://www.conventionalcommits.org/): `feat:`, `fix:`, `docs:`, `spec:`, `chore:`.
- One PR per concern. Don't bundle a spec change with a CLI change.
- PRs that touch `spec/` must link to an RFC issue.

---

## Release process

- Spec releases follow semver: `1.0` → `1.1` (additive) → `2.0` (breaking).
- CLI releases follow semver independently: `infini 1.4.2`.
- Registry versions are immutable. Once `infini/coding-loop@1.2` is published, it cannot be republished.
- Every release updates [`CHANGELOG.md`](CHANGELOG.md).

---

## Office hours

Weekly office hours are held on Discord. See [`docs/community.md`](docs/community.md) for the current schedule and the agenda doc.

---

## License of contributions

By contributing, you agree that your contributions are licensed under the same terms as the file you're editing:

- `spec/` and `docs/` — CC-BY-4.0
- `cli/`, `ci/`, `adapters/` — MIT
- `loops/`, `examples/` — MIT

---

## The bar

The bar is not "this is a good idea." The bar is "this makes INFINI more useful to someone who is shipping real loops in production." If your PR clears that bar, we will merge it. If it doesn't, we'll tell you why.

We are shipping first. Join us.
