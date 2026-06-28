# Release Checklist

Use this checklist for every release. Copy it into the release PR description.

---

## Pre-release

- [ ] All CI checks pass on `main`
- [ ] `python -m pytest cli/tests/ -q` passes locally
- [ ] `infini conformance tests/conformance/ --engine infini --mock` passes (8/8)
- [ ] `infini certify adapters/hermes --engine infini --mock` passes
- [ ] `infini certify adapters/openclaw --engine infini --mock` passes
- [ ] `python ci/generate_matrix.py` runs without error
- [ ] `python ci/check_schema_sync.py` passes
- [ ] All corpus cases validate: `for f in tests/corpus/*/Loopfile.yaml; do infini validate "$f"; done`
- [ ] No `runs/` directory committed: `git status --porcelain | grep runs/` returns nothing
- [ ] No `__pycache__/`, `.next/`, `node_modules/` committed

## Version bump

- [ ] `cli/pyproject.toml` version bumped
- [ ] `cli/src/infini/__init__.py` `__version__` matches
- [ ] `CHANGELOG.md` updated with release notes
- [ ] `spec/versions.md` updated if spec version changed

## Tag and push

- [ ] `git tag v0.X.0`
- [ ] `git push origin v0.X.0`
- [ ] Publish workflow triggers (`.github/workflows/publish.yml`)
- [ ] PyPI upload succeeds (for first release: manual `twine upload`)

## Post-release

- [ ] `pip install infini-cli==v0.X.0` works in a fresh venv
- [ ] GitHub Release created with changelog notes
- [ ] Release announced (Discussions, social)
- [ ] Token rotated if any were used during release

## Rollback (if needed)

- [ ] Yank the PyPI version (don't delete)
- [ ] Publish a fix as a new version
- [ ] Update CHANGELOG with the fix
