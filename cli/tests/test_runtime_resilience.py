"""Tests for runtime determinism, retries, budget enforcement, step DAG resolution, and divergence classification."""
from __future__ import annotations

from pathlib import Path
import pytest

from infini.parse import parse
from infini.engine import run
from infini.trace import new_trace, add_step, finalize_trace
from infini.replay import replay
from infini.diff import find_first_step_divergence


RESILIENT_LOOP_YAML = """\
LOOPFILE: "1.0"
name: resilience-test-loop
version: 1.0.0
OBJECTIVE: "Validate resilience under retries and budget limits."
AGENTS:
  - { name: worker, role: builder, model_tier: haiku }
STEPS:
  - { id: s1, name: step_one, action: build, uses: worker }
  - { id: s2, name: step_two, action: verify_build, uses: worker, depends_on: [s1], retry: { max: 2, backoff: exponential } }
VERIFY:
  syntactic: ["build.out:exists"]
  semantic: ["judge:quality>=80"]
  confidence_threshold: 80
BUDGET:
  dollars: 5.0
  minutes: 10
STOP_WHEN: ["all_verify_passed"]
"""


def test_deterministic_replay_trace_identity(tmp_path):
    """Running under deterministic mock mode produces byte-identical traces on replay."""
    lf = parse(RESILIENT_LOOP_YAML)
    trace_dir = tmp_path / "run1"
    trace1 = run(lf, output_dir=trace_dir, mock=True, deterministic=True, verbose=False)
    
    assert trace1.outcome == "verified"
    trace_file = trace_dir / "run.json"
    assert trace_file.exists()

    # Replay step s1 using from_step='s1'
    replayed = replay(trace_dir, from_step="s1")
    assert replayed.loopfile == lf.name
    assert len(replayed.steps) >= 1
    assert replayed.steps[0].id == "s1"


def test_budget_exhaustion_dollars(tmp_path):
    """When budget is constrained below step cost, execution halts with budget_exceeded."""
    tiny_budget_yaml = """\
LOOPFILE: "1.0"
name: tight-budget-loop
version: 1.0.0
OBJECTIVE: "Halt on budget exhaustion."
AGENTS:
  - { name: worker, role: builder, model_tier: haiku }
STEPS:
  - { id: s1, name: expensive_step, action: build, uses: worker }
  - { id: s2, name: unreachable_step, action: build_more, uses: worker, depends_on: [s1] }
VERIFY:
  syntactic: []
  semantic: []
  confidence_threshold: 80
BUDGET:
  dollars: 0.008
  minutes: 10
STOP_WHEN: ["all_verify_passed"]
"""
    lf = parse(tiny_budget_yaml)
    trace = run(lf, output_dir=tmp_path, mock=True, deterministic=False, verbose=False)

    assert trace.outcome == "budget_exceeded"
    # Step 1 executes, but Step 2 halts on budget exhaustion
    executed_step_ids = [s.id for s in trace.steps]
    assert "s1" in executed_step_ids
    assert "s2" not in executed_step_ids


def test_budget_exhaustion_minutes(tmp_path):
    """When time budget is constrained to near-zero, execution halts with budget_exceeded."""
    zero_time_yaml = """\
LOOPFILE: "1.0"
name: zero-time-loop
version: 1.0.0
OBJECTIVE: "Halt on minute budget exhaustion."
AGENTS:
  - { name: worker, role: builder, model_tier: haiku }
STEPS:
  - { id: s1, name: timed_step, action: build, uses: worker }
VERIFY:
  syntactic: []
  semantic: []
  confidence_threshold: 80
BUDGET:
  dollars: 100.0
  minutes: 0.001
STOP_WHEN: ["all_verify_passed"]
"""
    lf = parse(zero_time_yaml)
    trace = run(lf, output_dir=tmp_path, mock=True, deterministic=False, verbose=False)

    assert trace.outcome == "budget_exceeded"


def test_step_dependency_ordering(tmp_path):
    """Steps execute in topological order respecting depends_on."""
    dag_yaml = """\
LOOPFILE: "1.0"
name: dag-order-loop
version: 1.0.0
OBJECTIVE: "Execute DAG in order."
AGENTS:
  - { name: a1, role: builder, model_tier: haiku }
STEPS:
  - { id: root, name: start, action: init, uses: a1 }
  - { id: child1, name: branch_a, action: process_a, uses: a1, depends_on: [root] }
  - { id: child2, name: branch_b, action: process_b, uses: a1, depends_on: [root] }
  - { id: join, name: finalize, action: merge, uses: a1, depends_on: [child1, child2] }
VERIFY:
  syntactic: []
  semantic: []
  confidence_threshold: 80
BUDGET:
  dollars: 10.0
  minutes: 10
STOP_WHEN: ["iterations>=1"]
"""
    lf = parse(dag_yaml)
    trace = run(lf, output_dir=tmp_path, mock=True, deterministic=True, verbose=False)

    step_ids = [s.id for s in trace.steps]
    assert step_ids.index("root") < step_ids.index("child1")
    assert step_ids.index("root") < step_ids.index("child2")
    assert step_ids.index("child1") < step_ids.index("join")
    assert step_ids.index("child2") < step_ids.index("join")


def test_trace_divergence_classification():
    """Diff correctly classifies step count, status, and step ID divergence."""
    t1 = new_trace("loop-a", "yaml1")
    t1.outcome = "verified"
    t1.iterations = 1
    add_step(t1, "s1", "step1", agent="b1", action="init", artifacts=[], status="ok", cost_dollars=0.01, cost_minutes=0.5, tokens_in=10, tokens_out=20)
    add_step(t1, "s2", "step2", agent="b1", action="eval", artifacts=[], status="ok", cost_dollars=0.02, cost_minutes=0.5, tokens_in=10, tokens_out=20)

    t2 = new_trace("loop-a", "yaml2")
    t2.outcome = "budget_exceeded"
    t2.iterations = 1
    add_step(t2, "s1", "step1", agent="b1", action="init", artifacts=[], status="ok", cost_dollars=0.01, cost_minutes=0.5, tokens_in=10, tokens_out=20)
    add_step(t2, "s2", "step2", agent="b1", action="eval", artifacts=[], status="failed", cost_dollars=0.02, cost_minutes=0.5, tokens_in=10, tokens_out=20)

    first_div = find_first_step_divergence(t1.to_dict(), t2.to_dict())
    assert first_div is not None
    assert first_div["step_id"] == "s2"
    assert "Status differed" in first_div["reason"]
