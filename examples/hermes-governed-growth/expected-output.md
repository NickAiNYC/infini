# Expected output

A successful run of `claim-audit-loop.yaml` produces:

```
runs/latest/
├── run.json                  # INFINI trace
├── evidence.json             # s1 artifact
├── policy_check.json         # s2 artifact
├── decision.md               # s3 artifact
├── decision.signed.md        # s4 artifact
├── audit/
│   └── log.jsonl             # signed audit trail
└── state/                    # resumable state
```

`run.json` excerpt:

```json
{
  "loopfile": "infini/claim-audit-loop@1.0.0",
  "engine": { "type": "hermes", "adapter": "adapters/hermes" },
  "governance": {
    "policy_violations": [],
    "escalations": [
      { "at_step": "s3", "reason": "confidence_below_threshold", "value": 71 }
    ],
    "audit_hash": "sha256:9f3a…",
    "memory_refs": ["claims/2026-06-12#similar-claim"]
  },
  "outcome": "verified",
  "budget": { "spent_dollars": 2.08, "spent_minutes": 6.92 }
}
```

CI runs `infini ci` against this folder and asserts the trace matches the above shape.
