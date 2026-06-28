# Verification Rubric

The default rubric used by the verifier agent. Loops may override.

## Dimensions

| dimension | weight | question |
|-----------|--------|----------|
| goal_alignment | 30 | Does the output satisfy the original objective? |
| completeness | 20 | Are all required parts present? |
| reliability | 20 | Can the loop recover from failure and resume safely? |
| cost_efficiency | 10 | Does the loop avoid unnecessary expensive operations? |
| artifact_quality | 10 | Are outputs durable, structured, reusable? |
| safety | 10 | Are risks, guardrails, escalation paths defined? |

## Scoring

| score | meaning |
|-------|---------|
| 90-100 | production_ready |
| 80-89 | strong_but_needs_minor_revision |
| 70-79 | usable_but_risky |
| <70 | refine_required |

## How the judge uses this

The verifier agent receives:
- the original objective
- the artifacts produced
- this rubric

It returns a JSON object:

```json
{
  "goal_alignment": 92,
  "completeness": 88,
  "reliability": 95,
  "cost_efficiency": 90,
  "artifact_quality": 87,
  "safety": 93,
  "weighted_total": 91.0,
  "verdict": "production_ready",
  "weak_dimensions": ["artifact_quality"],
  "notes": "..."
}
```

The loop's `confidence_threshold` (in `VERIFY:`) is compared against `weighted_total`. If below, the loop either refines or escalates per its `ESCALATE_WHEN` policy.
