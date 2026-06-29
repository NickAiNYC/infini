# Loop Registry

A public catalog of reusable, portable Loopfiles.

Browse, copy, fork, improve, and run.

## Categories

- [Coding](coding/) — code review, PR babysitting, changelog drafting
- [Research](research/) — literature reviews, competitor analysis, deep dives
- [DevOps](devops/) — CI repair, deployment verification, incident triage
- [Security](security/) — vulnerability scanning, compliance checks
- [Marketing](marketing/) — social media drafting, SEO analysis
- [Sales](sales/) — lead enrichment, outreach sequencing
- [Support](support/) — ticket triage, routing, auto-reply drafting
- [Legal](legal/) — contract review, policy drafting
- [Finance](finance/) — reconciliation, report generation
- [Healthcare](healthcare/) — clinical note drafting, audit preparation
- [Education](education/) — lesson planning, quiz generation
- [Infrastructure](infrastructure/) — config validation, drift detection

## How to contribute

1. Write a Loopfile that solves a real problem
2. Run `infini run Loopfile.yaml --mock` to verify it parses
3. Run `infini conformance tests/conformance/ --mock` to certify behavior
4. Open a PR adding it to `seed/` or creating a new category

Anyone can submit. No approval gate — just a working Loopfile with a one-line description.

## How to use

```bash
# Browse available loops
ls loops/

# Run one directly
infini run loops/coding/loop.yaml --mock
```

Full registry with versioning, search, and install: `infini registry list` / `infini registry install @infini/hello-world`
