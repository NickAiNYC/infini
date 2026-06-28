"""Tests for the certification module."""
import json
import pytest
from pathlib import Path

from infini.certify import (
    CertificationReport,
    ConformanceResult,
    _determine_status,
    _map_manifest_caps,
    _report_to_markdown,
)


def test_map_manifest_caps_returns_true_capabilities():
    """Capabilities with value True should be in the result."""
    caps = {
        "parse_loopfile": True,
        "run_loop": True,
        "verify": False,
        "inspect_trace": True,
        "replay": False,
    }
    result = _map_manifest_caps(caps)
    assert "parse_loopfile" in result
    assert "run_loop" in result
    assert "inspect_trace" in result
    assert "verify" not in result
    assert "replay" not in result


def test_map_manifest_caps_handles_empty():
    """Empty capabilities dict returns empty list."""
    assert _map_manifest_caps({}) == []
    assert _map_manifest_caps(None) == []


def test_determine_status_experimental_without_required():
    """Missing required capabilities → experimental."""
    status = _determine_status(supported=[], passed=8, total=8)
    assert status == "experimental"


def test_determine_status_certified_at_90_percent():
    """>= 90% pass rate with required capabilities → certified."""
    status = _determine_status(
        supported=["parse_loopfile"],
        passed=9,
        total=10,
    )
    assert status == "certified"


def test_determine_status_compatible_at_50_percent():
    """50-89% pass rate with required capabilities → compatible."""
    status = _determine_status(
        supported=["parse_loopfile"],
        passed=5,
        total=10,
    )
    assert status == "compatible"


def test_determine_status_experimental_below_50_percent():
    """< 50% pass rate with required capabilities → experimental."""
    status = _determine_status(
        supported=["parse_loopfile"],
        passed=4,
        total=10,
    )
    assert status == "experimental"


def test_certification_report_to_json_roundtraps():
    """Report should serialize to JSON and contain all fields."""
    report = CertificationReport(
        adapter_name="test-adapter",
        version="1.0.0",
        engine="infini",
        spec_version="LOOPFILE-1.0",
        supported_capabilities=["parse_loopfile", "run_loop"],
        conformance_results=[
            ConformanceResult(
                test_name="simple-loop",
                status="pass",
                detail="outcome=verified",
                required_capabilities=["parse_loopfile"],
            ),
        ],
        compatibility_percentage=85.0,
        certification_status="compatible",
        timestamp="2026-06-28T12:00:00Z",
        notes=["test note"],
    )
    data = json.loads(report.to_json())
    assert data["adapter_name"] == "test-adapter"
    assert data["certification_status"] == "compatible"
    assert data["compatibility_percentage"] == 85.0
    assert len(data["conformance_results"]) == 1
    assert data["conformance_results"][0]["status"] == "pass"


def test_certification_report_does_not_include_runs_paths():
    """Reports must not contain transient runs/ paths."""
    report = CertificationReport(
        adapter_name="test",
        version="1.0.0",
        engine="infini",
        spec_version="LOOPFILE-1.0",
        supported_capabilities=["parse_loopfile"],
        conformance_results=[
            ConformanceResult("test", "pass", "outcome=verified", ["parse_loopfile"]),
        ],
        compatibility_percentage=100.0,
        certification_status="certified",
        timestamp="2026-06-28T12:00:00Z",
    )
    json_str = report.to_json()
    md_str = _report_to_markdown(report)
    assert "runs/" not in json_str
    assert "runs/" not in md_str


def test_markdown_report_represents_skipped_honestly():
    """Skipped capabilities must appear as skip, not pass."""
    report = CertificationReport(
        adapter_name="test",
        version="1.0.0",
        engine="infini",
        spec_version="LOOPFILE-1.0",
        supported_capabilities=["parse_loopfile"],
        conformance_results=[
            ConformanceResult("a", "pass", "ok", ["parse_loopfile"]),
            ConformanceResult("b", "skip", "missing replay", ["replay"]),
            ConformanceResult("c", "fail", "outcome=unverified", ["verify"]),
        ],
        compatibility_percentage=33.3,
        certification_status="experimental",
        timestamp="2026-06-28T12:00:00Z",
    )
    md = _report_to_markdown(report)
    assert "⏭️ skip" in md
    assert "❌ fail" in md
    assert "✅ pass" in md


def test_markdown_report_includes_all_required_fields():
    """Markdown report must include name, version, status, compat, caps."""
    report = CertificationReport(
        adapter_name="hermes",
        version="1.0.0",
        engine="infini",
        spec_version="LOOPFILE-1.0",
        supported_capabilities=["parse_loopfile", "run_loop"],
        conformance_results=[],
        compatibility_percentage=70.0,
        certification_status="certified",
        timestamp="2026-06-28T12:00:00Z",
    )
    md = _report_to_markdown(report)
    assert "hermes" in md
    assert "1.0.0" in md
    assert "certified" in md
    assert "70.0%" in md
    assert "parse_loopfile" in md
    assert "run_loop" in md
