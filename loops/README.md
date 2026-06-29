# Loop Registry

A public catalog of reusable, portable Loopfiles.

Browse, copy, fork, improve, and run.

## Golden loops

| Loop | Description | Agents | Steps |
|------|-------------|--------|-------|
| [GitHub Issue Triage](github-issue-triage/) | Classify, label, and route incoming issues | 3 | 4 |
| [PR Review](pr-review/) | Review open PRs — CI check, code analysis, structured review | 3 | 5 |
| [Claim Audit](claim-audit/) | Audit website claims — extract, classify, identify gaps | 4 | 5 |
| [Scrutexity Claim Audit](scrutexity-claim-audit/) | Med-spa claim audit (internal workflow) | 4 | 5 |

## How to use

```bash
# Run any golden loop on the reference engine
infini run loops/github-issue-triage/Loopfile.yaml --mock

# Run the same loop on LangGraph
infini run loops/github-issue-triage/Loopfile.yaml --mock --engine langgraph

# Compare traces across engines
infini diff runs/latest/run.json runs/latest/run.json
```

## How to contribute

1. Write a Loopfile that solves a real problem
2. Run `infini run Loopfile.yaml --mock` to verify it parses
3. Run `infini conformance tests/conformance/ --mock` to certify behavior
4. Open a PR adding it to `loops/`

Anyone can submit. No approval gate — just a working Loopfile with a one-line description.

Full registry with versioning, search, and install: `infini registry list` / `infini registry install @infini/hello-world`
