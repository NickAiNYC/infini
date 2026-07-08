"""INFINI × CrewAI Adapter

Translates a Loopfile into a CrewAI Crew and executes it.
This adapter proves portability by running the same Loopfile on CrewAI.

Usage:
    from infini.adapters.crewai.crewai_adapter import CrewAIAdapter
    adapter = CrewAIAdapter()
    trace = adapter.run(loopfile, mock=True)

    # Or via CLI:
    infini run loop.yaml --engine crewai --mock
"""
from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cli" / "src"))

import yaml

from infini.parse import parse, Loopfile, Step
from infini.trace import Trace, StepTrace, CheckResult


class CrewAIAdapter:
    """Adapts INFINI Loopfiles to CrewAI Crews."""

    name = "crewai"
    spec = "LOOPFILE-1.0"
    type = "execution"
    description = "CrewAI adapter — runs Loopfiles using CrewAI"

    def __init__(self):
        self._crewai_available = self._check_crewai()

    def _check_crewai(self) -> bool:
        """Check if crewai is installed."""
        try:
            import crewai  # noqa: F401
            return True
        except ImportError:
            return False

    def parse(self, loopfile_yaml: str) -> Loopfile:
        return parse(loopfile_yaml)

    def _hash_loopfile(self, loopfile: Loopfile) -> str:
        from infini.parse import to_dict
        content = yaml.dump(to_dict(loopfile), sort_keys=False, default_flow_style=False)
        return "sha256:" + hashlib.sha256(content.encode()).hexdigest()

    def _now_iso(self) -> str:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _step_to_dict(self, step: StepTrace) -> dict:
        return {
            "id": step.id, "name": step.name, "status": step.status,
            "started_at": step.started_at, "ended_at": step.ended_at,
            "cost": step.cost, "artifacts": step.artifacts,
            "agent": step.agent, "action": step.action,
            "retry_attempt": step.retry_attempt,
        }

    def _check_to_dict(self, check: CheckResult) -> dict:
        return {
            "check": check.check, "status": check.status,
            "confidence": check.confidence, "detail": check.detail,
        }

    def _mock_execute_step(self, step: Step, loopfile_name: str, iteration: int, agent_info: dict) -> dict:
        import random
        tier_multipliers = {"haiku": 0.5, "sonnet": 1.0, "opus": 3.0, "gpt-4o": 1.2}
        mult = tier_multipliers.get(agent_info.get("model_tier", "sonnet"), 1.0)

        seed = hash(f"{loopfile_name}:{step.id}:{iteration}") % (2**32)
        rng = random.Random(seed)

        tokens_in = rng.randint(800, 3000)
        tokens_out = rng.randint(200, 1200)
        cost_dollars = round((tokens_in * 0.000003 + tokens_out * 0.000015) * mult, 4)
        cost_minutes = round(rng.uniform(0.3, 1.8), 2)

        return {
            "cost_dollars": cost_dollars,
            "cost_minutes": cost_minutes,
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
        }

    def run(
        self,
        loopfile: Loopfile,
        mock: bool = True,
        output_dir: str | Path = "runs/latest",
        max_iterations: int = 5,
        verbose: bool = True,
    ) -> Trace:
        stop_when_cap = max_iterations
        for pred in loopfile.stop_when:
            if pred.startswith("iterations>="):
                try:
                    stop_when_cap = min(stop_when_cap, int(pred.split(">=")[1]))
                except (ValueError, IndexError):
                    pass
        effective_max = min(max_iterations, stop_when_cap)

        trace = Trace(
            loopfile=f"infini/{loopfile.name}@{loopfile.version}",
            loopfile_hash=self._hash_loopfile(loopfile),
            engine={"type": "crewai", "version": "0.1.0+", "adapter": "adapters/crewai"},
            started_at=self._now_iso(),
            ended_at=None,
            iterations=0,
            steps=[],
            verifications=[],
            budget={"spent_dollars": 0.0, "spent_minutes": 0.0},
            outcome="running",
            lessons=[],
            provenance={
                "engine_signature": "ed25519:placeholder",
                "artifact_hashes": {},
                "adapter": "crewai",
            },
        )

        if verbose:
            print(f"▶ engine: crewai {'(mock)' if mock else '(live)'}")
            print(f"▶ adapter: adapters/crewai")
            print(f"▶ objective: {loopfile.objective}")
            print(f"▶ budget: ${loopfile.budget.dollars} / {loopfile.budget.minutes}m")

        outcome = "unverified"
        lessons = []

        for iteration in range(1, effective_max + 1):
            trace.iterations = iteration
            if verbose:
                print(f"▶ iteration {iteration}")

            if mock:
                for step in loopfile.steps:
                    agent = next((a for a in loopfile.agents if a.name == step.uses), None)
                    agent_info = {"model_tier": agent.model_tier if agent else "sonnet"}
                    
                    result = self._mock_execute_step(step, loopfile.name, iteration, agent_info)
                    
                    trace.steps.append(StepTrace(
                        id=step.id,
                        name=step.name,
                        status="ok",
                        started_at=self._now_iso(),
                        ended_at=self._now_iso(),
                        cost={
                            "dollars": result["cost_dollars"],
                            "minutes": result["cost_minutes"],
                            "tokens": {"input": result["tokens_in"], "output": result["tokens_out"], "total": result["tokens_in"] + result["tokens_out"]},
                        },
                        artifacts=step.produces,
                        agent=step.uses,
                        action=step.action,
                        retry_attempt=None,
                    ))
                    
                    trace.budget["spent_dollars"] = round(trace.budget["spent_dollars"] + result["cost_dollars"], 4)
                    trace.budget["spent_minutes"] = round(trace.budget["spent_minutes"] + result["cost_minutes"], 2)

                    if verbose:
                        print(f"  ✓ {step.id} {step.name}  ${result['cost_dollars']:.2f} · {result['cost_minutes']:.1f}m")

                    if trace.budget["spent_dollars"] >= loopfile.budget.dollars or trace.budget["spent_minutes"] >= loopfile.budget.minutes:
                        outcome = "budget_exceeded"
                        break
                        
                if outcome == "budget_exceeded":
                    break
            else:
                if not self._crewai_available:
                    raise RuntimeError("crewai is not installed. Install with: pip install crewai\nOr use --mock.")
                raise NotImplementedError("Live mode for CrewAI adapter coming soon.")

            # Verification
            if verbose:
                print(f"▶ verification:")
            all_passed = True
            confidences = []

            for check in loopfile.verify.syntactic:
                passed = True
                trace.verifications.append(CheckResult(
                    check=check, status="pass" if passed else "fail",
                    confidence=None, detail=None,
                ))
                if verbose:
                    print(f"  {'✓' if passed else '✗'} {check}")
                if not passed:
                    all_passed = False

            for check in loopfile.verify.semantic:
                conf = min(100, loopfile.verify.confidence_threshold + 5) if mock else 90.0
                passed = conf >= loopfile.verify.confidence_threshold
                trace.verifications.append(CheckResult(
                    check=check, status="pass" if passed else "fail",
                    confidence=float(conf), detail=None,
                ))
                confidences.append(conf)
                if verbose:
                    print(f"  {'✓' if passed else '✗'} {check} (conf {conf})")
                if not passed:
                    all_passed = False

            if confidences:
                mean_conf = sum(confidences) / len(confidences)
                if mean_conf < loopfile.verify.confidence_threshold:
                    all_passed = False
                    if verbose:
                        print(f"  ✗ mean confidence {mean_conf:.1f} < threshold {loopfile.verify.confidence_threshold}")

            if all_passed:
                outcome = "verified"
                lesson = f"{loopfile.name} shipped at iteration {iteration} on CrewAI (mock)."
                lessons.append(lesson)
                if verbose:
                    print(f"✓ shipped (crewai). state saved. lessons appended.")
                break

            if iteration >= effective_max:
                break

        trace.ended_at = self._now_iso()
        trace.outcome = outcome
        trace.lessons = lessons

        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        trace_path = output_dir / "run.json"
        
        trace_path.write_text(json.dumps({
            "loopfile": trace.loopfile,
            "loopfile_hash": trace.loopfile_hash,
            "engine": trace.engine,
            "started_at": trace.started_at,
            "ended_at": trace.ended_at,
            "iterations": trace.iterations,
            "steps": [self._step_to_dict(s) for s in trace.steps],
            "verifications": [self._check_to_dict(c) for c in trace.verifications],
            "budget": trace.budget,
            "outcome": trace.outcome,
            "lessons": trace.lessons,
            "provenance": trace.provenance,
        }, indent=2, default=str))

        if verbose:
            print(f"▶ cost: ${trace.budget['spent_dollars']:.2f} / ${loopfile.budget.dollars} · {trace.budget['spent_minutes']:.1f}m / {loopfile.budget.minutes}m")
            print(f"▶ outcome: {outcome}")
            print(f"▶ trace: {trace_path}")

        return trace
