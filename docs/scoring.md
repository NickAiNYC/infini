# INFINI Scoring Methodology

This document rigorously defines every score and metric printed by the INFINI CLI.

---

## 1. Project Readiness Audit Score (`infini audit`)

The `infini audit` command inspects a target project directory for production-grade loop infrastructure signals. It produces a deterministic 0–100 Readiness Score.

### Mathematical Formula

$$\text{Readiness Score} = \sum_{i=1}^{N} \text{Points}(\text{signal}_i)$$

Where $N = 12$ infrastructure signals, totaling a maximum of 100 points:

| Signal ID | Weight | Description | Checked Criteria |
| :--- | :---: | :--- | :--- |
| `loopfile` | 15 pts | Loopfile presence | `Loopfile.yaml` or `Loopfile.yml` exists |
| `state` | 10 pts | State persistence | `STATE.md` or `state/` directory exists |
| `verifier` | 12 pts | Maker/checker separation | Verifier agent declared in agents list |
| `safety` | 8 pts | Safety documentation | `SAFETY.md` exists |
| `mcp_config` | 10 pts | MCP configuration | `.mcp.json` or `mcp.yaml` exists |
| `budget` | 7 pts | Budget limits | `loop-budget.md` or budget block defined |
| `loop_config` | 8 pts | Loop configuration | `LOOP.md` or `.loop.yml` exists |
| `conventions` | 8 pts | Agent conventions | `AGENTS.md` or `CLAUDE.md` exists |
| `ci` | 10 pts | CI automation | `.github/workflows/` with workflow YAML |
| `activity` | 8 pts | Proven activity | Recent git commits or runs within 7 days |
| `lessons` | 2 pts | Memory / lessons | `lessons.md` or `memory/lessons.md` exists |
| `replay_trace` | 2 pts | Replay trace | `runs/*/run.json` trace available |

### Maturity Levels

- **L0 Draft (0–24 pts):** Aspirational. No reproducible infrastructure.
- **L1 Report-only (25–49 pts):** Workflows execute, but state and artifacts are ephemeral.
- **L2 Assisted (50–74 pts):** Durable state, verified outputs, time-travel replay available.
- **L3 Unattended (75–100 pts):** Automated CI triggers, rigorous verification, budget safety caps.

---

## 2. Adapter Compatibility Score (`infini certify`)

The `infini certify <adapter_path>` command evaluates an external engine adapter against the INFINI specification and conformance test suite.

### Mathematical Formula

$$\text{Compatibility (\%)} = \text{CapScore} + \text{ConfScore}$$

Where:
- **Capability Score (50% max):**
  $$\text{CapScore} = \left(\frac{\text{Count of Supported Capabilities}}{12}\right) \times 50$$
  The 12 canonical capabilities are:
  `parse_loopfile`, `run_loop`, `verify`, `inspect_trace`, `replay`, `diff`, `plan`, `live`, `mcp`, `memory`, `governance`, `skills`.
- **Conformance Pass Rate (50% max):**
  $$\text{ConfScore} = \left(\frac{\text{Passed Conformance Tests}}{\text{Total Conformance Tests}}\right) \times 50$$
  Evaluated across the 8 standard conformance test suites in `tests/conformance/`.

### Derivation of Existing Adapter Scores

- **Hermes Adapter:**
  - Supported capabilities: 5 of 12 (`parse_loopfile`, `run_loop`, `verify`, `inspect_trace`, `replay`) $\rightarrow (5 / 12) \times 50 = 20.833\%$
  - Conformance suite: 8 of 8 passed $\rightarrow (8 / 8) \times 50 = 50.000\%$
  - **Total: $20.833\% + 50.000\% = 70.8\%$** (rounded to 1 decimal place).

- **OpenClaw Adapter:**
  - Supported capabilities: 4 of 12 (`parse_loopfile`, `run_loop`, `verify`, `inspect_trace`) $\rightarrow (4 / 12) \times 50 = 16.667\%$
  - Conformance suite: 8 of 8 passed $\rightarrow (8 / 8) \times 50 = 50.000\%$
  - **Total: $16.667\% + 50.000\% = 66.7\%$** (rounded to 1 decimal place).

