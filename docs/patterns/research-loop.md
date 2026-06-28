# Research Loop Pattern

## Problem

You need to answer a question with citations. Single-source answers are
unreliable; uncited answers are hallucinations. The loop must find
multiple sources, extract claims, verify citations, and synthesize.

## Diagram

```text
find_sources → extract_claims → verify_citations → write_brief → [VERIFY]
```

## Loopfile

```yaml
LOOPFILE: "1.0"
name: research-loop
version: 1.0.0

OBJECTIVE: >
  Answer a research question using at least three primary sources, with
  every claim cited and citations verified.

AGENTS:
  - { name: researcher, role: researcher, model_tier: sonnet, tools: [browser, file_system] }
  - { name: verifier,   role: verifier,   model_tier: sonnet, tools: [browser] }

STEPS:
  - { id: s1, name: find_sources,   action: browser.find_sources,    uses: researcher, produces: [sources.json] }
  - { id: s2, name: extract_claims, action: browser.extract_claims,  uses: researcher, depends_on: [s1], produces: [claims.json] }
  - { id: s3, name: verify_cites,   action: browser.verify_citations, uses: verifier,   depends_on: [s2], produces: [citation-check.json] }
  - { id: s4, name: write_brief,    action: file_system.write,        uses: researcher, depends_on: [s3], produces: [research_brief.md] }

VERIFY:
  syntactic:
    - "sources.json:valid_json"
    - "claims.json:valid_json"
    - "research_brief.md:every_claim_has_citation"
  semantic:
    - "judge:source_quality>=85"
    - "judge:answer_quality>=85"
  confidence_threshold: 85

BUDGET: { dollars: 6, minutes: 20 }
STOP_WHEN: [all_verify_passed, iterations>=3]
```

## Tradeoffs

**Gives:**
- Answers with traceable provenance.
- Built-in defense against hallucination (the citation check).

**Costs:**
- Browser tool calls are slow and expensive.
- The loop will fail verification if sources are paywalled or
  inaccessible. This is correct behavior, not a bug.

## Best practices

- **The citation check is non-negotiable.** `every_claim_has_citation` is
  the hard floor. Without it, you have an opinion generator.
- **Use multiple source types.** News articles, papers, primary
  documents, official statistics. A loop that only cites blog posts is
  not research.
- **Verify the citation actually supports the claim.** The
  `verify_citations` step is for this. A claim with a citation that
  doesn't support it is worse than an uncited claim.
- **Cap the source count.** Three good sources beats thirty mediocre
  ones. Set `max_sources: 5` in the find_sources action.
- **Don't trust the model's confidence.** Models are confident about
  hallucinations. Use the `judge:source_quality` check, not the model's
  self-reported confidence.
