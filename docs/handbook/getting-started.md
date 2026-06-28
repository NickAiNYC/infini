# Getting Started

> 15-minute read. By the end, you'll have run your first Loopfile and
> inspected its trace.

## 1. Install

```bash
pip install infini-cli
```

## 2. Run your first loop

```bash
git clone https://github.com/NickAiNYC/infini
cd infini
infini run examples/golden-research-assistant/research-loop.yaml --mock
```

Mock mode is deterministic — same input, same output. No API key needed.

## 3. Inspect the trace

```bash
infini inspect runs/latest/
```

## 4. Open the Observatory

```bash
infini ui runs/latest/run.json
```

## 5. Replay from a step

```bash
infini replay runs/latest/ --step s2
```

## 6. Write your own

```bash
infini init --target my-first-loop
cd my-first-loop
infini validate Loopfile
infini run Loopfile --mock
```

## What's next

- Read [Why Loopfiles?](why-loopfiles.md)
- Read the [Manifesto](../../MANIFESTO.md) — *Loops > Chains*
- Browse the [13 design patterns](../patterns/)
- Open an [RFC](../../spec/rfcs/) if the spec is missing something
