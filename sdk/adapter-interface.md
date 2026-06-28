# Adapter Interface Reference

The full contract every INFINI adapter implements. This document is
normative for adapter authors.

> See [`README.md`](README.md) for the overview. This document is the
> detailed reference.

---

## Types

The SDK exposes these types. All are dataclasses; all are JSON-serializable.

### `Loopfile`

A parsed and validated Loopfile.

```python
@dataclass
class Loopfile:
    spec_version: str          # "1.0"
    name: str
    version: str               # semver
    description: str | None
    objective: str
    agents: list[Agent]
    steps: list[Step]
    verify: Verify
    budget: Budget
    stop_when: list[str]
    lessons: Lessons | None
    state: StateConfig | None
    engine: EngineConfig | None
```

### `Agent`

```python
@dataclass
class Agent:
    name: str
    role: Literal["builder", "verifier", "critic", "researcher", "planner"]
    model_tier: str
    tools: list[str]
```

### `Step`

```python
@dataclass
class Step:
    id: str
    name: str
    action: str
    uses: str                  # agent name
    produces: list[str]
    depends_on: list[str]
    retry: RetryConfig | None
```

### `Verify`

```python
@dataclass
class Verify:
    syntactic: list[str]       # check strings
    semantic: list[str]
    confidence_threshold: int  # 0-100
```

### `Budget`

```python
@dataclass
class Budget:
    dollars: float
    minutes: float
    tokens: int | None
```

### `State`

The runtime state of a loop, passed between steps and persisted for replay.

```python
@dataclass
class State:
    step_outputs: dict[str, list[str]]   # step_id → artifact paths
    artifacts: dict[str, bytes]          # path → content
    memory: list[Lesson]                 # lessons recalled before this run
    lessons_appended: list[Lesson]       # lessons added during this run
    budget_spent: Budget
    iteration: int
```

### `VerifyResult`

```python
@dataclass
class VerifyResult:
    syntactic: list[CheckResult]
    semantic: list[CheckResult]
    mean_confidence: float
    threshold_met: bool
    all_passed: bool

@dataclass
class CheckResult:
    check: str
    passed: bool
    confidence: float | None  # only for semantic
    detail: str | None
```

### `Trace`

```python
@dataclass
class Trace:
    loopfile: str             # "infini/coding-loop@1.0"
    loopfile_hash: str        # sha256
    engine: EngineInfo
    started_at: datetime
    ended_at: datetime | None
    iterations: int
    steps: list[StepTrace]
    verifications: list[CheckResult]
    budget: BudgetSpent
    outcome: Literal["verified", "unverified", "budget_exceeded", "escalated", "error"]
    lessons: list[str]
    provenance: Provenance
    extensions: dict[str, dict]  # engine-specific
```

### `StepTrace`

```python
@dataclass
class StepTrace:
    id: str
    name: str
    status: Literal["ok", "failed", "retried", "skipped"]
    started_at: datetime
    ended_at: datetime
    cost: Cost
    artifacts: list[str]
    agent: str
    action: str
    retry_attempt: int | None
    extensions: dict[str, dict]
```

---

## The `Adapter` base class

```python
class Adapter:
    # Metadata — subclasses override
    name: str                    # e.g. "hermes"
    spec: str                    # e.g. "LOOPFILE-1.0"
    type: Literal["governance", "execution", "hybrid"]
    description: str
    min_engine_version: str
    tools: list[str]             # tools this adapter can call
    agent_roles: dict[str, str]  # Loopfile role → adapter's agent class
    trace_extensions: dict[str, dict[str, str]]  # extension name → field → type
    delegates: dict[str, str]    # capability → adapter name (hybrid mode)

    # Capabilities — subclasses decorate
    @Capability.PARSE
    def parse(self, loopfile_yaml: str) -> Loopfile: ...

    @Capability.RUN
    def run(self, loopfile: Loopfile, state: State) -> State: ...

    @Capability.VERIFY
    def verify(self, loopfile: Loopfile, state: State) -> VerifyResult: ...

    @Capability.INSPECT
    def inspect(self, run_dir: Path) -> Trace: ...

    @Capability.REPLAY
    def replay(self, run_dir: Path, from_step: str, mutations: dict) -> Trace: ...

    @Capability.DIFF
    def diff(self, v1: Loopfile, v2: Loopfile) -> Diff: ...
```

---

## Capability contracts

### `PARSE`

**Input:** raw Loopfile YAML (string).

**Output:** a `Loopfile` dataclass.

**Contract:**
- Must accept any v1.0 Loopfile.
- Must reject invalid Loopfiles with a structured `ValidationError` pointing to the offending field.
- Must use [`spec/schema.json`](../spec/schema.json) for validation.
- Must preserve key order from the source file.

### `RUN`

**Input:** a `Loopfile`, an initial `State`.

**Output:** the final `State`.

**Contract:**
- Must execute `STEPS` as a DAG, honoring `depends_on`.
- Must enforce `BUDGET` on dollars, minutes, and tokens.
- Must mark the run `budget_exceeded` and stop if any ceiling is breached.
- Must persist `STATE` per step (for replay).
- Must emit a `run.json` trace per spec §10.
- Must run at most `STOP_WHEN` iterations.

### `VERIFY`

**Input:** a `Loopfile`, the final `State`.

**Output:** a `VerifyResult`.

**Contract:**
- Must run every `syntactic` check and report pass/fail per check.
- Must run every `semantic` check and report confidence (0-100) per check.
- Must compute the mean confidence across semantic checks.
- Must mark the loop `verified` only if all checks pass and the mean ≥ `confidence_threshold`.

### `INSPECT`

**Input:** a path to a run directory.

**Output:** a `Trace`.

**Contract:**
- Must load `run.json` from the run directory.
- Must verify the trace's signature (per [RFC-0009](../spec/rfcs/RFC-0009-provenance.md)).
- Must return a structured `Trace` dataclass.

### `REPLAY`

**Input:** a run directory, a step ID, optional input mutations.

**Output:** a new `Trace` (the replay's trace).

**Contract:**
- Must restore state to just before the named step.
- Must apply input mutations to the step's parameters.
- Must execute from the named step forward.
- Must emit a new `run.json` in a new run directory.
- Must set `replay_of` and `replay_from_step` in the new trace.
- Must not modify the original run.

### `DIFF`

**Input:** two `Loopfile` dataclasses.

**Output:** a `Diff`.

**Contract:**
- Must produce a semantic diff, not a line diff.
- Must highlight changes to `OBJECTIVE`, `AGENTS`, `STEPS`, `VERIFY`, `BUDGET`, `STOP_WHEN`.
- Must classify the change as `additive`, `compatible`, or `breaking`.
- Must be human-readable when rendered as markdown.

---

## Hybrid mode

When an adapter declares `delegates`, it routes certain capabilities to
another adapter. The most common pattern: a governance adapter (Hermes)
delegates execution to an execution adapter (OpenClaw).

```python
class HermesAdapter(Adapter):
    name = "hermes"
    delegates = {"execution": "openclaw"}

    @Capability.RUN
    def run(self, loopfile, state):
        # 1. Run governance steps (policy_check, audit_pre, etc.)
        state = self._run_governance(loopfile, state)

        # 2. Delegate execution to OpenClaw
        openclaw = self.registry.get("openclaw")
        state = openclaw.run(loopfile, state)

        # 3. Run post-execution governance (audit_post, verify_governed)
        state = self._run_post_governance(loopfile, state)
        return state
```

Both adapters write to the same `run.json`. The trace's `extensions`
field carries both `governance` (from Hermes) and `tools` (from OpenClaw).

---

## Conformance testing

The SDK ships a conformance test suite. To run it against your adapter:

```bash
infini adapter test my-adapter/
```

The suite:
1. Loads your `adapter.yaml`.
2. For each declared capability, runs the canonical test cases.
3. Reports pass/fail per capability, with details on failures.
4. Outputs a conformance row suitable for inclusion in
   [`spec/compatibility.md`](../spec/compatibility.md).

An adapter that passes the suite is eligible for a ✅ in the matrix.

---

## Versioning

The SDK follows the spec version. SDK 1.0.x supports spec 1.0. SDK 1.1.x
supports spec 1.0 and 1.1. SDK 2.0.x supports spec 1.1 and 2.0.

Adapters declare their supported spec version in `adapter.yaml`. The CLI
refuses to run a Loopfile on an adapter that doesn't support its spec
version.

---

## See also

- [RFC-0007: Adapter Interface](../spec/rfcs/RFC-0007-adapter-interface.md) — the normative RFC.
- [`adapters/hermes/`](../adapters/hermes/) — reference governance adapter.
- [`adapters/openclaw/`](../adapters/openclaw/) — reference execution adapter.
- [`spec/compatibility.md`](../spec/compatibility.md) — the conformance matrix.
