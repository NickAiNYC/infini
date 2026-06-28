"""Adapter certification — `infini certify <adapter-path>`.

Certifies that an adapter:
  1. Has a valid adapter.yaml manifest
  2. Declares supported capabilities
  3. Passes required conformance cases (or marks them unsupported with reason)
  4. Produces a machine-readable JSON + human-readable Markdown report

Certification status:
  - experimental: < 50% compatibility, or missing required capabilities
  - compatible:   50-89% compatibility
  - certified:    >= 90% compatibility + all required capabilities pass
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

from .parse import parse_file, ParseError
from .engine import run as run_loop
from .adapters import load_adapter_manifest

console = Console()

# Required capabilities for "certified" status
REQUIRED_CAPABILITIES = ["parse_loopfile"]
# All capabilities tracked in the matrix
ALL_CAPABILITIES = [
    "parse_loopfile", "run_loop", "verify", "inspect_trace",
    "replay", "diff", "memory", "tools_mcp", "dag_parallel",
    "budget", "verification", "trace_export",
]


@dataclass
class ConformanceResult:
    test_name: str
    status: str  # pass | fail | skip
    detail: str
    required_capabilities: list[str]


@dataclass
class CertificationReport:
    adapter_name: str
    version: str
    engine: str
    spec_version: str
    supported_capabilities: list[str]
    conformance_results: list[ConformanceResult]
    compatibility_percentage: float
    certification_status: str  # experimental | compatible | certified
    timestamp: str
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "adapter_name": self.adapter_name,
            "version": self.version,
            "engine": self.engine,
            "spec_version": self.spec_version,
            "supported_capabilities": self.supported_capabilities,
            "conformance_results": [asdict(c) for c in self.conformance_results],
            "compatibility_percentage": self.compatibility_percentage,
            "certification_status": self.certification_status,
            "timestamp": self.timestamp,
            "notes": self.notes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _map_manifest_caps(manifest_caps: dict) -> list[str]:
    """Map adapter.yaml capability keys to the canonical list."""
    if not isinstance(manifest_caps, dict):
        return []
    return [k for k, v in manifest_caps.items() if v is True]


def _determine_status(supported: list[str], passed: int, total: int) -> str:
    """Determine certification status from capabilities + conformance results."""
    has_required = all(cap in supported for cap in REQUIRED_CAPABILITIES)
    if not has_required:
        return "experimental"
    pct = (passed / total * 100) if total > 0 else 0
    if pct >= 90:
        return "certified"
    elif pct >= 50:
        return "compatible"
    else:
        return "experimental"


def certify(
    adapter_path: str | Path,
    engine: str = "infini",
    mock: bool = True,
    conformance_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
) -> CertificationReport:
    """Certify an adapter. Returns a CertificationReport."""
    adapter_path = Path(adapter_path)
    manifest = load_adapter_manifest(adapter_path)

    notes: list[str] = []

    if manifest is None:
        notes.append(f"No adapter.yaml manifest found at {adapter_path}")
        # Can't certify without a manifest
        report = CertificationReport(
            adapter_name=adapter_path.name,
            version="unknown",
            engine=engine,
            spec_version="unknown",
            supported_capabilities=[],
            conformance_results=[],
            compatibility_percentage=0.0,
            certification_status="experimental",
            timestamp=_now_iso(),
            notes=notes,
        )
        return report

    adapter_info = manifest.get("adapter", {}) if isinstance(manifest, dict) else {}
    name = adapter_info.get("name", adapter_path.name)
    version = adapter_info.get("version", "unknown")
    spec_version = adapter_info.get("spec", "unknown")
    manifest_caps = manifest.get("capabilities", {}) if isinstance(manifest, dict) else {}
    supported = _map_manifest_caps(manifest_caps)

    if not supported:
        notes.append("Adapter declares no supported capabilities")

    # Run conformance if the directory exists
    conformance_results: list[ConformanceResult] = []
    if conformance_dir is None:
        # Look for tests/conformance relative to repo root
        repo_root = adapter_path.parent.parent
        conformance_dir = repo_root / "tests" / "conformance"

    conformance_dir = Path(conformance_dir)
    if conformance_dir.exists():
        test_dirs = sorted(
            d for d in conformance_dir.iterdir()
            if d.is_dir() and (d / "Loopfile.yaml").exists()
        )

        for test_dir in test_dirs:
            test_name = test_dir.name
            loopfile_path = test_dir / "Loopfile.yaml"

            # Determine required capabilities from the test's expected.json
            expected_path = test_dir / "expected.json"
            required_caps: list[str] = []
            if expected_path.exists():
                try:
                    expected = json.loads(expected_path.read_text())
                    required_caps = expected.get("required_capabilities", [])
                except json.JSONDecodeError:
                    pass

            # Check if the adapter supports the required capabilities
            missing_caps = [c for c in required_caps if c not in supported]
            if missing_caps:
                conformance_results.append(ConformanceResult(
                    test_name=test_name,
                    status="skip",
                    detail=f"missing capabilities: {', '.join(missing_caps)}",
                    required_capabilities=required_caps,
                ))
                continue

            # Run the loop
            try:
                lf = parse_file(loopfile_path)
                run_dir = Path("runs/certify") / name / test_name
                trace = run_loop(
                    lf,
                    output_dir=run_dir,
                    mock=mock,
                    max_iterations=5,
                    verbose=False,
                    deterministic=True,
                )

                if trace.outcome == "verified":
                    conformance_results.append(ConformanceResult(
                        test_name=test_name,
                        status="pass",
                        detail=f"outcome={trace.outcome}, steps={len(trace.steps)}, iters={trace.iterations}",
                        required_capabilities=required_caps,
                    ))
                else:
                    conformance_results.append(ConformanceResult(
                        test_name=test_name,
                        status="fail",
                        detail=f"outcome={trace.outcome}",
                        required_capabilities=required_caps,
                    ))
            except ParseError as e:
                conformance_results.append(ConformanceResult(
                    test_name=test_name,
                    status="fail",
                    detail=f"parse error: {e}",
                    required_capabilities=required_caps,
                ))
            except Exception as e:
                conformance_results.append(ConformanceResult(
                    test_name=test_name,
                    status="fail",
                    detail=f"run error: {e}",
                    required_capabilities=required_caps,
                ))
    else:
        notes.append(f"Conformance directory not found: {conformance_dir}")

    # Calculate compatibility percentage
    # Weight: capabilities (50%) + conformance pass rate (50%)
    cap_score = len([c for c in supported if c in ALL_CAPABILITIES]) / len(ALL_CAPABILITIES) * 50
    if conformance_results:
        passed = sum(1 for r in conformance_results if r.status == "pass")
        conf_score = (passed / len(conformance_results)) * 50
    else:
        conf_score = 0
    compatibility_percentage = round(cap_score + conf_score, 1)

    # Determine status
    passed_count = sum(1 for r in conformance_results if r.status == "pass")
    total_count = len(conformance_results)
    status = _determine_status(supported, passed_count, total_count)

    report = CertificationReport(
        adapter_name=name,
        version=version,
        engine=engine,
        spec_version=spec_version,
        supported_capabilities=supported,
        conformance_results=conformance_results,
        compatibility_percentage=compatibility_percentage,
        certification_status=status,
        timestamp=_now_iso(),
        notes=notes,
    )

    # Save report
    if output_dir:
        output_dir = Path(output_dir)
    else:
        output_dir = Path("registry/certifications")
    output_dir.mkdir(parents=True, exist_ok=True)

    json_path = output_dir / f"{name}.json"
    json_path.write_text(report.to_json())

    md_path = output_dir / f"{name}.md"
    md_path.write_text(_report_to_markdown(report))

    return report


def _report_to_markdown(report: CertificationReport) -> str:
    """Render a certification report as Markdown."""
    lines = [
        f"# Certification Report: {report.adapter_name}",
        "",
        f"**Status:** `{report.certification_status}`",
        f"**Compatibility:** {report.compatibility_percentage}%",
        f"**Version:** {report.version}",
        f"**Engine:** {report.engine}",
        f"**Spec:** {report.spec_version}",
        f"**Certified at:** {report.timestamp}",
        "",
        "## Supported capabilities",
        "",
    ]
    if report.supported_capabilities:
        for cap in report.supported_capabilities:
            lines.append(f"- `{cap}`")
    else:
        lines.append("(none declared)")

    lines.extend(["", "## Conformance results", ""])
    if report.conformance_results:
        lines.append("| Test | Status | Detail | Required capabilities |")
        lines.append("| --- | :---: | --- | --- |")
        for r in report.conformance_results:
            status_icon = {"pass": "✅", "fail": "❌", "skip": "⏭️"}.get(r.status, "?")
            caps = ", ".join(r.required_capabilities) if r.required_capabilities else "—"
            lines.append(f"| {r.test_name} | {status_icon} {r.status} | {r.detail} | {caps} |")
    else:
        lines.append("(no conformance tests run)")

    if report.notes:
        lines.extend(["", "## Notes", ""])
        for note in report.notes:
            lines.append(f"- {note}")

    lines.extend([
        "",
        "---",
        "",
        "Generated by `infini certify`. See [certification format](../../spec/versions.md).",
    ])
    return "\n".join(lines)


def print_report(report: CertificationReport) -> None:
    """Print a human-readable summary of a certification report."""
    console.rule(f"[bold]Certification: {report.adapter_name}[/bold]")
    console.print(f"  [dim]version:[/dim] {report.version}")
    console.print(f"  [dim]engine:[/dim]   {report.engine}")
    console.print(f"  [dim]spec:[/dim]     {report.spec_version}")
    console.print(f"  [dim]caps:[/dim]     {', '.join(report.supported_capabilities) or '(none)'}")
    console.print(f"  [dim]compat:[/dim]   {report.compatibility_percentage}%")
    status_color = {"certified": "green", "compatible": "yellow", "experimental": "red"}.get(
        report.certification_status, "white"
    )
    console.print(f"  [dim]status:[/dim]   [{status_color}]{report.certification_status}[/{status_color}]")
    console.print(f"  [dim]time:[/dim]     {report.timestamp}")

    if report.conformance_results:
        table = Table(show_lines=False)
        table.add_column("Test", style="bold")
        table.add_column("Status")
        table.add_column("Detail", style="dim")
        for r in report.conformance_results:
            status_str = {"pass": "[green]PASS[/green]", "fail": "[red]FAIL[/red]", "skip": "[yellow]SKIP[/yellow]"}.get(r.status, r.status)
            table.add_row(r.test_name, status_str, r.detail)
        console.print(table)

    if report.notes:
        console.print("\n[bold]Notes:[/bold]")
        for note in report.notes:
            console.print(f"  • {note}")
