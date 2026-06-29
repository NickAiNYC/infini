# Build Your First Portable Agent in 5 Minutes

A step-by-step tutorial. No frameworks to learn. No API keys. Just one
Loopfile, two engines, and a trace diff.

---

## Prerequisites

- Python 3.10+
- `pip` (or `pip3`)

---

## Step 1: Install INFINI (30 seconds)

```bash
pip install infini-cli
```

> Currently install from source while the package stabilizes:
> ```bash
> git clone https://github.com/NickAiNYC/infini
> cd infini
> pip install -e './cli[dev]'
> ```

Verify it works:

```bash
infini --version
```

---

## Step 2: Create a Loopfile (1 minute)

A Loopfile is a YAML document that describes an agent workflow.
This one writes a greeting to a file:

```bash
cat > loop.yaml << 'EOF'
LOOPFILE: "1.0"
name: hello-world
version: 1.0.0
description: "My first portable agent."

OBJECTIVE: "Write a greeting message to greeting.txt."

AGENTS:
  - { name: greeter, role: builder, model_tier: haiku }

STEPS:
  - { id: s1, name: greet, action: write_greeting, uses: greeter, produces: [greeting.txt] }

VERIFY:
  syntactic: ["greeting.txt:exists"]
  semantic: []
  confidence_threshold: 0

BUDGET: { dollars: 1, minutes: 2 }
STOP_WHEN: ["all_verify_passed"]
EOF
```

**What each field does:**

| Field | Purpose |
|-------|---------|
| `OBJECTIVE` | What the loop should accomplish |
| `AGENTS` | Who can do the work (one agent with a role) |
| `STEPS` | What they should do, in order |
| `VERIFY` | How to check the work was done correctly |
| `BUDGET` | How much time and money to spend |
| `STOP_WHEN` | When to stop trying |

---

## Step 3: Validate the Loopfile (30 seconds)

```bash
infini validate loop.yaml
```

Expected output:

```
✓ valid  hello-world@1.0.0  (LOOPFILE-1.0)
  objective: Write a greeting message to greeting.txt.
  agents: 1  steps: 1  verify: 1 syntactic + 0 semantic
  budget: $1.00 / 2m
```

---

## Step 4: Run it on the Reference Engine (1 minute)

```bash
infini run loop.yaml --engine infini --mock
```

Expected output:

```
▶ engine: infini (mock)
▶ s1 greet ✓
▶ verification: ✓ greeting.txt:exists
✓ shipped. trace: runs/latest/run.json
```

Check the output:

```bash
cat runs/latest/run.json | python3 -m json.tool | head -20
```

---

## Step 5: Run it on LangGraph (1 minute)

Without changing a single line of the Loopfile:

```bash
infini run loop.yaml --engine langgraph --mock
```

Expected output:

```
▶ engine: langgraph (mock)
▶ s1 greet ✓
▶ verification: ✓ greeting.txt:exists
✓ shipped (langgraph). trace: runs/latest/run.json
```

---

## Step 6: Compare the Traces (1 minute)

```bash
infini diff runs/reference/run.json runs/langgraph/run.json
```

Expected output:

```
✓ Identical trace structure. Verified. Portable.
```

Both engines produced the same trace structure from the same Loopfile.
One workflow. Two runtimes. Zero changes.

---

## What just happened?

In 5 minutes you:

1. Wrote a portable agent workflow (a Loopfile)
2. Ran it on two different engines (Reference + LangGraph)
3. Verified both produced identical trace structures

This is the core INFINI promise: **write once, run on any engine,
verify it for real.**

---

## Next steps

- [See the 60-second demo](demo.md) — a more realistic example
- [Compare INFINI with other frameworks](comparison.md)
- [Run on 4 engines](https://github.com/NickAiNYC/infini#also-runs-on-4-engines)
- [Add INFINI Guard to your CI](https://github.com/NickAiNYC/infini#ci-integration-30-seconds)
- [Read the full spec](../spec/loopfile-v1.md)
