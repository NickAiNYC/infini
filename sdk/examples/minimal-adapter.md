# Minimal Adapter (PARSE only)

The smallest possible INFINI adapter. Implements only `PARSE` — enough to
register with the CLI and validate Loopfiles, but not enough to run them.

Use this as a starting point for a real adapter. Add capabilities one at
a time, running the conformance suite after each.

---

## `my_adapter/__init__.py`

```python
from infini.sdk import Adapter, Capability
from infini.types import Loopfile
from infini.parse import parse_with_schema

class MinimalAdapter(Adapter):
    name = "minimal"
    spec = "LOOPFILE-1.0"
    type = "execution"
    description = "Minimal adapter — parse-only. Useful as a starting point."
    min_engine_version = "0.1.0"
    tools = []
    agent_roles = {}

    @Capability.PARSE
    def parse(self, loopfile_yaml: str) -> Loopfile:
        # The SDK ships a schema-based parser; use it.
        return parse_with_schema(loopfile_yaml, schema="spec/schema.json")

    # No RUN, VERIFY, INSPECT, REPLAY, DIFF — this adapter can only parse.
```

---

## `pyproject.toml`

```toml
[project]
name = "my-adapter"
version = "0.1.0"
dependencies = ["infini-sdk"]

[project.entry-points."infini.adapters"]
minimal = "my_adapter:MinimalAdapter"
```

---

## `adapter.yaml`

```yaml
adapter:
  name: minimal
  version: 0.1.0
  spec: LOOPFILE-1.0
  type: execution
  description: Minimal adapter — parse-only.

engine:
  type: minimal
  runtime: minimal-runtime
  min_version: 0.1.0

capabilities:
  parse_loopfile: true
  run_loop: false
  verify: false
  inspect_trace: false
  replay: false
  diff: false
```

---

## `examples/hello.yaml`

```yaml
LOOPFILE: "1.0"
name: hello
version: 1.0.0
description: Minimal example — validates with the minimal adapter.

OBJECTIVE: "Say hello."

AGENTS:
  - { name: builder, role: builder, model_tier: haiku }

STEPS:
  - { id: s1, name: greet, action: hello, uses: builder, produces: [greeting.txt] }

VERIFY:
  syntactic: ["greeting.txt:exists"]
  semantic: []
  confidence_threshold: 0

BUDGET: { dollars: 1, minutes: 5 }

STOP_WHEN: ["all_verify_passed"]
```

---

## Test it

```bash
pip install -e .

# Register the adapter
infini engines
# → minimal  (PARSE only)

# Validate a Loopfile
infini validate examples/hello.yaml --engine minimal
# → valid

# Try to run it (will fail — no RUN capability)
infini run examples/hello.yaml --engine minimal
# → error: adapter 'minimal' does not implement RUN
```

---

## Next steps

Add capabilities one at a time:

1. Implement `INSPECT` next. It's the easiest after `PARSE` — you just
   load a `run.json` from disk.
2. Implement `RUN`. This is the bulk of the work.
3. Implement `VERIFY`. Builds on `RUN`.
4. Implement `REPLAY`. Requires `STATE` persistence from `RUN`.
5. Implement `DIFF`. Standalone.

Run `infini adapter test` after each capability to confirm conformance.

When all six capabilities pass, your adapter is fully conformant and
eligible for a ✅ row in [`spec/compatibility.md`](../../spec/compatibility.md).
