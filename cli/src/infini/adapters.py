"""Adapter discovery and capability metadata.

Scans the adapters/ directory for adapter.yaml manifests and reports
actual capabilities (parse, run, verify, inspect, replay, diff) instead
of just directory names.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

import yaml


def find_adapters_dir(start: Optional[Path] = None) -> Optional[Path]:
    """Search upwards from start (or cwd) for an adapters/ directory."""
    p = Path(start or Path.cwd()).resolve()
    root = p.anchor
    while True:
        candidate = p / "adapters"
        if candidate.is_dir():
            return candidate
        if str(p) == root:
            return None
        p = p.parent


def load_adapter_manifest(adapter_dir: Path) -> dict | None:
    """Load an adapter's adapter.yaml manifest. Returns None if not found."""
    manifest_path = adapter_dir / "adapter.yaml"
    if not manifest_path.exists():
        return None
    try:
        with manifest_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def detect_adapters(base: Optional[Path] = None) -> list[dict]:
    """Scan for adapters and return their manifests.

    Returns a list of dicts, each with at minimum:
      - name: adapter directory name
      - path: absolute path to the adapter directory
      - manifest: the parsed adapter.yaml (or None if no manifest)
      - capabilities: list of supported capability strings (from manifest, or [])
    """
    adapters_dir = find_adapters_dir(base)
    if not adapters_dir:
        return []

    results = []
    for p in sorted(adapters_dir.iterdir()):
        if not p.is_dir():
            continue
        manifest = load_adapter_manifest(p)
        caps = []
        if manifest and isinstance(manifest.get("capabilities"), dict):
            caps = [k for k, v in manifest["capabilities"].items() if v is True]
        results.append({
            "name": p.name,
            "path": str(p),
            "manifest": manifest,
            "capabilities": caps,
        })
    return results
