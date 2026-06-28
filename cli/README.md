# INFINI CLI

The reference implementation of the `infini` command-line tool.

> The CLI is the **INFINI Reference Engine**. It conforms to the same Loopfile spec as every other engine. The only asymmetry: it ships first with new spec features, since the spec is developed against it.

---

## Install

```bash
pip install infini-cli

# With adapter extras
pip install infini-cli[hermes,openclaw]

# From source
git clone https://github.com/NickAiNYC/infini
cd infini/cli && pip install -e .
```

Requires Python 3.10+.

---

## Commands

```bash
infini validate  [Loopfile]   # check spec compliance
infini run       [Loopfile]   # execute a loop (--mock for no API key)
infini inspect   [run_dir]    # inspect a trace (--web opens Observatory, coming soon)
infini replay    [run_dir]    # time-travel debug from any step
infini diff      [v1] [v2]    # semantic diff between loops or traces
infini ui        [trace]      # launch the Observatory web app
infini engines                # list detected adapters (reads adapter.yaml)
infini init      [--target]   # scaffold a minimal project (Loopfile, loops/, state/, runs/)
infini new       <name>       # create a new project scaffold
infini graph     [Loopfile]   # render a simple ASCII graph of steps
infini benchmark [Loopfile]   # preview benchmark estimate (real profiling needs a run)
```

### Commands not yet implemented (planned)

```bash
infini install   [loop_ref]   # pull from registry (planned — registry not yet live)
infini publish   [Loopfile]   # push to registry (planned)
infini ci        [Loopfile]   # run loop against fixtures (GitHub Action)
infini search    [query]      # search the registry (planned)
infini migrate   [Loopfile]   # migrate a Loopfile between spec versions
infini keys generate           # generate a publisher signing keypair
```

### Mock mode

`infini run --mock` simulates LLM calls so you can run any Loopfile
without an API key. Useful for evaluation, CI, demos, and the conformance
suite. Mock mode is deterministic: same Loopfile + same seed = same output.

---

## Conformance

The CLI implements:

| Capability       | Status |
| ---------------- | :----: |
| Parse Loopfile   |   ✅   |
| Run Loop         |   ✅   |
| Verify           |   ✅   |
| Inspect Trace    |   ✅   |
| Replay           |   ✅   |
| Diff             |   ✅   |

This makes the CLI the **canonical conformance reference**. If your adapter disagrees with the CLI on a spec edge case, the CLI is right until an RFC says otherwise.

---

## Architecture

```
cli/
├── README.md           # you are here
├── pyproject.toml      # package metadata
├── src/infini/
│   ├── __init__.py
│   ├── main.py         # entrypoint
│   ├── parse.py        # Loopfile parser
│   ├── validate.py     # JSON Schema validator
│   ├── run.py          # reference engine
│   ├── inspect.py      # trace inspector (Loop Observatory)
│   ├── replay.py       # time-travel debugger
│   ├── diff.py         # semantic diff
│   ├── registry.py     # publish/install/search
│   ├── ci.py           # CI mode
│   ├── migrate.py      # spec migration
│   └── keys.py         # signing key management
└── tests/
    ├── conformance/    # spec conformance suite
    ├── fixtures/       # example Loopfiles
    └── expected/       # expected trace shapes
```

The full source ships with the next CLI release. This README documents the contract.

---

## The Loop Observatory

`infini inspect <run_dir>` opens the Loop Observatory — the signature feature.

The Observatory shows, for any run:

- the graph of decisions taken,
- every verification checkpoint and its verdict,
- total runtime, token count, and dollar cost,
- artifacts produced at each step,
- where the loop failed (if it did), and what was retried,
- what changed between iterations,
- governance events (Hermes) and tool calls (OpenClaw) in a swimlane view.

The Inspector ships today. The full UI (annotated timeline, cost waterfall, artifact gallery, replay studio) is in preview.

---

## License

MIT. See [repository LICENSE](../LICENSE).
