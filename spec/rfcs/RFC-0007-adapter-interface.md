# RFC-0007: Adapter Interface

- Start date: 2026-06-28
- Status: draft
- Spec version: N/A (interface contract)
- PR: TBD
- Implementation: SDK scaffold at [`sdk/`](../../sdk/); reference impls in `adapters/`

## Summary

Defines the contract every INFINI engine adapter must implement. The goal:
adding a runtime should require only implementing a small interface, not
forking the CLI.

## Motivation

Today, every agent runtime that wants to support Loopfiles has to figure
out:

- How to parse the YAML.
- How to validate against the schema.
- How to execute the STEPS DAG.
- How to enforce BUDGET.
- How to run VERIFY.
- How to emit a `run.json` trace.
- How to support replay.

Each of these is the same across engines, except for the actual execution.
The adapter interface extracts everything common and leaves only the
engine-specific bits to the adapter author.

## Detailed design

### The interface

An adapter is a module that implements six capabilities. Each capability
is a Python abstract base class (or equivalent in the adapter's language):

```python
from infini.sdk import Adapter, Capability

class MyAdapter(Adapter):
    name = "my-engine"
    spec = "LOOPFILE-1.0"

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

An adapter declares which capabilities it implements via the `@Capability`
decorator. The CLI's `infini engines` command reads this to populate the
compatibility matrix.

### Capability discovery

An adapter ships a manifest at `adapters/<name>/adapter.yaml`:

```yaml
adapter:
  name: hermes
  version: 1.0.0
  spec: LOOPFILE-1.0
  type: governance
  capabilities:
    parse_loopfile: true
    run_loop: true
    verify: true
    inspect_trace: true
    replay: true
    diff: false
  engine:
    type: hermes
    runtime: hermes-os
    min_version: 1.4.0
```

The CLI reads every `adapter.yaml` it can find and registers the adapter.
Adapters can be installed via pip extras (`pip install infini-cli[hermes]`)
or as standalone packages.

### Engine metadata

Adapters expose metadata the CLI uses for display and routing:

```python
class MyAdapter(Adapter):
    name = "my-engine"
    spec = "LOOPFILE-1.0"
    type = "execution"  # governance | execution | hybrid
    description = "..."
    min_engine_version = "1.4.0"
    tools = ["browser", "github", "terminal"]
    agent_roles = {
        "builder":   "my.coder.CoderAgent",
        "verifier":  "my.tester.TesterAgent",
        ...
    }
```

### Trace extensions

Adapters can extend the trace with engine-specific fields:

```python
class MyAdapter(Adapter):
    trace_extensions = {
        "governance": {
            "policy_violations": "array",
            "escalations": "array",
            "audit_hash": "string",
        }
    }
```

The CLI's `infini inspect` command renders these in the Observatory under
engine-specific tabs.

### Hybrid mode

An adapter can declare that it delegates to another adapter:

```python
class HermesAdapter(Adapter):
    name = "hermes"
    delegates = {
        "execution": "openclaw",  # delegate execution to OpenClaw
    }
```

When a Loopfile's `ENGINE.delegates.execution` is set, the Hermes adapter
handles governance; the OpenClaw adapter handles execution. Both write to
the same `run.json`.

## Alternatives considered

- **One big interface (adapter implements everything).** Rejected — too
  much work for a minimal adapter. Capability-based lets adapters ship
  partial conformance.
- **Adapter inherits from CLI's reference engine.** Rejected — couples
  adapters to the reference impl's internals.
- **No interface; adapters are just YAML manifests.** Rejected — the
  manifest describes metadata, but execution still needs code.
- **WebAssembly adapters.** Considered. Rejected for v1 — adds a runtime
  dependency. Could be revisited if a language-agnostic interface is
  needed.

## Backwards compatibility

v1.0. No prior version. The interface is part of v1.0; adapters that
implement it are conformant.

## Conformance impact

This RFC *defines* the adapter contract. The compatibility matrix in
[`spec/compatibility.md`](../compatibility.md) tracks which adapters
implement which capabilities.

## Open questions

- Should the interface be language-agnostic (e.g., via a JSON-RPC
  protocol)? Current answer: no, Python is the reference. Adapters in
  other languages can wrap the CLI's Python interface.
- How are adapter upgrades handled when the spec revs? Current answer: the
  adapter declares its `spec` version; the CLI refuses to run a Loopfile
  on an adapter that doesn't support its spec version.

## Future possibilities

- v1.1: adapter conformance test suite (`infini adapter test`).
- v1.2: adapter marketplace — browse and install adapters from the registry.
- v2.0: language-agnostic adapter protocol (JSON-RPC or WASM).

## Acknowledgements

The interface design is borrowed from OpenTelemetry's SDK, Docker's
containerd runtime interface, and LLVM's pass interface.
