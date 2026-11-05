# Expected output — golden-seo-pipeline

A successful run produces:

```
runs/latest/
├── run.json                  # INFINI trace (open in Observatory)
├── keywords.json             # s1: keyword research
├── draft.md                  # s2: initial draft
├── critique.md               # s3: critic's feedback
├── revised.md                # s4: revised draft
├── article.md                # s5: SEO-optimized article
├── meta-description.txt      # s5: meta description
├── seo-check.json            # s6: SEO verification results
└── state/                    # resumable state
```

The trace's `outcome` is `verified`. All syntactic checks pass (word
count, keyword density, meta description exists). All semantic checks
pass with confidence ≥ 85. The mean confidence is typically 87–91.

Open in the Observatory:

```bash
infini ui runs/latest/run.json
```

The 3D graph shows 6 nodes (s1 → s2 → s3 → s4 → s5 → s6) in a curved
arc, each colored cyan (passed). Click any node to see its cost,
tokens, and artifacts.
