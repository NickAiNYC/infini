# Expected output

A successful run of `coding-loop.yaml` produces:

```
runs/latest/
├── run.json                  # INFINI trace
├── plan.md                   # s1 artifact
├── src/
│   ├── dark-mode.tsx         # s2 artifact
│   └── dark-mode.css         # s2 artifact
├── test-output.log           # s3 artifact (exit 0)
├── pr-url.txt                # s4 artifact
└── state/                    # resumable state
```

`run.json` excerpt:

```json
{
  "loopfile": "infini/coding-loop@1.0.0",
  "engine": { "type": "openclaw", "adapter": "adapters/openclaw" },
  "tools": {
    "calls": [
      { "step": "s2", "tool": "file_system.write", "target": "src/dark-mode.tsx", "ok": true },
      { "step": "s2", "tool": "file_system.write", "target": "src/dark-mode.css", "ok": true },
      { "step": "s3", "tool": "terminal.run",      "target": "pytest -q",         "ok": true, "exit": 0 },
      { "step": "s4", "tool": "github.open_pr",    "target": "feature/dark-mode", "ok": true, "pr": 4129 }
    ],
    "denied": []
  },
  "outcome": "verified",
  "budget": { "spent_dollars": 0.95, "spent_minutes": 3.30 }
}
```

CI runs `infini ci` against this folder and asserts the trace matches the above shape.
