# INFINI Examples

Runnable demos. Each example is a self-contained directory with a Loopfile
and a README explaining what it demonstrates.

> For canonical loops, see [`../loops/`](../loops/).
> For engine adapters, see [`../adapters/`](../adapters/).
> For older demos, see [`_deprecated/`](_deprecated/).

## The curated set

| Example | Purpose |
|---------|---------|
| [`hello-world/`](hello-world/) | Smallest valid Loopfile — one agent, one step, one artifact |
| [`claim-audit/`](claim-audit/) | Evidence-heavy verification workflow with policy, budget, escalation |
| [`github-pr-review/`](github-pr-review/) | Engineering workflow — file edits, tests, PR creation |
| [`squad-loop/`](squad-loop/) | Declarative mapping of imperative multi-agent collaboration |

## Running an example

```bash
# From the repo root
infini run examples/hello-world/Loopfile.yaml --mock

# Inspect the trace
infini inspect runs/latest/

# Replay from any step
infini replay runs/latest/ --step s1
```

Each example's README shows expected output and explains the trace shape.

## Writing your own example

1. Copy the closest example folder.
2. Edit the Loopfile. Keep `LOOPFILE: "1.0"` as the version.
3. Update `expected-output.md` so CI knows what success looks like.
4. Update the README to explain what your demo shows.
5. PR to `examples/`.

Examples don't have to be canonical — they just have to be illustrative.

## License

MIT. See [repository LICENSE](../LICENSE).
