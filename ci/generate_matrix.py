"""Compatibility matrix generator.

Generates spec/compatibility.md from adapter manifests and certification
reports. Run with: python ci/generate_matrix.py
"""
from __future__ import annotations

import json
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).parent.parent
ADAPTERS_DIR = REPO_ROOT / "adapters"
CERTIFICATIONS_DIR = REPO_ROOT / "registry" / "certifications"
OUTPUT = REPO_ROOT / "spec" / "compatibility.md"

# All capabilities tracked in the matrix, in display order
CAPABILITIES = [
    ("validate", "parse_loopfile"),
    ("run", "run_loop"),
    ("verify", "verify"),
    ("inspect", "inspect_trace"),
    ("replay", "replay"),
    ("diff", "diff"),
    ("memory", "memory"),
    ("tools_mcp", "tools_mcp"),
    ("dag_parallel", "dag_parallel"),
    ("budget", "budget"),
    ("verification", "verification"),
    ("trace_export", "trace_export"),
]


def load_adapter_info(adapter_dir: Path) -> dict:
    """Load adapter info from adapter.yaml + certification report."""
    manifest_path = adapter_dir / "adapter.yaml"
    info = {
        "name": adapter_dir.name,
        "version": "—",
        "type": "—",
        "capabilities": {},
        "cert_status": None,
        "compat_pct": None,
        "has_manifest": False,
    }

    if manifest_path.exists():
        with manifest_path.open() as f:
            manifest = yaml.safe_load(f)
        if isinstance(manifest, dict):
            adapter = manifest.get("adapter", {})
            info["name"] = adapter.get("name", adapter_dir.name)
            info["version"] = adapter.get("version", "—")
            info["type"] = adapter.get("type", "—")
            info["capabilities"] = manifest.get("capabilities", {}) or {}
            info["has_manifest"] = True

    # Load certification report if it exists
    cert_path = CERTIFICATIONS_DIR / f"{info['name']}.json"
    if cert_path.exists():
        try:
            cert = json.loads(cert_path.read_text())
            info["cert_status"] = cert.get("certification_status")
            info["compat_pct"] = cert.get("compatibility_percentage")
        except json.JSONDecodeError:
            pass

    return info


def cap_icon(supported: bool | None) -> str:
    if supported is True:
        return "✅"
    elif supported is False:
        return "❌"
    return "🚧"


def generate_matrix() -> str:
    """Generate the compatibility matrix markdown."""
    adapters = []
    if ADAPTERS_DIR.exists():
        for d in sorted(ADAPTERS_DIR.iterdir()):
            if d.is_dir():
                adapters.append(load_adapter_info(d))

    lines = [
        "# Engine Compatibility Matrix",
        "",
        "> Auto-generated from `adapters/*/adapter.yaml` and `registry/certifications/*.json`.",
        "> Run `python ci/generate_matrix.py` to regenerate.",
        "",
        "## Conformance levels",
        "",
        "An adapter is **certified** when it passes all required conformance cases.",
        "See [`RELEASE.md`](../RELEASE.md) for the certification process.",
        "",
        "Legend: ✅ supported · 🚧 in progress · ❌ not supported · — not declared",
        "",
        "## Matrix",
        "",
    ]

    # Build header
    headers = ["Engine", "Version", "Type"]
    for display, _ in CAPABILITIES:
        headers.append(display.replace("_", " ").title())
    headers.extend(["Compat %", "Status"])

    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Build rows
    for a in adapters:
        row = [a["name"], a["version"], a["type"]]
        for _, cap_key in CAPABILITIES:
            val = a["capabilities"].get(cap_key)
            if val is None and a["has_manifest"]:
                row.append("❌")
            elif val is True:
                row.append("✅")
            elif val is False:
                row.append("🚧")
            else:
                row.append("—")
        row.append(f"{a['compat_pct']}%" if a['compat_pct'] is not None else "—")
        row.append(a['cert_status'] or "—")
        lines.append("| " + " | ".join(row) + " |")

    lines.extend([
        "",
        "## Certification reports",
        "",
    ])

    cert_reports = sorted(CERTIFICATIONS_DIR.glob("*.json")) if CERTIFICATIONS_DIR.exists() else []
    if cert_reports:
        for report_path in cert_reports:
            try:
                report = json.loads(report_path.read_text())
                name = report.get("adapter_name", report_path.stem)
                status = report.get("certification_status", "—")
                pct = report.get("compatibility_percentage", "—")
                lines.append(f"- [`{name}`](../registry/certifications/{report_path.name}) — {status} ({pct}%)")
            except json.JSONDecodeError:
                pass
    else:
        lines.append("_No certification reports yet. Run `infini certify adapters/<name>` to generate one._")

    lines.extend([
        "",
        "## Updating this matrix",
        "",
        "```bash",
        "# Certify an adapter (generates registry/certifications/<name>.json)",
        "infini certify adapters/hermes --engine infini --mock",
        "infini certify adapters/openclaw --engine infini --mock",
        "",
        "# Regenerate this matrix from manifests + certifications",
        "python ci/generate_matrix.py",
        "```",
        "",
        "This file is auto-generated. Do not edit by hand.",
    ])

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(generate_matrix())
    print(f"Generated {OUTPUT}")
