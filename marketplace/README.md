# INFINI Marketplace

> **Status: Preview.** The marketplace is a Git-based index of community
> loops, organized by category. No hosted service.

## Categories

| Category | Description |
| --- | --- |
| [Research](research/) | Multi-source research with citations and verification. |
| [Coding](coding/) | Feature implementation, refactoring, debugging, review. |
| [DevOps](devops/) | SRE, oncall, deployment automation, migration. |
| [Security](security/) | Vulnerability research, incident response, postmortem. |
| [Compliance](compliance/) | Audit, policy enforcement, regulatory workflows. |
| [Marketing](marketing/) | Content drafting, campaign analysis, brand voice. |
| [Sales](sales/) | Outreach, prospecting, account research. |
| [Legal](legal/) | Contract review, case research, citation checking. |
| [Healthcare](healthcare/) | Clinical research, claims audit, FDA workflows. |
| [Finance](finance/) | Reconciliation, risk analysis, regulatory reporting. |
| [Infrastructure](infrastructure/) | SRE, oncall, deployment, migration. |
| [Education](education/) | Lesson planning, assessment, personalized tutoring. |

## Submitting a loop

1. Write a Loopfile
2. Validate: `infini validate loop.yaml`
3. Test: `infini run loop.yaml --mock`
4. Create the submission following the [template](#submission-template)
5. PR to `marketplace/<category>/<your-loop>/`

Each submission must include: Loopfile, diagram, benchmark, essay,
verification notes, replay notes, license, tags, difficulty, estimated
runtime, required capabilities.

## Principles

- **Verification over popularity.** A loop with 5 stars and verified ✅
  is featured above a loop with 5000 stars and no verification.
- **No fake numbers.** Download counts are real (when the registry ships).
- **No paid placement.** Featured loops are curated by maintainers.
