# Retry Pattern

## Problem

A step occasionally fails for transient reasons: a network timeout, a
rate limit, a flaky test. You don't want the whole loop to fail; you want
to retry the step a few times before giving up.

## Diagram

```text
step → fail → retry → fail → retry → pass → continue
```

## Loopfile

```yaml
STEPS:
  - id: s3
    name: run_tests
    action: terminal.run
    uses: tester
    depends_on: [s2]
    produces: [test-output.log]
    retry: { max: 3, backoff: exponential }
```

## Tradeoffs

**Gives:**
- Resilience to transient failures.
- No need to restart the whole loop when one step flakes.

**Costs:**
- Each retry costs money and time.
- A step that retries 3 times hides a real bug. Retries are for transient
  failures, not for "the prompt is wrong."

## Best practices

- **Use exponential backoff.** Linear backoff hammers a service that's
  already struggling.
- **Cap at 3 retries.** If a step fails 4 times, something is genuinely
  wrong. Escalate, don't retry.
- **Don't retry verification failures.** If `verify` fails, retrying
  `run` without changing anything is just spending money. Either fix the
  step (and retry) or escalate.
- **Log every retry.** The trace should show every attempt, not just the
  final outcome. This is what `infini inspect` is for.
- **Retry the step, not the loop.** Loop-level retries are the next
  iteration; step-level retries are this pattern. They're different.
