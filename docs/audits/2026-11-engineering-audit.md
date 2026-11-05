# Engineering Baseline Audit: INFINI & Birkin
**Date:** November 5, 2026  
**Auditor:** Principal AI Infrastructure & Staff Security Engineer  
**Scope:** `NickAiNYC/infini` and `NickAiNYC/Birkin`  
**Target Standard:** Institutional AI infrastructure & systems engineering standard (reproducible verification, clear architectural boundaries, fail-closed security, zero promotional exaggeration).

---

## 1. Executive Summary

A comprehensive baseline audit was conducted across the source code, tests, CI workflows, runtime adapters, cryptographic layers, and documentation of both **INFINI** and **Birkin**.

- **INFINI** provides a working declarative workflow runtime and OpenTelemetry GenAI trace exporter, but its GitHub Actions CI failed due to broken path references to golden examples moved in a previous refactoring. Furthermore, while the built-in reference engine is fully functional and determinism is benchmarked at 100.0%, external execution adapters remain mock-only and require rigorous boundary separation.
- **Birkin** implements a local-first fail-closed policy engine, Ed25519 action receipt signing, and a SHA-256 hash-chained audit ledger with 40 passing tests. However, human-in-the-loop (HITL) approval flows require end-to-end operationalization, execution receipts must be strictly distinguished from authorization receipts, and adapter seams must be explicitly clarified against real production agent runtimes.

---

## 2. INFINI Baseline Audit

### 2.1 Implemented vs. Mock Functionality
- **Implemented & Fully Operational:**
  - `Loopfile` YAML specification parser and JSON schema validator (`parse.py`, `schema.json`).
  - Reference execution engine with SQLite-backed state and DAG step progression (`engine.py`, `db.py`).
  - OpenTelemetry GenAI Semantic Conventions exporter (`otel.py`), emitting compliant spans for LLM workflow steps.
  - Cross-engine step divergence diffing (`diff.py`), isolating divergence in step outcomes, status, and tokens.
  - Deterministic time-travel replay engine (`replay.py`).
  - Pure-Python Ed25519 trace signing and offline signature verification CLI (`crypto.py`, `infini verify-trace`).
  - Model Context Protocol (MCP) tool runtime and client (`mcp_client.py`, `mcp_runtime.py`).
- **Mock-Only Adapters:**
  - `LangGraph` adapter (`adapters/langgraph/`, `test_langgraph_adapter.py`): Translates Loopfiles to StateGraph structures and simulates trace emission. Live LangGraph multi-turn execution is not wired.
  - `Hermes`, `OpenClaw`, `Codemap`, `Local`: Syntactic translation and mock trace simulation only.
- **Unimplemented / Stubs:**
  - `CrewAI`, `AutoGen`, `Mastra`, `Goose`, `OpenAI Agents SDK`: Stubs in `adapters/` that fail gracefully with clear "not implemented" notices.

### 2.2 CI Failure Root Cause Analysis
- **Failure:** GitHub Actions run `41975201208` failed on step `Golden examples (examples/golden-research-assistant/research-loop.yaml)`.
- **Root Cause:** Commit `835a0c3` ("Curate examples/ to 4 intentional demos") moved `golden-research-assistant` and `golden-seo-pipeline` into `examples/_deprecated/` without updating the CI matrix in `.github/workflows/infini-ci.yml`.
- **Remediation:** Restored canonical golden examples (`examples/golden-research-assistant` and `examples/golden-seo-pipeline`) to `examples/` and expanded the CI matrix to test all active canonical examples (`quickstart.yaml`, `claim-audit`, `github-pr-review`, `squad-loop`, `mcp-runtime`).

### 2.3 Baseline Test Results
- **Unit & Integration Suite (`pytest cli/tests`):** **56 passed** in 6.37s.
- **Conformance Suite (`infini conformance tests/conformance/ --mock`):** **9 passed, 0 failed** across `browser-loop`, `cost-loop`, `mcp-loop`, `memory-loop`, `parallel-loop`, `research-loop`, `retry-loop`, `simple-loop`, and `verification-loop`.
- **Reproducible Local Benchmark (`make bench`):**
  - Replay Determinism: **100.0%** (100/100 runs byte-identical).
  - Per-Step Latency Overhead: Mean **1.846 ms**, P50 **1.819 ms**, P95 **2.008 ms** (Apple M4 hardware, recorded in `benchmarks/results.json`).

---

## 3. Birkin Baseline Audit

### 3.1 Security Architecture & Policy Plane
- **Implemented & Fully Operational:**
  - Fail-closed policy engine (`policy.py`) evaluating path rules, shell commands, and risk scores.
  - Ed25519 cryptographic signing (`crypto.py`) generating `AuthorizationReceipt` objects.
  - Append-only SHA-256 hash-chained audit ledger (`audit.py`) with Merkle root checkpoints.
  - Six-attack tamper detection matrix (`tests/test_tamper_matrix.py`) detecting signature mutation, identity swap, policy modification, root rewriting, missing events, and reordered events.
  - Offline verification CLI (`birkin verify`).
- **Gaps & Architectural Seams:**
  - **Authorization vs. Execution Receipt Distinction:** An `AuthorizationReceipt` certifies that a tool call *was permitted* under policy; it must not be conflated with evidence that the tool *actually executed* or produced a specific side effect.
  - **Human-in-the-Loop (HITL) Workflow:** `decision=require_approval` is supported by the policy engine, but approval resolution (interactive or asynchronous sign-off with expiration/denial) requires a dedicated, deterministic operational flow.
  - **Hermes Runtime Status:** `birkin.adapters.hermes` is an in-process tool registry demonstration, not a production distributed agent deployment.

### 3.2 Baseline Test Results
- **Unit & Tamper Suite (`pytest tests/`):** **40 passed** in 0.16s.
- **CI Smoke Gate (`bash scripts/ci_smoke.sh`):** **7/7 checks passed** (unit tests, demo package generation, offline verification, prompt injection attack block, privilege escalation block, tamper detection, NullAgent seam).
- **SQLite Hash-Chain Tamper Test (`bash tests/tamper-test.sh`):** **6/6 passed**, correctly catching trigger bypass and table mutation.

---

## 4. Prioritized Engineering Findings

| Priority | Component | Issue | Remediation Plan |
| :--- | :--- | :--- | :--- |
| **P0** | INFINI CI | Golden examples matrix in `.github/workflows/infini-ci.yml` points to missing paths. | Restore canonical examples to `examples/` and test all active workflows in matrix. |
| **P0** | Birkin Architecture | `AuthorizationReceipt` could be misinterpreted as execution confirmation. | Implement distinct `ExecutionReceipt` model explicitly binding action results to prior authorization receipts. |
| **P1** | Birkin HITL | `require_approval` lacks deterministic approval/rejection lifecycle controls. | Implement approval grant/deny CLI and programmatic interface with explicit expirations and cryptographic binding. |
| **P1** | INFINI Runtime | Adapter boundaries need formal contracts to prevent claiming live execution for mock adapters. | Add explicit `EngineCapabilities` enumeration and runtime capability introspection. |
| **P2** | Cross-Repo Seam | No standard interface for INFINI workflows to consume Birkin authorization. | Create a lightweight, decoupled integration specification and verification test. |
| **P2** | Supply Chain & CI | GitHub Actions workflows use mutable tags and lack dependency lockfiles. | Pin action versions and verify reproducible installations. |

---

## 5. Modernization Plan

### Phase 1: INFINI Modernization
1. **Fix CI:** Commit golden example restoration and matrix expansion. Verify green workflow locally and remotely.
2. **Runtime Simplification & Type Safety:** Formalize `EngineCapabilities`, type annotations, and explicit error codes.
3. **Determinism Verification:** Add property-based tests verifying determinism under concurrent step simulations and error handling.
4. **Developer Experience:** Ensure `pip install -e .` and `examples/quickstart.yaml` work with zero credentials and under 60 seconds.

### Phase 2: Birkin Security Modernization
1. **Receipt Semantics:** Add `ExecutionReceipt` to strictly decouple policy authorization from execution verification.
2. **Deterministic HITL Approval Workflow:** Add `birkin approve` and `birkin deny` commands with time-bounded tokens.
3. **Threat-Model-Driven Tests:** Add explicit test cases for path traversal, argument smuggling, and replay attacks.
4. **Decoupled INFINI-Birkin Seam:** Implement a clean adapter contract (`birkin.adapters.infini_adapter` / `infini.governance`) demonstrating pre-action authorization checks.

### Phase 3: Engineering Standards & Documentation
1. Update `README.md` and generate clean vector architecture SVGs for both repositories.
2. Add `IMPLEMENTATION_STATUS.md` in both repositories documenting exact capabilities, tested versions, and deferred items.
3. Verify all test suites and submit reviewable pull requests on dedicated branches.
