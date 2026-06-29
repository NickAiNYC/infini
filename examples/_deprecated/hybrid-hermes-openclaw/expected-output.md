# Expected output

A successful run of `governed-coding-loop.yaml` produces:

```
runs/latest/
├── run.json                  # INFINI trace — both governance + tools populated
├── plan.md                   # s1 (Hermes)
├── policy_check.json         # s2 (Hermes)
├── audit/
│   ├── pre.jsonl             # s3 (Hermes, signed)
│   └── post.jsonl            # s7 (Hermes, signed)
├── src/
│   ├── dark-mode.tsx         # s4 (OpenClaw)
│   └── dark-mode.css         # s4 (OpenClaw)
├── test-output.log           # s5 (OpenClaw, exit 0)
├── pr-url.txt                # s6 (OpenClaw)
├── governance-verify.json    # s8 (Hermes)
└── state/                    # resumable across the Hermes/OpenClaw boundary
```

`run.json` excerpt (hybrid trace carries **both** governance and tools):

```json
{
  "loopfile": "infini/governed-coding-loop@1.0.0",
  "engine": {
    "type": "hermes",
    "adapter": "adapters/hermes",
    "delegates": {
      "execution": { "type": "openclaw", "adapter": "adapters/openclaw" }
    }
  },
  "governance": {
    "policy_violations": [],
    "escalations": [],
    "audit_hash": "sha256:b7c1…",
    "memory_refs": ["coding/2026-06-20#similar-feature"]
  },
  "tools": {
    "calls": [
      { "step": "s4", "tool": "file_system.write", "target": "src/dark-mode.tsx", "ok": true },
      { "step": "s4", "tool": "file_system.write", "target": "src/dark-mode.css", "ok": true },
      { "step": "s5", "tool": "terminal.run",      "target": "pytest -q",         "ok": true, "exit": 0 },
      { "step": "s6", "tool": "github.open_pr",    "target": "feature/dark-mode", "ok": true, "pr": 4130 }
    ],
    "denied": []
  },
  "outcome": "verified",
  "budget": { "spent_dollars": 1.70, "spent_minutes": 4.35 }
}
```

CI runs `infini ci` against this folder and asserts the trace matches the above shape — including that **both** `governance.audit_hash` and `tools.calls` are present. A hybrid run that lacks either is a CI failure.
