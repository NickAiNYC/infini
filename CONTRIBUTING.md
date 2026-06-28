# Contributing to Loom

Thanks for being here. Loom is built in the open, and we mean it.

## What we accept

| Type | Where | How |
|------|-------|-----|
| Spec changes | `spec/` | Open an RFC in `spec/rfcs/` first |
| New canonical loops | `loops/` | PR with Loopfile + 300-word essay + 3 fixtures |
| Engine adapters | `cli/adapters/` | PR with adapter + compatibility manifest |
| Inspector / replay / diff improvements | `cli/` | PR with tests |
| Essays, benchmarks | `docs/` | PR or discussions post first |
| Bug fixes | anywhere | PR with reproduction |

## How to contribute a loop

1. Pick a loop shape that does not exist yet (see `loops/` for the 12 canonicals).
2. Write the Loopfile. Run `loom validate` on it. Fix all errors.
3. Write a 300-word essay in `docs/essays/{loop-name}.md` explaining when to use it, when not to, and the trade-offs.
4. Add 3 fixtures in `tests/fixtures/{loop-name}/` and 3 expected outputs in `tests/expected/{loop-name}/`.
5. Open a PR. CI will run `loom ci` against your fixtures.

We merge loops that:
- Have ≥2 verification tiers
- Have a non-trivial essay (not just a description of the YAML)
- Have fixtures that actually exercise the loop
- Follow the existing naming and structure conventions

## How to contribute an engine adapter

If you maintain or use an agent runtime (LangGraph, CrewAI, OpenClaw, HermesAgents, AutoGen, etc.), you can make it Loom-compatible by writing an adapter that:

1. Reads a Loopfile
2. Validates it (`loom validate`)
3. Maps `AGENTS` to your runtime's agent primitives
4. Maps `STEPS` to your runtime's graph / chain / dag
5. Emits `trace.jsonl` per the trace spec
6. Writes `loop_state.json` per the state spec

Ship it as `loom-{engine}-adapter`. We will list it in `cli/adapters/README.md`.

## Sign your commits

We require DCO sign-off (`git commit -s`). It's the lightest-weight contributor agreement that still lets us relicense defensively if needed.

## Be excellent

- Disagreements are fine. Disrespect is not.
- We do not merge PRs from accounts that have been abusive in any Loom space.
- We follow the Contributor Covenant 2.1.

## RFC process

Spec changes go through RFCs. The bar is intentionally low for v1 — we would rather ship and learn than debate forever.

1. Copy `spec/rfcs/_template.md` to `spec/rfcs/{NNN}-{short-name}.md`.
2. Fill it in. Be concrete.
3. Open a PR. We discuss for at least 7 days.
4. We accept, reject, or defer. Accepted RFCs become the next spec version.

## Office hours

Weekly, Thursdays 10am PT. See `docs/community.md` for the link. We do not require PRs to come through office hours, but it usually makes them faster.

## Recognition

Every contributor who gets a PR merged is added to `CONTRIBUTORS.md`. We do not gate this on size — first commit counts.
