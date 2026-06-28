# Registry Metadata Schema

The fields every Loopfile exposes in the registry, and the Loop Quality
Score computed from them.

> See [RFC-0005](../spec/rfcs/RFC-0005-registry.md) for the registry
> protocol and [RFC-0006](../spec/rfcs/RFC-0006-marketplace.md) for the
> marketplace that consumes this metadata.

---

## Loop Quality Score

Every Loopfile in the registry receives a quality score from 0 to 100,
computed from eight sub-scores. The score is computed by `infini ci`
against the loop's published fixtures; it is not a publisher claim.

| Sub-score | Weight | What it measures |
| --- | :---: | --- |
| Readability | 10% | Is the Loopfile easy to read? (lines per step, comment density, objective clarity) |
| Reusability | 15% | Can the loop be reused across inputs? (parameterization, no hardcoded paths) |
| Verification | 20% | Does the loop have a meaningful `VERIFY` block? (syntactic + semantic, non-trivial threshold) |
| Portability | 15% | Does the loop run on multiple engines? (uses only spec-defined features) |
| Determinism | 10% | Is the loop's behavior reproducible? (no hidden state, no env dependencies) |
| Estimated cost | 10% | Is the loop's cost reasonable for its task? (benchmark against category baseline) |
| Failure recovery | 10% | Does the loop handle failures well? (retry policy, budget guard, escalation) |
| Documentation | 10% | Is the loop documented? (essay, verification.md, benchmark.md, replay.md) |

The final score is the weighted mean, rounded to the nearest integer.

### Score tiers

| Tier | Score | Meaning |
| --- | --- | --- |
| ★★★★★ | 90–100 | Production-ready. Verified, portable, documented, benchmarked. |
| ★★★★ | 75–89 | Solid. Production-ready with caveats. |
| ★★★ | 60–74 | Usable. Development or low-stakes production. |
| ★★ | 40–59 | Draft. Not production-ready. |
| ★ | 0–39 | Stub. Not runnable. |

The marketplace surfaces the tier as a star rating. The sub-scores are
visible on the loop's detail page.

---

## Registry metadata fields

Every Loopfile in the registry exposes:

| Field | Type | Source | Description |
| --- | --- | --- | --- |
| `name` | string | Loopfile | Slug identifier. |
| `version` | semver | Loopfile | Loopfile version. |
| `description` | string | Loopfile | One-line description. |
| `ns` | string | Registry | Publisher namespace. |
| `publisher` | string | Registry | Publisher identity (verified via signature). |
| `published_at` | datetime | Registry | When this version was published. |
| `content_hash` | sha256 | Registry | Content-addressed hash. |
| `signature` | ed25519 | Registry | Publisher's signature. |
| `category` | enum | Loopfile tags | Marketplace category. |
| `tags` | list[string] | Loopfile tags | Free-form tags. |
| `difficulty` | enum | Computed | `beginner` \| `intermediate` \| `advanced` |
| `estimated_runtime` | duration | Benchmark | Mean runtime from benchmark. |
| `estimated_cost` | dollars | Benchmark | Mean cost from benchmark. |
| `required_tools` | list[string] | Loopfile | Tools the loop needs. |
| `supported_engines` | list[string] | Compatibility matrix | Engines the loop has been tested against. |
| `maintainer` | string | Registry | Current maintainer (may differ from publisher). |
| `license` | enum | Loopfile | `MIT` \| `Apache-2.0` \| `CC-BY-4.0` \| ... |
| `verification_score` | int (0–100) | Computed | Loop Quality Score. |
| `verification_tier` | enum | Computed | `★★★★★` \| `★★★★` \| ... |
| `downloads` | int | Registry | Real download count. |
| `compatibility` | map | Compatibility matrix | Per-engine conformance. |
| `spec_version` | string | Loopfile | `LOOPFILE-1.0` |
| `repository` | url | Loopfile | Source repo (if open-source). |
| `homepage` | url | Loopfile | Loop homepage (if different from repo). |

---

## Computing the score

```bash
infini score loops/coding-loop/Loopfile.yaml
```

This:

1. Validates the Loopfile against [`spec/schema.json`](../spec/schema.json).
2. Runs the loop against its fixtures (if any).
3. Computes each sub-score.
4. Computes the weighted mean.
5. Outputs the tier and a per-sub-score breakdown.

The output is JSON, suitable for CI:

```json
{
  "loopfile": "infini/coding-loop@1.0.0",
  "quality_score": 87,
  "tier": "★★★★",
  "subscores": {
    "readability":        90,
    "reusability":        85,
    "verification":       95,
    "portability":        80,
    "determinism":        85,
    "estimated_cost":     82,
    "failure_recovery":   88,
    "documentation":      90
  }
}
```

---

## Difficulty

Difficulty is computed from:

- Number of steps (more = harder).
- Number of agents (more = harder).
- Whether the loop uses composition (`delegates`).
- Whether the loop uses advanced patterns (parallel workers, fan-out).
- Whether the loop requires governance.

| Difficulty | Criteria |
| --- | --- |
| `beginner` | ≤ 4 steps, 1–2 agents, no composition, no advanced patterns. |
| `intermediate` | 5–8 steps, 2–3 agents, may use composition or one advanced pattern. |
| `advanced` | 9+ steps, 3+ agents, or uses multiple advanced patterns. |

Difficulty is informational. It does not affect the quality score.

---

## What the score is not

- **Not a ranking.** Two loops with the same score are not "equal"; they
  may have different sub-score distributions.
- **Not a guarantee.** A 90+ loop can still fail in production. The score
  measures loop quality, not loop correctness for your specific task.
- **Not static.** The score is recomputed when:
  - The loop's Loopfile changes.
  - The loop's fixtures change.
  - The benchmark reruns (cost and runtime subscores can drift).
  - The compatibility matrix updates (portability subscore can change).

---

## License

CC-BY-4.0. See [repository LICENSE](../LICENSE).
