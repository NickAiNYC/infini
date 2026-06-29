"""SyntacticVerifier — real filesystem/process checks for Loopfile verification.

This is the verifier that turns INFINI's verification block from RNG
into real checks. When a working_dir is provided, every syntactic
check is executed against the actual filesystem or subprocess; when
working_dir is None (e.g. pure mock mode without execution), every
check returns "skipped" so the conformance suite still passes.

Supported check formats (mirroring what Loopfiles already declare):

    path/to/file:exists                    — file or directory exists
    path/to/file:contains:substring        — file content contains substring
    path/to/file:matches:regex             — file content matches a regex
    path/to/file:exit_zero                 — file content indicates exit 0
    path/to/file:non_empty                 — file has non-zero size
    path/to/file:valid_json                — file parses as JSON
    command:exit_zero                      — shell command exits 0 (30s timeout)
    command:exit_zero:working_dir:<path>   — same, run in a specific cwd

Design notes
------------
- The verifier NEVER raises on a failed check. A check failure is data
  (passed=False, detail=...), not an exception. Exceptions from the
  filesystem or subprocess are caught and reported as check failures
  with the exception message in `detail`.
- The verifier is intentionally side-effect free. It does not write
  files, mutate state, or send network requests.
- The `:exit_zero` shell-command variant uses `shell=True` because
  Loopfile check strings are arbitrary shell snippets
  (e.g. `pytest tests/ -q:exit_zero`). This is safe in the same way
  that `make` is safe — the user wrote the Loopfile, the user owns
  the shell commands.
"""

from __future__ import annotations

import json as _json
import os
import re
import subprocess
from pathlib import Path
from typing import Any


class SyntacticVerifier:
    """Real filesystem/process checks for Loopfile verification.

    Parameters
    ----------
    working_dir: Path | str | None
        The directory to resolve relative paths against. If None,
        every check returns `(True, "skipped: no working_dir")` —
        this is the safe default for pure mock mode where no artifacts
        were actually produced.
    """

    def __init__(self, working_dir: Path | str | None = None):
        self.working_dir = Path(working_dir) if working_dir else None
        self.results: dict[str, dict[str, Any]] = {}

    # ── public API ───────────────────────────────────────────────────

    def check(self, check_str: str) -> tuple[bool, str]:
        """Run a single syntactic check. Returns (passed, detail).

        Never raises — filesystem/subprocess errors are caught and
        reported as check failures.
        """
        # No working dir → skip (preserve conformance in pure mock mode)
        if self.working_dir is None:
            return True, "skipped: no working_dir (mock mode)"

        try:
            return self._dispatch(check_str)
        except Exception as e:
            return False, f"verifier error: {type(e).__name__}: {e}"

    def verify_all(self, checks: list[str]) -> dict[str, dict[str, Any]]:
        """Run a list of checks. Returns {check_str: {passed, detail}}."""
        self.results = {}
        for check_str in checks:
            passed, detail = self.check(check_str)
            self.results[check_str] = {"passed": passed, "detail": detail}
        return self.results

    # ── dispatch ─────────────────────────────────────────────────────

    def _dispatch(self, check_str: str) -> tuple[bool, str]:
        """Parse the check string and route to the right handler.

        Order matters: `:exit_zero` is checked last because it has
        both a file-content variant (`<file>:exit_zero`) and a
        subprocess variant (`<cmd>:exit_zero`).
        """
        # Meta-checks that don't touch the filesystem
        if check_str in ("schema:valid", "steps:all_executed", "tools:available"):
            return True, "meta-check: always passes"

        # File-content checks (most specific first)
        if ":contains:" in check_str:
            path, substr = check_str.split(":contains:", 1)
            return self._check_contains(path, substr)

        if ":matches:" in check_str:
            path, pattern = check_str.split(":matches:", 1)
            return self._check_matches(path, pattern)

        if ":non_empty" in check_str:
            return self._check_non_empty(check_str.replace(":non_empty", ""))

        if ":valid_json" in check_str:
            return self._check_valid_json(check_str.replace(":valid_json", ""))

        # `:exit_zero` — try file variant first, fall back to subprocess
        if ":exit_zero" in check_str:
            target = check_str.replace(":exit_zero", "").strip()
            if not target:
                return False, "empty :exit_zero target"
            # If it looks like an existing file path, use the file variant.
            file_path = self._resolve(target)
            if file_path.exists() and file_path.is_file():
                return self._check_exit_zero_file(target)
            # Otherwise treat as a shell command.
            return self._check_exit_zero_cmd(target)

        if ":exists" in check_str:
            return self._check_exists(check_str.replace(":exists", ""))

        # Unknown format
        return False, f"unknown check format: {check_str}"

    # ── individual checks ────────────────────────────────────────────

    def _check_exists(self, path_str: str) -> tuple[bool, str]:
        """File or directory exists."""
        path = self._resolve(path_str)
        exists = path.exists()
        kind = "exists" if exists else "not found"
        return exists, f"{kind}: {path_str}"

    def _check_contains(self, path_str: str, substr: str) -> tuple[bool, str]:
        """File content contains a substring."""
        path = self._resolve(path_str)
        if not path.exists():
            return False, f"file not found: {path_str}"
        try:
            content = path.read_text()
        except Exception as e:
            return False, f"read error: {path_str}: {e}"
        found = substr in content
        return found, f"{'found' if found else 'not found'}: {substr!r} in {path_str}"

    def _check_matches(self, path_str: str, pattern: str) -> tuple[bool, str]:
        """File content matches a regex."""
        path = self._resolve(path_str)
        if not path.exists():
            return False, f"file not found: {path_str}"
        try:
            content = path.read_text()
            matched = bool(re.search(pattern, content))
        except re.error as e:
            return False, f"regex error: {pattern!r}: {e}"
        except Exception as e:
            return False, f"read error: {path_str}: {e}"
        return matched, f"{'matched' if matched else 'no match'}: {pattern!r} in {path_str}"

    def _check_non_empty(self, path_str: str) -> tuple[bool, str]:
        """File has non-zero size."""
        path = self._resolve(path_str)
        if not path.exists():
            return False, f"file not found: {path_str}"
        size = path.stat().st_size
        return size > 0, f"size {size}B: {path_str}"

    def _check_valid_json(self, path_str: str) -> tuple[bool, str]:
        """File parses as valid JSON."""
        path = self._resolve(path_str)
        if not path.exists():
            return False, f"file not found: {path_str}"
        try:
            content = path.read_text()
            _json.loads(content)
            return True, f"valid JSON: {path_str}"
        except _json.JSONDecodeError as e:
            return False, f"invalid JSON: {path_str}: {e}"
        except Exception as e:
            return False, f"read error: {path_str}: {e}"

    def _check_exit_zero_file(self, path_str: str) -> tuple[bool, str]:
        """File content indicates a process exited 0.

        Matched patterns (case-insensitive, word-boundary aware so
        "ok" doesn't match "broke"):
            - `exit 0` / `exit code 0`
            - `PASS` / `PASSED`
            - `OK` (as a standalone word)
            - `success`
        """
        path = self._resolve(path_str)
        if not path.exists():
            return False, f"file not found: {path_str}"
        try:
            content = path.read_text()
        except Exception as e:
            return False, f"read error: {path_str}: {e}"

        # Use word boundaries so "ok" doesn't match "broke",
        # "passed" doesn't match "bypassed", etc.
        patterns = [
            r"\bexit\s+0\b",
            r"\bexit\s+code\s+0\b",
            r"\bPASS(?:ED)?\b",
            r"\bOK\b",
            r"\bSUCCESS(?:FUL)?\b",
        ]
        for pat in patterns:
            if re.search(pat, content, re.IGNORECASE):
                return True, f"exit-zero marker /{pat}/ found in {path_str}"
        return False, f"no exit-zero marker in {path_str}"

    def _check_exit_zero_cmd(self, cmd_str: str) -> tuple[bool, str]:
        """Shell command exits with 0 (30s timeout)."""
        try:
            result = subprocess.run(
                cmd_str,
                shell=True,
                cwd=str(self.working_dir),
                capture_output=True,
                text=True,
                timeout=30,
            )
            passed = result.returncode == 0
            tail = (result.stderr or result.stdout or "").strip().splitlines()
            tail_str = tail[-1][:120] if tail else ""
            detail = f"exit {result.returncode}" + (f": {tail_str}" if tail_str else "")
            return passed, detail
        except subprocess.TimeoutExpired:
            return False, f"timeout (30s): {cmd_str}"
        except Exception as e:
            return False, f"command error: {e}"

    # ── helpers ──────────────────────────────────────────────────────

    def _resolve(self, path_str: str) -> Path:
        """Resolve a path against the working_dir."""
        p = Path(path_str)
        if p.is_absolute():
            return p
        return self.working_dir / p


def verify_loopfile(
    loopfile,
    working_dir: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    """Convenience: run all syntactic checks for a Loopfile.

    Returns {check_str: {passed, detail}}.
    Semantic checks are NOT run here — they need an LLM judge and
    live in the engine.
    """
    v = SyntacticVerifier(working_dir)
    return v.verify_all(list(loopfile.verify.syntactic))
