# Test Plan

## What we test

### Spec compliance (`loom validate`)
- YAML parses
- All required fields present
- VERIFY has ≥2 tiers
- BUDGET has ≥1 ceiling
- STOP_WHEN non-empty
- STEPS reference valid agents
- depends_on has no cycles

### CLI behavior
- `loom validate` returns 0 on valid Loopfile, 1 on invalid
- `loom inspect` renders a trace correctly
- `loom replay` accepts navigation commands
- `loom diff` classifies changes by severity
- `loom ci` compares fixtures to expected
- `loom engines` lists registered engines

### Loop fixtures
Every canonical loop in `loops/` ships with 3 fixtures in `tests/fixtures/{loop-name}/` and 3 expected outputs in `tests/expected/{loop-name}/`. CI runs `loom ci` against each.

## How to run

```bash
# Validate every loop
for f in loops/*.yaml; do loom validate "$f"; done

# Run fixture tests
pytest tests/

# Or via the CLI
loom ci --loopfile loops/coding-loop.yaml \
        --fixtures tests/fixtures/coding-loop \
        --expect    tests/expected/coding-loop
```

## Adding tests

1. Add a fixture to `tests/fixtures/{loop-name}/{case}.json`
2. Add expected output to `tests/expected/{loop-name}/{case}.json`
3. Open a PR. CI runs it.
