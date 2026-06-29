"""Canonical loop pattern registry for INFINI.

Each pattern is a real-world loop template that scaffolds a working
Loopfile + supporting files. Patterns lower first-run friction —
`infini init --pattern daily-triage` should produce a loop you can
actually run.

Patterns
--------
1. daily-triage       — triage new issues/PRs every morning
2. pr-babysitter      — monitor an open PR for test failures + reviews
3. ci-sweeper         — sweep CI failures and propose fixes
4. issue-triage       — label + route incoming issues
5. changelog-drafter  — draft changelog entries from merged PRs
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class LoopPattern:
    """A canonical loop pattern — a reusable loop template."""
    name: str
    description: str
    cadence: str
    loopfile_yaml: str
    supporting_files: dict[str, str] = field(default_factory=dict)

    def scaffold(self, target_dir: str | Path) -> list[Path]:
        target_dir = Path(target_dir)
        target_dir.mkdir(parents=True, exist_ok=True)
        created: list[Path] = []
        lf_path = target_dir / "Loopfile.yaml"
        lf_path.write_text(self.loopfile_yaml)
        created.append(lf_path)
        for filename, content in self.supporting_files.items():
            fpath = target_dir / filename
            fpath.parent.mkdir(parents=True, exist_ok=True)
            fpath.write_text(content)
            created.append(fpath)
        return created


_DAILY_TRIAGE = LoopPattern(
    name="daily-triage",
    description="Triage new issues and PRs every morning — label, prioritize, route.",
    cadence="daily (cron: 0 9 * * *)",
    loopfile_yaml="""LOOPFILE: "1.0"
name: daily-triage
version: 1.0.0
description: >
  Daily triage loop: scan new issues and PRs, label them, assign
  priority, and route to the right owner. Runs once per day.

OBJECTIVE: >
  Triage all new issues and PRs from the last 24 hours.

AGENTS:
  - { name: triager, role: researcher, model_tier: sonnet, tools: [github] }
  - { name: labeler, role: builder,   model_tier: haiku,  tools: [github] }
  - { name: verifier, role: verifier, model_tier: haiku,  tools: [github] }

STEPS:
  - { id: s1, name: fetch_new,   action: github.list_new,     uses: triager,  produces: [new-items.json] }
  - { id: s2, name: classify,    action: github.classify,      uses: labeler,  depends_on: [s1], produces: [triaged.json] }
  - { id: s3, name: apply,       action: github.apply_labels,  uses: labeler,  depends_on: [s2], produces: [applied.json] }
  - { id: s4, name: verify,      action: github.verify_labels, uses: verifier, depends_on: [s3], produces: [verify.json] }

VERIFY:
  syntactic:
    - "new-items.json:exists"
    - "triaged.json:exists"
    - "verify.json:valid_json"
  semantic:
    - "judge:triage_accuracy>=85"
  confidence_threshold: 85

BUDGET: { dollars: 2, minutes: 10 }
STOP_WHEN:
  - all_verify_passed
  - iterations>=2
LESSONS: { path: lessons.md, append: true }
STATE:   { path: state/, resume: true }
""",
    supporting_files={
        "STATE.md": "# daily-triage state\n\nLast run: (none)\nItems triaged: 0\n",
        "LOOP.md": "# daily-triage loop config\n\n## Cadence\n- Runs daily at 09:00 UTC\n- Cron: `0 9 * * *`\n\n## Limits\n- Max 50 items per run\n- Max $2 per run\n- Max 10 minutes per run\n\n## Handoff\n- If triage accuracy < 85%, escalate to human\n- If > 50 items, split into batches\n",
        "lessons.md": "# daily-triage lessons\n\n(Accumulates learnings across runs.)\n",
        "AGENTS.md": "# Agent conventions for daily-triage\n\n## Roles\n- **triager**: fetches new items, reads content\n- **labeler**: classifies and applies labels\n- **verifier**: checks labels were applied correctly\n\n## Safety\n- Never close issues or PRs — only label\n- Never modify code — only metadata\n- Human review required for priority:critical\n",
    },
)

_PR_BABYSITTER = LoopPattern(
    name="pr-babysitter",
    description="Monitor an open PR for test failures, review requests, and merge readiness.",
    cadence="on PR open + every 30 min while open",
    loopfile_yaml="""LOOPFILE: "1.0"
name: pr-babysitter
version: 1.0.0
description: >
  PR babysitter loop: monitor an open pull request for CI status,
  review requests, and merge readiness. Alerts on blockers.

OBJECTIVE: >
  Monitor PR for test failures and merge blockers.

AGENTS:
  - { name: watcher,  role: researcher, model_tier: haiku,  tools: [github] }
  - { name: alerter,  role: builder,    model_tier: haiku,  tools: [github, slack] }

STEPS:
  - { id: s1, name: check_ci,    action: github.check_ci,    uses: watcher, produces: [ci-status.json] }
  - { id: s2, name: check_reviews, action: github.check_reviews, uses: watcher, depends_on: [s1], produces: [review-status.json] }
  - { id: s3, name: assess,      action: merge.assess,       uses: watcher, depends_on: [s2], produces: [assessment.json] }
  - { id: s4, name: alert,       action: slack.notify,       uses: alerter, depends_on: [s3], produces: [alert.json], condition: "artifact:exists:assessment.json" }

VERIFY:
  syntactic:
    - "ci-status.json:exists"
    - "review-status.json:exists"
  semantic:
    - "judge:monitoring_completeness>=90"
  confidence_threshold: 90

BUDGET: { dollars: 1, minutes: 5 }
STOP_WHEN:
  - all_verify_passed
  - iterations>=1
LESSONS: { path: lessons.md, append: true }
STATE:   { path: state/, resume: true }
""",
    supporting_files={
        "STATE.md": "# pr-babysitter state\n\nPR: (none)\nChecks: 0\nAlerts: 0\n",
        "LOOP.md": "# pr-babysitter loop config\n\n## Cadence\n- On PR open\n- Every 30 minutes while PR is open\n- On PR close (final summary)\n\n## Limits\n- Max $1 per run\n- Max 5 minutes per run\n\n## Handoff\n- Alert on CI failure\n- Alert on review block\n- Alert on merge conflict\n",
        "lessons.md": "# pr-babysitter lessons\n\n(Accumulates learnings across runs.)\n",
    },
)

_CI_SWEEPER = LoopPattern(
    name="ci-sweeper",
    description="Sweep CI failures, identify root cause, and propose fixes as PRs.",
    cadence="on CI failure",
    loopfile_yaml="""LOOPFILE: "1.0"
name: ci-sweeper
version: 1.0.0
description: >
  CI sweeper loop: when CI fails, analyze the failure, identify root
  cause, propose a fix, and open a pull request with the fix.

OBJECTIVE: >
  Diagnose CI failures and propose fixes as pull requests.

AGENTS:
  - { name: analyst,  role: researcher, model_tier: sonnet, tools: [github, terminal] }
  - { name: fixer,    role: builder,    model_tier: sonnet, tools: [file_system, terminal, github] }
  - { name: verifier, role: verifier,   model_tier: haiku,  tools: [terminal] }

STEPS:
  - { id: s1, name: fetch_failures, action: github.list_failed_runs, uses: analyst,  produces: [failures.json] }
  - { id: s2, name: diagnose,       action: ci.diagnose,             uses: analyst,  depends_on: [s1], produces: [diagnosis.md] }
  - { id: s3, name: fix,            action: file_system.write,       uses: fixer,    depends_on: [s2], produces: [fix.patch] }
  - { id: s4, name: test,           action: terminal.run,            uses: verifier, depends_on: [s3], produces: [test-output.log] }
  - { id: s5, name: open_pr,        action: github.open_pr,          uses: fixer,    depends_on: [s4], produces: [pr-url.txt], condition: "step:s4:status==ok" }

VERIFY:
  syntactic:
    - "failures.json:exists"
    - "diagnosis.md:exists"
    - "test-output.log:exit_zero"
  semantic:
    - "judge:fix_correctness>=85"
  confidence_threshold: 85

BUDGET: { dollars: 5, minutes: 30 }
STOP_WHEN:
  - all_verify_passed
  - iterations>=3
LESSONS: { path: lessons.md, append: true }
STATE:   { path: state/, resume: true }
""",
    supporting_files={
        "STATE.md": "# ci-sweeper state\n\nFailures swept: 0\nPRs opened: 0\n",
        "LOOP.md": "# ci-sweeper loop config\n\n## Cadence\n- On CI failure (GitHub Actions webhook)\n\n## Limits\n- Max 3 failures per run\n- Max $5 per run\n- Max 30 minutes per run\n\n## Handoff\n- If fix_correctness < 85%, do not open PR — escalate to human\n- If test suite fails after fix, do not open PR\n- Always link the original CI failure in the PR description\n",
        "SAFETY.md": "# ci-sweeper safety constraints\n\n## What this loop CAN do\n- Read CI logs\n- Write code fixes\n- Run tests\n- Open pull requests\n\n## What this loop CANNOT do\n- Merge pull requests\n- Push directly to main\n- Modify CI configuration\n- Close issues without human approval\n",
        "lessons.md": "# ci-sweeper lessons\n\n(Accumulates learnings across runs.)\n",
    },
)

_ISSUE_TRIAGE = LoopPattern(
    name="issue-triage",
    description="Label, prioritize, and route incoming issues to the right team.",
    cadence="on issue open + hourly batch",
    loopfile_yaml="""LOOPFILE: "1.0"
name: issue-triage
version: 1.0.0
description: >
  Issue triage loop: when a new issue is opened, classify it (bug,
  feature, question), assign priority, and route to the right team.

OBJECTIVE: >
  Triage new issues: classify, prioritize, and route.

AGENTS:
  - { name: classifier, role: researcher, model_tier: sonnet, tools: [github] }
  - { name: router,     role: builder,    model_tier: haiku,  tools: [github] }
  - { name: verifier,   role: verifier,   model_tier: haiku,  tools: [github] }

STEPS:
  - { id: s1, name: fetch,     action: github.list_new_issues, uses: classifier, produces: [issues.json] }
  - { id: s2, name: classify,  action: issue.classify,          uses: classifier, depends_on: [s1], produces: [classified.json] }
  - { id: s3, name: route,     action: issue.assign,            uses: router,     depends_on: [s2], produces: [routed.json] }
  - { id: s4, name: verify,    action: github.verify_labels,    uses: verifier,   depends_on: [s3], produces: [verify.json] }

VERIFY:
  syntactic:
    - "issues.json:exists"
    - "classified.json:valid_json"
  semantic:
    - "judge:classification_accuracy>=85"
  confidence_threshold: 85

BUDGET: { dollars: 1, minutes: 10 }
STOP_WHEN:
  - all_verify_passed
  - iterations>=2
LESSONS: { path: lessons.md, append: true }
STATE:   { path: state/, resume: true }
""",
    supporting_files={
        "STATE.md": "# issue-triage state\n\nIssues triaged: 0\n",
        "LOOP.md": "# issue-triage loop config\n\n## Cadence\n- On issue open (webhook)\n- Hourly batch for unprocessed issues\n\n## Limits\n- Max 20 issues per run\n- Max $1 per run\n\n## Routing rules\n- bug → engineering team\n- feature → product team\n- question → support team\n- priority:critical → page on-call\n",
        "lessons.md": "# issue-triage lessons\n\n(Accumulates learnings across runs.)\n",
    },
)

_CHANGELOG_DRAFTER = LoopPattern(
    name="changelog-drafter",
    description="Draft changelog entries from merged PRs since the last release.",
    cadence="on release prep (manual / pre-tag)",
    loopfile_yaml="""LOOPFILE: "1.0"
name: changelog-drafter
version: 1.0.0
description: >
  Changelog drafter loop: fetch all PRs merged since the last release,
  categorize them (feature, fix, breaking), and draft a changelog entry.

OBJECTIVE: >
  Draft a changelog from merged PRs since the last release.

AGENTS:
  - { name: fetcher, role: researcher, model_tier: haiku,  tools: [github] }
  - { name: writer,  role: builder,    model_tier: sonnet, tools: [github] }
  - { name: verifier, role: verifier,  model_tier: haiku,  tools: [github] }

STEPS:
  - { id: s1, name: fetch_merges, action: github.list_merges, uses: fetcher,  produces: [merges.json] }
  - { id: s2, name: categorize,   action: changelog.categorize, uses: writer,   depends_on: [s1], produces: [categorized.json] }
  - { id: s3, name: draft,        action: changelog.draft,      uses: writer,   depends_on: [s2], produces: [CHANGELOG-draft.md] }
  - { id: s4, name: verify,       action: changelog.verify,     uses: verifier, depends_on: [s3], produces: [verify.json] }

VERIFY:
  syntactic:
    - "merges.json:exists"
    - "CHANGELOG-draft.md:exists"
    - "CHANGELOG-draft.md:non_empty"
  semantic:
    - "judge:changelog_completeness>=90"
  confidence_threshold: 90

BUDGET: { dollars: 1, minutes: 10 }
STOP_WHEN:
  - all_verify_passed
  - iterations>=1
LESSONS: { path: lessons.md, append: true }
STATE:   { path: state/, resume: true }
""",
    supporting_files={
        "STATE.md": "# changelog-drafter state\n\nLast release: (none)\nEntries drafted: 0\n",
        "LOOP.md": "# changelog-drafter loop config\n\n## Cadence\n- Manual (before a release)\n- Or: on PR merge to release branch\n\n## Limits\n- Max $1 per run\n- Max 10 minutes per run\n\n## Format\n- Keep a Changelog format\n- Categories: Added, Changed, Deprecated, Removed, Fixed, Security\n",
        "lessons.md": "# changelog-drafter lessons\n\n(Accumulates learnings across runs.)\n",
    },
)


_PATTERNS: dict[str, LoopPattern] = {
    p.name: p for p in [
        _DAILY_TRIAGE,
        _PR_BABYSITTER,
        _CI_SWEEPER,
        _ISSUE_TRIAGE,
        _CHANGELOG_DRAFTER,
    ]
}


def get_pattern(name: str) -> LoopPattern | None:
    return _PATTERNS.get(name)


def list_patterns() -> list[LoopPattern]:
    return list(_PATTERNS.values())


def pattern_names() -> list[str]:
    return list(_PATTERNS.keys())
