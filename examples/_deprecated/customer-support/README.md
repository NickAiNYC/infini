# Customer Support Agent — Golden Example

> Triage → Research → Respond → Verify. Multi-step with escalation.

## What this demonstrates

- **Sequential pipeline** with 4 steps
- **Escalation policy** (low confidence → human review)
- **Memory recall** (checks past tickets before responding)
- **Quality verification** (response must pass tone + accuracy checks)

## Run it

```bash
infini validate examples/customer-support/Loopfile.yaml
infini run examples/customer-support/Loopfile.yaml --mock
infini inspect runs/latest/
```

## Loop flow

```
recall_past → research_issue → draft_response → verify_quality
                                                    ↓
                                            verified or escalate
```
