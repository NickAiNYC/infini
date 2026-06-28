# Hidden State

## Smell

The loop modifies state the engine doesn't know about: environment
variables, files outside the declared `produces`, database rows, external
API calls.

## Why it fails

The engine can't replay what it can't see. A step that reads an
environment variable works on the original run; on replay, the variable
is different (or missing), and the step produces different output. The
replay is unfaithful.

Worse, hidden state makes the loop non-portable. A loop that reads
`MY_TEAM_API_KEY` from the env works on your machine; it fails on
someone else's.

## Fix

- **Declare every artifact in `produces`.** If a step writes a file, the
  file is in `produces`. No exceptions.
- **Pass inputs through `depends_on`, not through env.** Step B needs
  step A's output? Step A produces it; step B declares
  `depends_on: [A]`. Don't use env vars as a side channel.
- **Use engine-managed state.** `STATE: { path: state/<loop>/,
  resume: true }` is the engine's state directory. Put loop state there,
  not in arbitrary filesystem locations.
- **Declare external dependencies in `ENGINE.tools`.** If the loop needs
  a database, declare `tools: [db]`. The adapter provides the DB
  connection; the loop doesn't connect directly.
- **Inspect the trace.** `infini inspect` should show every artifact
  the loop touched. If an artifact is missing from the trace, it's
  hidden state. Fix it.
- **Test replay.** If `infini replay runs/latest/ --step s3` produces
  different output than the original run, you have hidden state. Find
  it.
