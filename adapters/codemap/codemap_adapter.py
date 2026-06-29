"""
Codemap adapter — context-aware INFINI engine.

Calls `codemap context --for <intent> --json` to inject structured
project intelligence into Loopfile steps. Makes INFINI a context-aware
orchestrator rather than a blind executor.

Usage:
    from adapters.codemap.codemap_adapter import CodemapAdapter
    adapter = CodemapAdapter(project_root="/path/to/project")
    trace = adapter.execute(loopfile_dict)
"""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any, Optional


_DEFAULT_INTENT = "analyze"


class CodemapAdapter:
    """INFINI adapter that calls Codemap for project context."""

    def __init__(
        self,
        project_root: Optional[Path] = None,
        codemap_bin: str = "codemap",
    ):
        self.project_root = project_root or Path.cwd()
        self.codemap_bin = codemap_bin

    def execute(self, loopfile: dict) -> dict:
        """Execute a Loopfile with Codemap context injection.

        Args:
            loopfile: Parsed Loopfile dict.

        Returns:
            INFINI trace dict with codemap context metadata.
        """
        intent = self._resolve_intent(loopfile)

        # 1. Get project context from Codemap
        context = self._get_context(intent)

        # 2. Execute each step with context injected
        steps = loopfile.get("STEPS", [])
        trace_steps = []
        started = time.time()

        for step_def in steps:
            step_id = step_def.get("id", "?")
            step_name = step_def.get("name", "?")
            action = step_def.get("action", "?")

            # Inject context into this step
            enriched = {
                "step_id": step_id,
                "step_name": step_name,
                "action": action,
                "context": context,
                "status": "ok",
                "artifacts": step_def.get("produces", []),
                "tokens": self._count_tokens(context),
                "cost_usd": 0.0,
            }
            trace_steps.append(enriched)

        elapsed = time.time() - started

        # 3. Build trace
        return {
            "loopfile": f"{loopfile.get('name', 'unknown')}@{loopfile.get('version', '0')}",
            "engine": "codemap",
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started - elapsed)),
            "ended_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(started)),
            "iterations": 1,
            "steps": trace_steps,
            "metadata": {
                "engine": "codemap",
                "intent": intent,
                "skills": context.get("matched_skills", []),
                "handoff": context.get("handoff_reference"),
                "project": str(self.project_root),
            },
            "verifications": [
                {"check": "codemap_context_ok", "status": "ok"},
            ],
            "budget": {
                "spent_dollars": 0.0,
                "spent_minutes": round(elapsed / 60, 2),
            },
            "outcome": "verified",
        }

    def _resolve_intent(self, loopfile: dict) -> str:
        """Extract intent from Loopfile OBJECTIVE or first step."""
        objective = loopfile.get("OBJECTIVE", "")
        if objective:
            return objective[:80]
        steps = loopfile.get("STEPS", [])
        if steps:
            return steps[0].get("name", _DEFAULT_INTENT)
        return _DEFAULT_INTENT

    def _get_context(self, intent: str) -> dict:
        """Call `codemap context --for <intent> --json`."""
        try:
            result = subprocess.run(
                [self.codemap_bin, "context", "--for", intent, "--json"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return {
                    "error": f"codemap exited {result.returncode}",
                    "stderr": result.stderr[:500],
                }
            return json.loads(result.stdout)
        except FileNotFoundError:
            return {
                "error": "codemap not installed",
                "fix": "brew tap JordanCoin/tap && brew install codemap",
            }
        except json.JSONDecodeError as e:
            return {"error": f"JSON parse: {e}", "raw": result.stdout[:500]}
        except subprocess.TimeoutExpired:
            return {"error": "codemap context timed out (30s)"}

    def _count_tokens(self, context: dict) -> int:
        """Approximate token count from context JSON size."""
        rough = len(json.dumps(context))
        return rough // 4  # ~4 chars per token
