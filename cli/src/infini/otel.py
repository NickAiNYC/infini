"""OpenTelemetry exporter for INFINI execution traces.

Maps INFINI traces (run.json) to OpenTelemetry format following the
GenAI Semantic Conventions.

OpenTelemetry Specification Status (GenAI WG / Semantic Conventions):
---------------------------------------------------------------------
STABLE Core Trace Attributes:
  - trace_id, span_id, parent_span_id
  - name
  - kind (SPAN_KIND_INTERNAL)
  - start_time_unix_nano, end_time_unix_nano
  - status.code (STATUS_CODE_OK, STATUS_CODE_ERROR)

EXPERIMENTAL GenAI Attributes (v1.27+ Draft):
  - gen_ai.system              ("infini")
  - gen_ai.workflow.name       (Loopfile objective / name)
  - gen_ai.workflow.iterations (iteration count)
  - gen_ai.workflow.outcome    ("verified" | "unverified" | "budget_exceeded")
  - gen_ai.operation.name      (Step action name, e.g. "summarize")
  - gen_ai.request.model       (Agent model tier, e.g. "sonnet")
  - gen_ai.usage.input_tokens  (input token count)
  - gen_ai.usage.output_tokens (output token count)
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _iso_to_unix_nano(iso_str: str | None) -> int:
    """Convert ISO-8601 UTC timestamp to Unix nanoseconds."""
    if not iso_str:
        return int(datetime.now(timezone.utc).timestamp() * 1e9)
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return int(dt.timestamp() * 1e9)
    except Exception:
        return int(datetime.now(timezone.utc).timestamp() * 1e9)


def _hash_id(data: str, length: int) -> str:
    """Deterministic hex ID from string seed."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()[:length]


def trace_to_otel(trace_data: dict[str, Any]) -> dict[str, Any]:
    """Convert an INFINI trace dict into an OpenTelemetry ResourceSpans dict.

    Follows OTel GenAI Semantic Conventions with explicit stable vs experimental
    attribute segregation.
    """
    loopfile_name = trace_data.get("loopfile", "unknown")
    clean_loop_name = loopfile_name.split("/")[-1].split("@")[0] if ("/" in loopfile_name or "@" in loopfile_name) else loopfile_name
    loopfile_hash = trace_data.get("loopfile_hash", "0" * 32)
    engine_info = trace_data.get("engine", {})
    engine_type = engine_info.get("type", "unknown") if isinstance(engine_info, dict) else str(engine_info)
    outcome = trace_data.get("outcome", "unverified")

    # Generate deterministic 128-bit (32 hex char) trace ID from loopfile and started_at
    started_at = trace_data.get("started_at", "")
    trace_id = _hash_id(f"{loopfile_hash}:{started_at}", 32)

    # Root span: loop workflow execution
    root_span_id = _hash_id(f"{trace_id}:root", 16)
    root_start_nano = _iso_to_unix_nano(trace_data.get("started_at"))
    root_end_nano = _iso_to_unix_nano(trace_data.get("ended_at"))
    if root_end_nano <= root_start_nano:
        root_end_nano = root_start_nano + 1_000_000_000  # at least 1s

    root_status = "STATUS_CODE_OK" if outcome == "verified" else "STATUS_CODE_ERROR"

    budget = trace_data.get("budget", {})

    root_span = {
        "traceId": trace_id,
        "spanId": root_span_id,
        "parentSpanId": "",
        "name": f"loop {clean_loop_name}",
        "kind": "SPAN_KIND_INTERNAL",
        "startTimeUnixNano": root_start_nano,
        "endTimeUnixNano": root_end_nano,
        "attributes": [
            # Experimental GenAI Semantic Conventions
            {"key": "gen_ai.system", "value": {"stringValue": "infini"}},
            {"key": "gen_ai.workflow.name", "value": {"stringValue": clean_loop_name}},
            {"key": "gen_ai.workflow.outcome", "value": {"stringValue": outcome}},
            {"key": "gen_ai.workflow.iterations", "value": {"intValue": int(trace_data.get("iterations", 1))}},
            # Runtime attributes
            {"key": "engine.type", "value": {"stringValue": engine_type}},
            {"key": "cost.dollars", "value": {"doubleValue": float(budget.get("spent_dollars", 0.0))}},
            {"key": "cost.minutes", "value": {"doubleValue": float(budget.get("spent_minutes", 0.0))}},
        ],
        "status": {"code": root_status},
    }

    spans = [root_span]

    # Child spans for each step execution
    steps = trace_data.get("steps", [])
    step_start_offset = root_start_nano
    for idx, step in enumerate(steps):
        step_id = step.get("id", f"s{idx}")
        step_name = step.get("name", "step")
        span_id = _hash_id(f"{root_span_id}:{step_id}:{idx}", 16)
        
        s_start = _iso_to_unix_nano(step.get("started_at"))
        s_end = _iso_to_unix_nano(step.get("ended_at"))
        if s_start == root_start_nano and s_end == root_start_nano:
            s_start = step_start_offset
            s_end = s_start + 100_000_000
            step_start_offset = s_end

        cost_dict = step.get("cost", {})
        tokens_dict = cost_dict.get("tokens", {}) if isinstance(cost_dict, dict) else {}
        input_tokens = int(tokens_dict.get("input", 0))
        output_tokens = int(tokens_dict.get("output", 0))
        dollars = float(cost_dict.get("dollars", 0.0)) if isinstance(cost_dict, dict) else 0.0

        step_status = step.get("status", "ok")
        span_status = "STATUS_CODE_OK" if step_status == "ok" else "STATUS_CODE_ERROR"

        step_span = {
            "traceId": trace_id,
            "spanId": span_id,
            "parentSpanId": root_span_id,
            "name": f"step {step_id} ({step_name})",
            "kind": "SPAN_KIND_INTERNAL",
            "startTimeUnixNano": s_start,
            "endTimeUnixNano": s_end,
            "attributes": [
                # Experimental GenAI Semantic Conventions
                {"key": "gen_ai.system", "value": {"stringValue": "infini"}},
                {"key": "gen_ai.operation.name", "value": {"stringValue": step.get("action", "execute")}},
                {"key": "gen_ai.request.model", "value": {"stringValue": step.get("agent", "agent")}},
                {"key": "gen_ai.usage.input_tokens", "value": {"intValue": input_tokens}},
                {"key": "gen_ai.usage.output_tokens", "value": {"intValue": output_tokens}},
                # Step identifiers & cost
                {"key": "step.id", "value": {"stringValue": step_id}},
                {"key": "step.name", "value": {"stringValue": step_name}},
                {"key": "step.agent", "value": {"stringValue": step.get("agent", "")}},
                {"key": "step.status", "value": {"stringValue": step_status}},
                {"key": "cost.dollars", "value": {"doubleValue": dollars}},
            ],
            "status": {"code": span_status},
        }
        spans.append(step_span)

    # Child spans for verification checks
    verifications = trace_data.get("verifications", [])
    for idx, v in enumerate(verifications):
        v_check = v.get("check", f"check_{idx}")
        v_status = v.get("status", "fail")
        v_span_id = _hash_id(f"{root_span_id}:verify:{idx}:{v_check}", 16)
        
        attributes = [
            {"key": "gen_ai.system", "value": {"stringValue": "infini"}},
            {"key": "gen_ai.operation.name", "value": {"stringValue": "verify"}},
            {"key": "verify.check", "value": {"stringValue": v_check}},
            {"key": "verify.status", "value": {"stringValue": v_status}},
        ]
        conf = v.get("confidence")
        if conf is not None:
            attributes.append({"key": "verify.confidence", "value": {"doubleValue": float(conf)}})

        v_span = {
            "traceId": trace_id,
            "spanId": v_span_id,
            "parentSpanId": root_span_id,
            "name": f"verify {v_check}",
            "kind": "SPAN_KIND_INTERNAL",
            "startTimeUnixNano": root_end_nano - 100_000_000,
            "endTimeUnixNano": root_end_nano,
            "attributes": attributes,
            "status": {"code": "STATUS_CODE_OK" if v_status == "pass" else "STATUS_CODE_ERROR"},
        }
        spans.append(v_span)

    return {
        "resourceSpans": [
            {
                "resource": {
                    "attributes": [
                        {"key": "service.name", "value": {"stringValue": "infini"}},
                        {"key": "service.version", "value": {"stringValue": "0.2.0"}},
                        {"key": "telemetry.sdk.language", "value": {"stringValue": "python"}},
                        {"key": "telemetry.sdk.name", "value": {"stringValue": "opentelemetry"}},
                    ]
                },
                "scopeSpans": [
                    {
                        "scope": {
                            "name": "io.infini.tracer",
                            "version": "0.2.0",
                        },
                        "spans": spans,
                    }
                ],
            }
        ]
    }


def export_trace_to_otel_json(trace_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Load an INFINI trace JSON file and export to OpenTelemetry JSON format."""
    trace_path = Path(trace_path)
    output_path = Path(output_path)
    trace_data = json.loads(trace_path.read_text(encoding="utf-8"))
    otel_data = trace_to_otel(trace_data)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(otel_data, indent=2), encoding="utf-8")
    return otel_data
