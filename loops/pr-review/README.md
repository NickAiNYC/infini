# PR Review

Review open pull requests — check CI, analyze changes, and produce structured reviews.

## Agents

- **reviewer**: Fetches PR data and CI status
- **analyst**: Analyzes code changes and writes review
- **verifier**: Confirms review completeness

## Steps

1. Fetch PR metadata and diff
2. Check CI pipeline status
3. Analyze code changes for quality and safety
4. Write structured review comments
5. Verify review covers all changed files

## Usage

```bash
infini run loops/pr-review/Loopfile.yaml --mock
infini run loops/pr-review/Loopfile.yaml --mock --engine langgraph
infini diff runs/latest/run.json runs/latest/run.json
```
