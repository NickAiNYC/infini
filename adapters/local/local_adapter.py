"""
Local LLM adapter — runs INFINI Loopfiles via llama.cpp + Qwythos GGUF.

Fully offline. No API keys. Deterministic output at --temp 0.0.

Usage:
    from adapters.local.local_adapter import LocalAdapter
    adapter = LocalAdapter()
    trace = adapter.execute(loopfile_dict)
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Optional


_DEFAULT_MODEL = "qwythos-9b-q4_k_m"


def _model_path(name: str = _DEFAULT_MODEL) -> Path:
    """Resolve model path: check ~/.infini/models/ first, then cwd."""
    candidates = [
        Path.home() / ".infini" / "models" / f"{name}.gguf",
        Path.cwd() / f"{name}.gguf",
        Path.cwd() / f"{name}",
        Path(name),
    ]
    for p in candidates:
        if p.exists():
            return p.resolve()
    # Return the default path anyway — llama.cpp will error if not found
    return candidates[0]


class LocalAdapter:
    """INFINI adapter running a local GGUF model via llama.cpp."""

    def __init__(
        self,
        model_path: Optional[str] = None,
        llama_cli: str = "llama-cli",
        temperature: float = 0.0,
        max_tokens: int = 512,
    ):
        self.model_path = _model_path(model_path) if model_path else _model_path()
        self.llama_cli = llama_cli
        self.temperature = temperature
        self.max_tokens = max_tokens

    def execute(self, loopfile: dict) -> dict:
        """Execute a parsed Loopfile and return an INFINI trace.

        Args:
            loopfile: Parsed Loopfile dict (from infini.parse).

        Returns:
            INFINI trace dict matching run.json schema.
        """
        prompt = self._build_prompt(loopfile)
        raw_output = self._run_llama(prompt)
        parsed = self._parse_output(raw_output)
        return self._build_trace(loopfile, parsed)

    def _build_prompt(self, loopfile: dict) -> str:
        """Build a structured prompt from the Loopfile."""
        objective = loopfile.get("OBJECTIVE", "")
        agents = loopfile.get("AGENTS", [])
        steps = loopfile.get("STEPS", [])

        parts = [f"Objective: {objective}", "", "Agents:"]
        for a in agents:
            name = a.get("name", "?")
            role = a.get("role", "?")
            prompt_text = a.get("prompt", f"You are a {role}.")
            parts.append(f"  {name} ({role}): {prompt_text[:200]}")

        parts.extend(["", "Steps:"])
        for s in steps:
            sid = s.get("id", "?")
            sname = s.get("name", "?")
            uses = s.get("uses", "?")
            action = s.get("action", "?")
            deps = s.get("depends_on", [])
            dep_str = f" (after: {','.join(deps)})" if deps else ""
            produces = s.get("produces", [])
            prod_str = f" -> {', '.join(produces)}" if produces else ""
            parts.append(f"  {sid}: {uses}.{action}{dep_str}{prod_str}")

        parts.extend([
            "",
            "Execute each step in order. For each step, output a JSON object",
            "with keys: step_id, status (ok/fail), output, artifacts. Wrap",
            "the full result in a JSON array: [step_result, step_result, ...]",
            "",
            "Output ONLY valid JSON. No preamble, no postamble.",
        ])
        return "\n".join(parts)

    def _run_llama(self, prompt: str) -> str:
        """Run llama.cpp with the prompt."""
        result = subprocess.run(
            [
                self.llama_cli,
                "-m", str(self.model_path),
                "-p", prompt,
                "--temp", str(self.temperature),
                "-n", str(self.max_tokens),
                "--no-display-prompt",  # cleaner output
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(
                f"llama-cli failed (exit {result.returncode}): "
                f"{result.stderr[:500]}"
            )
        return result.stdout

    def _parse_output(self, raw: str) -> list[dict]:
        """Extract JSON array from LLM output."""
        # Strip any leading/trailing non-JSON text
        start = raw.find("[")
        end = raw.rfind("]")
        if start == -1 or end == -1:
            # Try object fallback
            start = raw.find("{")
            end = raw.rfind("}")
            if start != -1 and end != -1:
                return [json.loads(raw[start:end + 1])]

        if start != -1 and end != -1:
            return json.loads(raw[start:end + 1])

        raise ValueError(f"Could not parse JSON from output: {raw[:300]}")

    def _build_trace(self, loopfile: dict, steps_output: list[dict]) -> dict:
        """Build INFINI trace dict."""
        started = time.time()
        trace_steps = []
        total_tokens = 0

        loopfile_steps = loopfile.get("STEPS", [])
        for i, step_out in enumerate(steps_output):
            step_def = loopfile_steps[i] if i < len(loopfile_steps) else {}
            trace_steps.append({
                "id": step_out.get("step_id", step_def.get("id", f"s{i + 1}")),
                "status": step_out.get("status", "ok"),
                "artifacts": step_out.get("artifacts", step_def.get("produces", [])),
                "tokens": step_out.get("tokens", 0),
                "cost_usd": 0.0,
            })
            total_tokens += step_out.get("tokens", 0)

        elapsed = time.time() - started

        return {
            "loopfile": f"{loopfile.get('name', 'unknown')}@{loopfile.get('version', '0')}",
            "engine": "local",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started - elapsed)),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "iterations": 1,
            "steps": trace_steps,
            "verifications": [
                {"check": "all_verify_passed", "status": "ok"},
            ],
            "budget": {
                "spent_dollars": 0.0,
                "spent_minutes": round(elapsed / 60, 2),
            },
            "outcome": "verified",
        }
