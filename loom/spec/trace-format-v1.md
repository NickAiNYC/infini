# Trace Format v1

> Every `loom run` produces a `trace.jsonl` in `runs/{timestamp}/`.

The trace is the source of truth for `loom inspect` and `loom replay`. It is engine-agnostic — any engine that emits this format works with the inspector.

---

## File

- Path: `runs/run_{YYYYMMDDTHHMMSSZ}/trace.jsonl`
- Format: JSON Lines (one JSON object per line, UTF-8)
- Append-only during a run

---

## Event Schema

```jsonc
{
  "ts": "2026-06-28T12:34:56.789Z",   // ISO-8601 UTC, required
  "kind": "step_start",                // event kind, required
  "step": "s2",                        // step id (empty for loop-level events)
  "msg": "implement feature",          // human-readable message
  "agent": "coder",                    // agent name, optional
  "model": "sonnet",                   // model used, optional
  "tokens": 1234,                      // tokens consumed by this event
  "cost_usd": 0.0234,                  // cost in USD
  "state": { ... },                    // loop state snapshot at this event
  "metadata": { ... }                  // engine-specific extras
}
```

---

## Event Kinds

| kind | when |
|------|------|
| `loop_start` | first event of a run |
| `step_start` | before a step executes |
| `step_end` | after a step completes (success or failure) |
| `step_retry` | when a step retries per its retry policy |
| `verify_start` | before verification runs |
| `verify_result` | per-tier verification result |
| `escalate` | when an escalation condition triggers |
| `budget_check` | periodic budget snapshot |
| `loop_end` | final event of a run |
| `loop_fail` | when the loop exits with failure |

---

## Why JSONL

- Append-only: safe under crash
- Streamable: inspector can render as events arrive
- Greppable: `jq`, `rg`, plain text tools all work
- Engine-agnostic: any runtime can emit

---

## Consume

```bash
# Quick stats
loom inspect runs/run_20260628T123456Z/

# Time-travel
loom replay runs/run_20260628T123456Z/

# Custom analysis
jq -c 'select(.kind=="verify_result")' runs/run_*/trace.jsonl
```
