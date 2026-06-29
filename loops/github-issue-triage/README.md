# GitHub Issue Triage

Classify, label, and route incoming GitHub issues.

## Agents

- **triager**: Fetches new issues, reads content
- **labeler**: Classifies and applies labels
- **verifier**: Confirms labels are correct

## Steps

1. Fetch new issues from the repository
2. Classify each issue (bug, feature, question, etc.)
3. Apply labels and assign priority
4. Verify label accuracy

## Usage

```bash
infini run loops/github-issue-triage/Loopfile.yaml --mock
infini run loops/github-issue-triage/Loopfile.yaml --mock --engine langgraph
infini diff runs/latest/run.json runs/latest/run.json
```
