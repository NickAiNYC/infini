# Minimal Adapter

The smallest possible INFINI adapter. Implements `PARSE` only — enough
to register with the CLI and validate Loopfiles, but not enough to run
them. Use this as your starting point.

> Copy this directory, rename it, implement `RUN`, then `VERIFY`, then
> `INSPECT`, then `REPLAY`. Run `infini certify` after each.

---

## Files

- [`adapter.yaml`](adapter.yaml) — the manifest
- [`__init__.py`](__init__.py) — the adapter module (~50 lines)
- [`README.md`](README.md) — this file

---

## How to use

1. Copy this directory to `adapters/<your-name>/`
2. Edit `adapter.yaml`: change `name`, `type`, `description`
3. Edit `__init__.py`: implement `RUN` (and later `VERIFY`, `INSPECT`, `REPLAY`)
4. Test: `infini validate examples/golden-research-assistant/research-loop.yaml`
5. Certify: `infini certify adapters/<your-name> --mock`
6. PR to `adapters/`

---

## What to implement next

```python
# In __init__.py, uncomment and implement these:

# @Capability.RUN
# def run(self, loopfile: Loopfile, state: State) -> State:
#     """Execute the STEPS DAG. Return the final state."""
#     # Your runtime's execution logic here
#     pass

# @Capability.VERIFY
# def verify(self, loopfile: Loopfile, state: State) -> VerifyResult:
#     """Run syntactic + semantic checks."""
#     pass

# @Capability.INSPECT
# def inspect(self, run_dir: Path) -> Trace:
#     """Load a run's trace."""
#     pass
```

Each capability you implement flips a `false` to `true` in your
`adapter.yaml` and moves you up the certification ladder.

See the [Adapter Interface Reference](../adapter-interface.md) for the
full contract.
