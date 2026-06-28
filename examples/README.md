# INFINI Examples

Runnable demos. Each example is a self-contained folder with a Loopfile, an expected-output spec, and a README explaining what the demo shows.

> For canonical loops, see [`../loops/`](../loops/). For engine adapters, see [`../adapters/`](../adapters/). This directory is for **demos that show INFINI in action**.

---

## The three signature demos

| Demo | Engine | What it shows |
| --- | --- | --- |
| [`hermes-governed-growth/`](hermes-governed-growth/)     | Hermes    | Governance brain: policy, budget, escalation, audit trail. |
| [`openclaw-agent-loop/`](openclaw-agent-loop/)          | OpenClaw  | Execution runtime: file edits, tests, PR creation. |
| [`hybrid-hermes-openclaw/`](hybrid-hermes-openclaw/)     | Both      | **The market hook.** Hermes governs. OpenClaw executes. INFINI records and replays. |

If you only run one demo, run the hybrid.

---

## Running a demo

```bash
# From the repo root
infini run examples/hybrid-hermes-openclaw/governed-coding-loop.yaml

# Inspect the trace
infini inspect runs/latest/

# Replay from any step
infini replay runs/latest/ --step s4
```

Each demo's README shows expected output and explains the trace shape.

---

## Writing your own example

1. Copy the closest demo folder.
2. Edit the Loopfile. Keep `LOOPFILE: "1.0"` as the version.
3. Update `expected-output.md` so CI knows what success looks like.
4. Update the README to explain what your demo shows.
5. PR to `examples/`.

Examples don't have to be canonical — they just have to be illustrative.

---

## License

MIT. See [repository LICENSE](../LICENSE).
