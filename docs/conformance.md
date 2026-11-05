# INFINI Conformance Suite

[![CI Conformance](https://img.shields.io/github/actions/workflow/status/NickAiNYC/infini/infini-ci.yml?style=flat-square&branch=main&label=CI%20Conformance)](https://github.com/NickAiNYC/infini/actions)
[![Conformance Tests](https://img.shields.io/badge/conformance-8%2F8%20passing-brightgreen?style=flat-square)](tests/conformance/)

The INFINI Conformance Suite validates that an engine or adapter faithfully implements the Loopfile v1.0 specification. Any runtime claiming INFINI compatibility must execute these canonical workflows and produce traces conforming to the standard trace schema.

---

## The 8 Conformance Tests

| Test Name | Loopfile | Asserted Capabilities & Guarantees |
| :--- | :--- | :--- |
| **`simple-loop`** | [`tests/conformance/simple-loop/`](../tests/conformance/simple-loop/) | Asserts minimal 1-step pipeline parse, deterministic execution, and syntactic artifact existence check (`greeting.txt:exists`). |
| **`retry-loop`** | [`tests/conformance/retry-loop/`](../tests/conformance/retry-loop/) | Asserts step retry logic: transient failures trigger retry attempts up to `retry.max` cap without failing the entire run. |
| **`verification-loop`** | [`tests/conformance/verification-loop/`](../tests/conformance/verification-loop/) | Asserts dual-tier verification: syntactic checks (`valid_json`, `exists`) and semantic evaluation (`judge:correctness>=80`) against confidence thresholds. |
| **`cost-loop`** | [`tests/conformance/cost-loop/`](../tests/conformance/cost-loop/) | Asserts budget enforcement: execution terminates with `budget_exceeded` status when dollars or minutes reach declared limits. |
| **`memory-loop`** | [`tests/conformance/memory-loop/`](../tests/conformance/memory-loop/) | Asserts iteration memory: lessons learned from previous iterations are persisted and recalled in subsequent iterations. |
| **`parallel-loop`** | [`tests/conformance/parallel-loop/`](../tests/conformance/parallel-loop/) | Asserts directed acyclic graph (DAG) resolution: steps with `depends_on` execute in topological order across multiple agent roles. |
| **`research-loop`** | [`tests/conformance/research-loop/`](../tests/conformance/research-loop/) | Asserts multi-step pipeline lifecycle (gather -> synthesize -> review) with cross-step artifact handoffs. |
| **`browser-loop`** | [`tests/conformance/browser-loop/`](../tests/conformance/browser-loop/) | Asserts tool interaction lifecycle, parameter passing, and tool execution trace recording. |

---

## Running the Conformance Suite

Run against the reference engine:
```bash
infini conformance tests/conformance/ --mock
```

Run against a specific adapter:
```bash
infini conformance tests/conformance/ --engine hermes --mock
infini conformance tests/conformance/ --engine openclaw --mock
```

To certify an adapter and calculate its official compatibility percentage:
```bash
infini certify adapters/hermes --mock
```
Formula and scoring methodology are detailed in [docs/scoring.md](scoring.md).

