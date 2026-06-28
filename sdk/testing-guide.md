# Testing Guide

How to test your adapter before submitting for certification.

> A tested adapter is a trustworthy adapter. The conformance suite is
> the floor; your own tests are the ceiling.

---

## 1. Validate your manifest

```bash
infini engines
```

Your adapter should appear with its declared capabilities. If it doesn't
appear, your `adapter.yaml` is malformed or in the wrong location.

---

## 2. Run the conformance suite

```bash
infini conformance tests/conformance/ --engine infini --mock
```

This runs all 8 conformance cases. Your adapter should be able to parse
every Loopfile (the `parse_loopfile` capability). If any fail to parse,
fix your parser before anything else.

---

## 3. Test PARSE against the corpus

The canonical corpus has 10 cases with varied structures:

```bash
for f in tests/corpus/*/Loopfile.yaml; do
    infini validate "$f" || echo "FAIL: $f"
done
```

All 10 should pass. If any fail, your schema validation is too strict
or too lenient.

---

## 4. Test RUN with a simple loop

Once you implement `RUN`, test against the simplest corpus case:

```bash
infini run tests/corpus/001-simple-task/Loopfile.yaml --engine my-adapter
```

The loop should execute and produce a trace. If it fails, check:

- Does your engine resolve `model_tier` correctly?
- Does your engine honor `BUDGET`?
- Does your engine execute `STEPS` in `depends_on` order?

---

## 5. Test VERIFY

Once you implement `VERIFY`, test against a verification-heavy case:

```bash
infini run tests/corpus/002-research-summary/Loopfile.yaml --engine my-adapter
```

The trace should show verification results with confidence scores. If
confidence is always 100, your verifier is a rubber stamp — fix it.

---

## 6. Test INSPECT

```bash
infini inspect runs/latest/
```

The trace should load and render. If it doesn't, your `run.json` doesn't
match the spec's trace format (see [spec §10](../spec/loopfile-v1.md)).

---

## 7. Test REPLAY

```bash
infini replay runs/latest/ --step s2
```

The replay should restore state at step `s2` and resume. If the replay
produces different output, your state persistence is broken.

---

## 8. Write your own tests

Add tests in `adapters/<your-name>/tests/`:

- `test_parse.py` — every corpus case parses
- `test_run.py` — simple loop executes and produces artifacts
- `test_verify.py` — verifier fails on bad output, passes on good
- `test_replay.py` — replay reproduces the original run

Run them with pytest:

```bash
cd adapters/<your-name>
python -m pytest tests/ -q
```

---

## 9. Check for common pitfalls

| Pitfall | How to check |
| --- | --- |
| Hardcoded model names | grep your code for `gpt-4`, `claude-3` — should use `model_tier` |
| Hidden state | Run twice with same input — should produce same output |
| Budget not enforced | Set a $0.01 budget — loop should abort |
| Verifier always passes | Run a deliberately bad Loopfile — verifier should fail |
| Trace missing fields | `infini inspect` should show all fields |

---

## Next steps

- [Certification Guide](certification-guide.md) — get the certified badge
- [Publishing Guide](publishing-guide.md) — share your adapter
- [Adapter Interface Reference](adapter-interface.md) — the full contract
