# State Format v1

> Resumable loops require durable state. This is the contract.

---

## File

- Default path: `state/loop_state.json`
- Format: JSON, UTF-8
- Atomically rewritten after every step (write to `.tmp`, rename)

---

## Schema

```jsonc
{
  "loop": {
    "name": "coding-loop",
    "version": "1.0.0",
    "spec": "1.0"
  },
  "objective": "Add dark mode toggle, preserve tests",
  "status": "running",                    // running | paused | done | failed | escalated
  "started_at": "2026-06-28T12:34:56Z",
  "updated_at": "2026-06-28T12:38:21Z",
  "current_step": "s3",
  "completed_steps": ["s1", "s2"],
  "pending_steps": ["s3", "s4", "s5"],
  "blocked_on": null,                     // step id or null
  "artifacts": {
    "s1": ["plan.md"],
    "s2": ["src_diff.patch"]
  },
  "budget": {
    "dollars": { "used": 1.23, "limit": 5.00 },
    "tokens":  { "used": 123456, "limit": 500000 },
    "minutes": { "used": 3.5,   "limit": 15 }
  },
  "verify_results": {
    "s4": { "syntactic": "pass", "semantic": "pass", "external": "pass", "score": 92 }
  },
  "failures": [
    { "step": "s2", "ts": "...", "reason": "...", "retry": 1 }
  ],
  "escalations": [],
  "confidence": 0.86,
  "next_action": "run s3 (run_test_suite)",
  "lessons_appended": true
}
```

---

## Resume Strategy

The `resume_strategy` field in the Loopfile determines what happens on restart:

| strategy | behavior |
|----------|----------|
| `continue` | Pick up from `current_step`. Reuse completed artifacts. |
| `restart` | Wipe state, run from scratch. |
| `ask` | Pause and ask the user. |

---

## Atomicity

Engines MUST write state atomically:

```python
import os, json, tempfile
def save_state(state, path):
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(path))
    with os.fdopen(fd, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, path)
```

A torn write must not corrupt state.

---

## Versioning

State files include the loop `version` they were written by. If a Loopfile's version changes, the engine refuses to resume and emits a `loop_fail` event with reason `version_mismatch`.
