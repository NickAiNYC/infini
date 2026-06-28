# Golden Example: Research Assistant

> **The proof.** This Loopfile runs identically across multiple engines.
> Same YAML, same verification, same trace shape — different runtimes.

## The loop

A multi-source research assistant that answers a question using at least
three primary sources, verifies every claim has a citation, and produces
a research brief.

## Run it

```bash
# On the INFINI Reference Engine (mock mode — no API key needed)
infini run examples/golden-research-assistant/research-loop.yaml --mock

# On Hermes (governance brain)
infini run examples/golden-research-assistant/research-loop.yaml --engine hermes

# On OpenClaw (execution runtime)
infini run examples/golden-research-assistant/research-loop.yaml --engine openclaw

# Inspect the trace in the Observatory
infini ui runs/latest/run.json
```

The **exact same YAML** runs on all three engines. That's the portability
layer. That's the point.

## Why this is a "golden" example

- **Portable.** Uses only spec-defined features. No engine-specific assumptions.
- **Verified.** Two-tier verification: syntactic (citation exists) + semantic (source quality).
- **Bounded.** $6 / 20m budget. Stops when verified or after 3 iterations.
- **Inspectable.** Produces a `run.json` trace the Observatory can render in 3D.
- **Replayable.** `infini replay runs/latest/ --step s2` to time-travel.

## Files

- [`research-loop.yaml`](research-loop.yaml) — the Loopfile
- [`expected-output.md`](expected-output.md) — what a verified run produces
- [`README.md`](README.md) — this file
