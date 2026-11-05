"""Tests for OpenTelemetry export, cross-engine trace compatibility, and divergence diffing."""
from pathlib import Path
import pytest

from infini.parse import parse_file
from infini.engine import run as run_reference_engine
from infini.diff import find_first_step_divergence
from infini.otel import trace_to_otel, export_trace_to_otel_json

import sys
_repo_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_repo_root / "adapters" / "langgraph"))
from langgraph_adapter import LangGraphAdapter  # noqa: E402


def test_cross_engine_trace_match(tmp_path):
    """Proves the portability claim: same Loopfile produces matching span trees and attribute keys across two engines."""
    loopfile_path = _repo_root / "tests" / "conformance" / "simple-loop" / "Loopfile.yaml"
    lf = parse_file(loopfile_path)

    # Engine 1: INFINI Reference Engine (deterministic mock mode)
    ref_run_dir = tmp_path / "ref"
    ref_trace = run_reference_engine(
        lf,
        output_dir=ref_run_dir,
        mock=True,
        deterministic=True,
        verbose=False,
    )

    # Engine 2: LangGraph Adapter (mock mode)
    lg_run_dir = tmp_path / "langgraph"
    lg_adapter = LangGraphAdapter()
    lg_trace = lg_adapter.run(
        lf,
        mock=True,
        output_dir=lg_run_dir,
        verbose=False,
    )

    # Convert both to OpenTelemetry GenAI format
    ref_otel = trace_to_otel(ref_trace.to_dict())
    lg_otel = trace_to_otel(lg_trace.to_dict())

    # Verify standard OTel schema envelopes
    assert "resourceSpans" in ref_otel
    assert "resourceSpans" in lg_otel

    ref_spans = ref_otel["resourceSpans"][0]["scopeSpans"][0]["spans"]
    lg_spans = lg_otel["resourceSpans"][0]["scopeSpans"][0]["spans"]

    # Assert identical span tree structure
    assert len(ref_spans) == len(lg_spans), f"Span count mismatch: {len(ref_spans)} vs {len(lg_spans)}"

    # Check root spans
    ref_root = ref_spans[0]
    lg_root = lg_spans[0]
    assert ref_root["parentSpanId"] == ""
    assert lg_root["parentSpanId"] == ""
    assert ref_root["name"] == lg_root["name"]

    # Verify span tree parent-child links and attribute keys across all spans
    for i in range(len(ref_spans)):
        r_span = ref_spans[i]
        l_span = lg_spans[i]

        # Names and hierarchy
        assert r_span["name"] == l_span["name"]
        if i > 0:
            assert r_span["parentSpanId"] == ref_root["spanId"]
            assert l_span["parentSpanId"] == lg_root["spanId"]

        # Attribute keys must match exactly
        r_keys = {attr["key"] for attr in r_span["attributes"]}
        l_keys = {attr["key"] for attr in l_span["attributes"]}
        assert r_keys == l_keys, f"Span {r_span['name']} attribute keys mismatch: {r_keys ^ l_keys}"

        # Verify GenAI conventions are present
        assert "gen_ai.system" in r_keys

    # Test file export works and produces valid JSON on disk
    export_path = tmp_path / "exported_otel.json"
    exported_data = export_trace_to_otel_json(ref_run_dir / "run.json", export_path)
    assert export_path.exists()
    assert exported_data["resourceSpans"][0]["scopeSpans"][0]["spans"][0]["name"] == ref_root["name"]


def test_first_step_divergence_detection():
    """Asserts that find_first_step_divergence accurately identifies the exact step and reason of divergence."""
    trace_base = {
        "steps": [
            {"id": "s1", "name": "fetch", "status": "ok", "action": "read", "agent": "worker", "artifacts": ["a.txt"]},
            {"id": "s2", "name": "process", "status": "ok", "action": "compute", "agent": "worker", "artifacts": ["b.txt"]},
        ]
    }

    # Case 1: Identical steps -> No divergence
    trace_same = {
        "steps": [
            {"id": "s1", "name": "fetch", "status": "ok", "action": "read", "agent": "worker", "artifacts": ["a.txt"]},
            {"id": "s2", "name": "process", "status": "ok", "action": "compute", "agent": "worker", "artifacts": ["b.txt"]},
        ]
    }
    assert find_first_step_divergence(trace_base, trace_same) is None

    # Case 2: Divergence at step s2 due to status
    trace_status_diverge = {
        "steps": [
            {"id": "s1", "name": "fetch", "status": "ok", "action": "read", "agent": "worker", "artifacts": ["a.txt"]},
            {"id": "s2", "name": "process", "status": "failed", "action": "compute", "agent": "worker", "artifacts": ["b.txt"]},
        ]
    }
    div = find_first_step_divergence(trace_base, trace_status_diverge)
    assert div is not None
    assert div["step_id"] == "s2"
    assert "Status differed" in div["reason"]

    # Case 3: Divergence due to extra steps
    trace_extra_step = {
        "steps": [
            {"id": "s1", "name": "fetch", "status": "ok", "action": "read", "agent": "worker", "artifacts": ["a.txt"]},
            {"id": "s2", "name": "process", "status": "ok", "action": "compute", "agent": "worker", "artifacts": ["b.txt"]},
            {"id": "s3", "name": "cleanup", "status": "ok", "action": "delete", "agent": "worker", "artifacts": []},
        ]
    }
    div3 = find_first_step_divergence(trace_base, trace_extra_step)
    assert div3 is not None
    assert div3["step_id"] == "s3"
    assert "Step count mismatch" in div3["reason"]

