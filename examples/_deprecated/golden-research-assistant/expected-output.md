# Expected output — golden-research-assistant

A successful run produces:

```
runs/latest/
├── run.json                  # INFINI trace (open in Observatory)
├── sources.json              # s1: at least 3 primary sources
├── claims.json               # s2: extracted claims with citations
├── citation-check.json       # s3: every citation verified
├── research_brief.md         # s4: the final brief
└── state/                    # resumable state
```

The trace's `outcome` is `verified`. All syntactic checks pass. All
semantic checks pass with confidence ≥ 85. The mean confidence is
typically 88–92.

Open in the Observatory:

```bash
infini ui runs/latest/run.json
```

The 3D graph shows 4 nodes (s1 → s2 → s3 → s4) in a curved arc, each
colored cyan (passed). Click any node to see its cost, tokens, and
artifacts.
