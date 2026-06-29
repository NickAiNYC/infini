"""Objective verification — every check is a real, reproducible assertion.

No LLM judgement. No random confidence. A check either holds against the bytes
on disk or it does not. Supported check grammar (left of the first colon is the
artifact path):

    <path>:exists              file exists and is non-empty
    <path>:valid_json          file parses as JSON
    <path>:contains:<text>     file text contains the literal substring
    <path>:key:<dotted.key>    JSON file has the (possibly nested) key
    <path>:sha256:<hexdigest>  file content hash equals the given digest
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def _split(check: str) -> tuple[str, str, str]:
    parts = check.split(":", 2)
    path = parts[0]
    op = parts[1] if len(parts) > 1 else ""
    arg = parts[2] if len(parts) > 2 else ""
    return path, op, arg


def evaluate_check(check: str, work: Path) -> dict:
    """Return {check, status: pass|fail, detail}. Never raises."""
    path_s, op, arg = _split(check)
    target = work / path_s
    try:
        if op == "exists":
            ok = target.exists() and target.stat().st_size > 0
            return _r(check, ok, "present" if ok else "missing or empty")
        if op == "valid_json":
            if not target.exists():
                return _r(check, False, "file missing")
            json.loads(target.read_text(encoding="utf-8"))
            return _r(check, True, "parses as JSON")
        if op == "contains":
            if not target.exists():
                return _r(check, False, "file missing")
            ok = arg in target.read_text(encoding="utf-8")
            return _r(check, ok, f"substring {'found' if ok else 'absent'}: {arg!r}")
        if op == "key":
            if not target.exists():
                return _r(check, False, "file missing")
            obj = json.loads(target.read_text(encoding="utf-8"))
            cur = obj
            for part in arg.split("."):
                if isinstance(cur, dict) and part in cur:
                    cur = cur[part]
                else:
                    return _r(check, False, f"key absent: {arg}")
            return _r(check, True, f"key present: {arg}")
        if op == "sha256":
            if not target.exists():
                return _r(check, False, "file missing")
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            ok = digest == arg
            return _r(check, ok, f"hash {'matches' if ok else 'MISMATCH'} ({digest[:12]}…)")
        return _r(check, False, f"unknown op: {op}")
    except Exception as e:  # objective failure, reported not hidden
        return _r(check, False, f"error: {e}")


def _r(check: str, ok: bool, detail: str) -> dict:
    return {"check": check, "status": "pass" if ok else "fail", "detail": detail}


def run_verification(checks: list[str], work: Path) -> tuple[list[dict], bool]:
    """Evaluate all checks. Returns (results, all_passed)."""
    results = [evaluate_check(c, work) for c in checks]
    all_passed = all(r["status"] == "pass" for r in results)
    return results, all_passed
