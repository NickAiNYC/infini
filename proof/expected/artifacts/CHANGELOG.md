# Changelog

## 1.4.0 (2026-07-01)

### ⚠ BREAKING CHANGES

- **verify**: real filesystem-backed syntactic checks (e1f2a3b)

## Features

- **parser**: support conventional commit scopes (a1b2c3d)
- **registry**: add local install resolution (b2c3d4e)
- **verify**: real filesystem-backed syntactic checks (e1f2a3b)

## Bug Fixes

- **engine**: enforce budget ceiling before step dispatch (c3d4e5f)
- **trace**: stable ordering of verification entries (d4e5f6a)
- **cli**: replay error when step id is absent (e5f6a7b)

## Performance

- **diff**: stream large traces instead of loading whole file (f6a7b8c)

## Refactoring

- **parse**: extract schema loader (c9d0e1f)

## Documentation

- **spec**: clarify VERIFY normative semantics (a7b8c9d)
- **readme**: mark simulated paths explicitly (b8c9d0e)

## Tests

- **conformance**: add failing-case fixtures (f2a3b4c)

## Chores

- **ci**: pin python matrix to 3.10-3.12 (d0e1f2a)
