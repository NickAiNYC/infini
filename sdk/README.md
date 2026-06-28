# INFINI Adapter SDK

The Adapter SDK is the contract every INFINI engine adapter implements.
The goal: adding a runtime should require only implementing a small
interface, not forking the CLI.

> **INFINI runs Loopfiles.** Engines that conform to the spec can run
> Loopfiles. This SDK is how they conform.

---

## The six capabilities

Every adapter declares which of six capabilities it implements. Partial
conformance is allowed and tracked in [`spec/compatibility.md`](../spec/compatibility.md).

| Capability | What it does | Required for |
| --- | --- | --- |
| `PARSE`    | Parse and validate a Loopfile. | Adapter registration. |
| `RUN`      | Execute the STEPS DAG. | `infini run`. |
| `VERIFY`   | Run syntactic and semantic checks. | `verified` outcome. |
| `INSPECT`  | Emit a `run.json` trace. | `infini inspect`. |
| `REPLAY`   | Resume from any step. | `infini replay`. |
| `DIFF`     | Semantic diff between Loopfiles. | `infini diff`. |

`PARSE` is the only required capability. An adapter that ships only
`PARSE` is registered and listed in `infini engines`; it can validate
Loopfiles but not run them.

---

## The interface

The SDK is a set of abstract base classes. The reference implementation is
in Python; adapters in other languages wrap the CLI's Python interface.

```python
# my_adapter/__init__.py
from infini.sdk import Adapter, Capability
from infini.types import Loopfile, State, Trace, VerifyResult, Diff

class MyAdapter(Adapter):
    name = "my-engine"
    spec = "LOOPFILE-1.0"
    type = "execution"  # governance | execution | hybrid
    description = "My agent runtime."
    min_engine_version = "1.0.0"
    tools = ["browser", "github", "terminal", "file_system"]
    agent_roles = {
        "builder":   "my.coder.CoderAgent",
        "verifier":  "my.tester.TesterAgent",
        "critic":    "my.reviewer.ReviewerAgent",
        "researcher":"my.scraper.ScraperAgent",
        "planner":   "my.planner.PlannerAgent",
    }

    @Capability.PARSE
    def parse(self, loopfile_yaml: str) -> Loopfile:
        """Parse and validate a Loopfile. Returns a structured Loopfile."""

    @Capability.RUN
    def run(self, loopfile: Loopfile, state: State) -> State:
        """Execute the STEPS DAG. Return the final state."""

    @Capability.VERIFY
    def verify(self, loopfile: Loopfile, state: State) -> VerifyResult:
        """Run syntactic and semantic checks. Return pass/fail + confidence."""

    @Capability.INSPECT
    def inspect(self, run_dir: Path) -> Trace:
        """Load a run's trace. Returns a structured Trace."""

    @Capability.REPLAY
    def replay(self, run_dir: Path, from_step: str, mutations: dict) -> Trace:
        """Replay a run from a step, with optional input mutations."""

    @Capability.DIFF
    def diff(self, v1: Loopfile, v2: Loopfile) -> Diff:
        """Produce a semantic diff between two Loopfiles."""
```

Full interface reference: [`adapter-interface.md`](adapter-interface.md).

---

## Install

```bash
pip install infini-sdk
```

The SDK is a separate package from the CLI. Adapters depend on the SDK,
not on the CLI.

---

## Anatomy of an adapter

An adapter ships:

```
my-adapter/
├── pyproject.toml          # depends on infini-sdk
├── my_adapter/
│   ├── __init__.py         # exports MyAdapter
│   ├── parser.py           # PARSE implementation
│   ├── runner.py           # RUN implementation
│   ├── verifier.py         # VERIFY implementation
│   ├── inspector.py        # INSPECT implementation
│   ├── replay.py           # REPLAY implementation (optional)
│   └── differ.py           # DIFF implementation (optional)
├── adapter.yaml            # adapter manifest
├── examples/
│   └── my-loop.yaml        # at least one runnable example
└── README.md
```

The `adapter.yaml` manifest is what the CLI reads to register the adapter.
See [`adapters/hermes/adapter.yaml`](../adapters/hermes/adapter.yaml) for
a real example.

---

## Capability discovery

The CLI discovers adapters via Python entry points. An adapter's
`pyproject.toml` declares:

```toml
[project.entry-points."infini.adapters"]
my-engine = "my_adapter:MyAdapter"
```

The CLI scans entry points on startup; `infini engines` lists them.

---

## Trace extensions

Adapters can extend the trace with engine-specific fields. The Hermes
adapter, for example, adds a `governance` field; the OpenClaw adapter
adds a `tools` field.

```python
class HermesAdapter(Adapter):
    trace_extensions = {
        "governance": {
            "policy_violations": "array",
            "escalations":       "array",
            "audit_hash":        "string",
            "memory_refs":       "array",
        }
    }
```

The CLI's `infini inspect` command renders these in the Observatory under
engine-specific tabs.

---

## Hybrid mode

An adapter can declare that it delegates to another adapter. This is how
the hybrid demo works: Hermes governs, OpenClaw executes.

```python
class HermesAdapter(Adapter):
    name = "hermes"
    delegates = {
        "execution": "openclaw",
    }
```

When a Loopfile's `ENGINE.delegates.execution` is set, the Hermes adapter
handles governance; the OpenClaw adapter handles execution. Both write to
the same `run.json`.

---

## Conformance test suite

The SDK ships a conformance test suite. Run it against your adapter:

```bash
infini adapter test my-adapter/
```

The suite tests each declared capability against a set of canonical
Loopfiles and expected traces. An adapter that passes the suite is
eligible for a ✅ in the compatibility matrix.

---

## Examples

- [`adapters/hermes/`](../adapters/hermes/) — full reference implementation
  of a governance adapter.
- [`adapters/openclaw/`](../adapters/openclaw/) — full reference
  implementation of an execution adapter.
- [`sdk/examples/minimal-adapter/`](examples/) — the smallest possible
  adapter (PARSE only).

---

## License

MIT. See [repository LICENSE](../LICENSE).
