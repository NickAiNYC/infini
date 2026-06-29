# Claim Audit

Audit a public website for claim assertions — extract claims, classify them, identify proof gaps, and emit findings.

## Agents

- **extractor**: Extracts verbatim claims from the target page
- **classifier**: Labels each claim by type (supported, unsupported, medical, testimonial, etc.)
- **analyst**: Identifies proof gaps and produces audit summary
- **verifier**: Confirms findings completeness

## Steps

1. Extract all assertions from the target page
2. Classify each claim per the classification standard
3. Identify proof gaps for unsupported claims
4. Produce audit summary
5. Emit prioritized findings

## Usage

```bash
infini run loops/claim-audit/Loopfile.yaml --mock
infini run loops/claim-audit/Loopfile.yaml --mock --engine langgraph
infini diff runs/latest/run.json runs/latest/run.json
```
