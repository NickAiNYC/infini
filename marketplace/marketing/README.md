# Marketplace — Marketing

> **Status: Preview.** No loops published yet — the public registry is
> not yet live. This page shows the category structure.

Content drafting, campaign analysis, brand voice.

## Submission template

Each loop submission should include:

```
marketplace/marketing/<loop-name>/
├── Loopfile.yaml          ← the loop
├── diagram.svg            ← visual flow
├── benchmark.md           ← performance numbers
├── essay.md               ← why this loop exists
├── verification.md        ← verify block explanation
├── replay.md              ← replay notes
├── LICENSE                ← license
├── metadata.json          ← tags, difficulty, runtime, capabilities
└── README.md              ← overview
```

### metadata.json

```json
{
  "name": "<loop-name>",
  "category": "marketing",
  "tags": ["marketing"],
  "difficulty": "intermediate",
  "estimated_runtime": "5m",
  "estimated_cost": "$2.50",
  "required_capabilities": ["parse_loopfile", "run_loop", "verify"],
  "license": "MIT",
  "author": "{github-username}"
}
```

## Featured loops

_None yet. Once the registry is live, this section will list 0–3
curated loops with a verification badge._

## New loops

_None yet._

---

← [Back to marketplace](../README.md)
