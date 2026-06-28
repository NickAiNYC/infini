# Release Process

How to cut a new release of `infini-cli` and publish it to PyPI.

---

## Prerequisites (one-time setup)

1. **Revoke any exposed GitHub tokens** at
   https://github.com/settings/personal-access-tokens before publishing
   anything. Do not publish with a token that has been in chat logs or
   shared documents.

2. **Create a PyPI account** at https://pypi.org/account/register/.
   Enable 2FA. PyPI accounts get hijacked constantly; do not skip this.

3. **Generate a PyPI API token** at
   https://pypi.org/manage/account/token/. For the first publish, scope
   it to "Entire account". After `infini-cli` exists, you can create a
   new token scoped to just that project.

4. **Add the token as a GitHub secret:**
   - Repository → Settings → Secrets and variables → Actions
   - New repository secret
   - Name: `PYPI_API_TOKEN`
   - Value: the `pypi-...` token

---

## Cutting a release

Follow this exact order. Do not skip steps.

### 1. Revoke exposed tokens

If any GitHub PAT has been pasted in chat, shared in a doc, or used in a
non-secure context, revoke it at
https://github.com/settings/personal-access-tokens before proceeding.

### 2. Bump the version

Edit `cli/pyproject.toml`:

```toml
version = "0.1.0"   # → "0.2.0" for minor, "0.1.1" for patch, "1.0.0" for major
```

Edit `cli/src/infini/__init__.py` to match:

```python
__version__ = "0.1.0"   # keep in sync with pyproject.toml
```

Update `CHANGELOG.md` with the changes in this release.

### 3. Test the local build

```bash
cd cli
python -m build
twine check dist/*
```

The build produces two files in `dist/`:
- `infini_cli-0.1.0-py3-none-any.whl`
- `infini_cli-0.1.0.tar.gz`

`twine check` validates the metadata (README renders, required fields
present). If it fails, fix the issue before continuing.

### 4. Upload manually (first time only)

For the very first publish, do it manually to confirm everything works:

```bash
twine upload dist/*
```

Username: `__token__`
Password: your `pypi-...` API token

After this succeeds, `pip install infini-cli` works for anyone, anywhere.

### 5. Tag the release

```bash
git tag v0.1.0
git push origin v0.1.0
```

Pushing the tag triggers the `publish.yml` workflow automatically. The
workflow builds, checks, and uploads to PyPI. Future releases use this
path — no manual `twine upload` needed.

### 6. Create a GitHub Release

Go to https://github.com/NickAiNYC/infini/releases/new and create a
release from the tag you just pushed. Paste the relevant section from
`CHANGELOG.md` as the release notes.

---

## Versioning

INFINI follows [Semantic Versioning](https://semver.org/):

| Bump | When to use |
| --- | --- |
| **Patch** (`0.1.0` → `0.1.1`) | Bug fixes, doc improvements, no new features |
| **Minor** (`0.1.0` → `0.2.0`) | New features, new CLI commands, backward-compatible |
| **Major** (`0.1.0` → `1.0.0`) | Breaking changes to the spec, CLI, or trace format |

The spec version (`LOOPFILE: "1.0"`) is independent of the CLI version.
A CLI `0.5.0` can still support spec `1.0`.

---

## Distribution channels

| Channel | What | Status |
| --- | --- | --- |
| **PyPI** (`pip install infini-cli`) | The Python package | Primary |
| **GitHub Releases** | Tagged source + release notes | Primary |
| **GHCR** (`ghcr.io/nickainyc/infini`) | Future Docker image | Planned |
| **GitHub Packages (Python)** | — | Not used |

We do not publish Python packages to GitHub Packages. PyPI is the
standard; GitHub Packages for Python requires a custom index URL that
breaks the one-command install.

---

## Rollback

PyPI does not allow re-uploading the same version number. If a release
is broken:

1. **Yank it:** `pip uninstall infini-cli; pip install infini-cli==0.1.0`
   still works, but `pip install infini-cli` won't pick it up.
   ```bash
   twine upload --repository pypi dist/infini_cli-0.1.0-py3-none-any.whl --verbose
   # then yank:
   # go to https://pypi.org/manage/project/infini-cli/release/0.1.0/
   # click "Yank"
   ```

2. **Publish a fix as a new version:** bump to `0.1.1`, rebuild, upload.

Never delete a released version. Yank, don't delete.

---

## Security notes

- **Never commit `PYPI_API_TOKEN` to a file.** It lives only in GitHub
  Secrets.
- **Never paste a PyPI token in chat, docs, or commit messages.** If you
  do, revoke it immediately at
  https://pypi.org/manage/account/token/.
- **The publish workflow only runs on tagged commits.** A rogue PR can't
  trigger a publish.
- **PyPI tokens are scoped.** Use a project-scoped token after the first
  publish, not an account-wide one.

---

## Checklist for v0.1.0 (first release)

- [ ] Revoke any exposed GitHub PATs
- [ ] Create PyPI account with 2FA
- [ ] Generate PyPI API token
- [ ] Add `PYPI_API_TOKEN` to GitHub secrets
- [ ] `cd cli && python -m build && twine check dist/*`
- [ ] `twine upload dist/*` (manual first publish)
- [ ] Verify `pip install infini-cli` works in a fresh venv
- [ ] `git tag v0.1.0 && git push origin v0.1.0`
- [ ] Create GitHub Release with changelog notes
- [ ] Post the launch tweet thread
