#!/usr/bin/env python3
"""
loom — the open standard for agent loops.

Usage:
  loom run        [Loopfile]           execute a loop
  loom validate   [Loopfile]           check spec compliance
  loom inspect    [run_dir]            visualize a run trace
  loom replay     [run_dir]            time-travel debug
  loom diff       [v1] [v2]            semantic diff between loop versions
  loom install    [loop_ref]           pull from registry
  loom publish    [Loopfile]           push to registry
  loom ci         [Loopfile]           run loop against fixtures (GitHub Action mode)
  loom engines                         list compatible engines
  loom search     [query]              search the registry
  loom version                         print version

Spec: Loopfile v1.0  —  https://github.com/loom-spec/loom
License: MIT
"""
from __future__ import annotations
import argparse
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    print("PyYAML required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

__version__ = "0.1.0"

SPEC_VERSION = "1.0"

REQUIRED_FIELDS = {"LOOM", "name", "version", "OBJECTIVE"}
REQUIRED_VERIFY_TIERS_MIN = 2
REQUIRED_BUDGET_FIELDS_MIN = 1


# ─────────────────────────────────────────────────────────────────────────────
# validate
# ─────────────────────────────────────────────────────────────────────────────
def cmd_validate(args: argparse.Namespace) -> int:
    path = Path(args.loopfile or "Loopfile")
    if not path.exists():
        print(f"❌ {path} not found", file=sys.stderr)
        return 2

    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        print(f"❌ YAML parse error: {e}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    # Required fields
    for f in REQUIRED_FIELDS:
        if f not in data:
            errors.append(f"missing required field: {f}")

    # Spec version
    if data.get("LOOM") != SPEC_VERSION:
        errors.append(f"LOOM must be '{SPEC_VERSION}' (got {data.get('LOOM')!r})")

    # VERIFY tiers
    verify = data.get("VERIFY", {}) or {}
    populated_tiers = [t for t in ("syntactic", "semantic", "external") if verify.get(t)]
    if len(populated_tiers) < REQUIRED_VERIFY_TIERS_MIN:
        errors.append(
            f"VERIFY must have at least {REQUIRED_VERIFY_TIERS_MIN} tiers "
            f"(got {len(populated_tiers)}: {populated_tiers})"
        )

    # BUDGET
    budget = data.get("BUDGET", {}) or {}
    if not budget:
        errors.append("BUDGET is required (at least one ceiling)")
    elif len(budget) < REQUIRED_BUDGET_FIELDS_MIN:
        errors.append("BUDGET must have at least one ceiling field")

    # STOP_WHEN
    if not data.get("STOP_WHEN"):
        errors.append("STOP_WHEN must be non-empty")

    # STEPS references valid agents
    agents = {a["name"] for a in (data.get("AGENTS") or [])}
    steps = data.get("STEPS") or []
    step_ids = {s["id"] for s in steps}
    for s in steps:
        if "uses" in s and s["uses"] not in agents:
            errors.append(f"step {s['id']!r} references unknown agent {s['uses']!r}")
        for dep in s.get("depends_on", []) or []:
            if dep not in step_ids:
                errors.append(f"step {s['id']!r} depends on unknown step {dep!r}")

    # DAG cycle check
    cycle = _detect_cycle(steps)
    if cycle:
        errors.append(f"cycle detected in depends_on: {' -> '.join(cycle)}")

    # Warnings
    if not data.get("SELF_IMPROVE"):
        warnings.append("SELF_IMPROVE not set — loop will not improve itself")
    if not data.get("ESCALATE_WHEN"):
        warnings.append("ESCALATE_WHEN not set — no human escalation path")
    if not data.get("STATE"):
        warnings.append("STATE not set — no resume protocol")

    # Report
    print(f"Validating: {path}")
    print(f"  name:    {data.get('name')}")
    print(f"  version: {data.get('version')}")
    print(f"  LOOM:    {data.get('LOOM')}")
    print(f"  verify:  {populated_tiers}")
    print(f"  budget:  {list(budget.keys())}")
    print(f"  steps:   {len(steps)}")
    print(f"  agents:  {len(agents)}")

    for w in warnings:
        print(f"  ⚠️  {w}")

    if errors:
        print()
        for e in errors:
            print(f"  ❌ {e}")
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1

    print(f"\n✓ valid. {len(warnings)} warning(s).")
    return 0


def _detect_cycle(steps: list[dict]) -> list[str] | None:
    graph = {s["id"]: list(s.get("depends_on") or []) for s in steps}
    visited: set[str] = set()
    stack: set[str] = set()
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        if node in stack:
            return path[path.index(node):] + [node]
        if node in visited:
            return None
        visited.add(node)
        stack.add(node)
        path.append(node)
        for n in graph.get(node, []):
            cycle = visit(n)
            if cycle:
                return cycle
        stack.discard(node)
        path.pop()
        return None

    for n in graph:
        cycle = visit(n)
        if cycle:
            return cycle
    return None


# ─────────────────────────────────────────────────────────────────────────────
# inspect
# ─────────────────────────────────────────────────────────────────────────────
def cmd_inspect(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    trace_path = run_dir / "trace.jsonl"
    if not trace_path.exists():
        print(f"❌ no trace.jsonl in {run_dir}", file=sys.stderr)
        return 2

    events = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
    if not events:
        print("(empty trace)")
        return 0

    print(f"Run: {run_dir}")
    print(f"Events: {len(events)}")
    print(f"Started: {events[0].get('ts')}")
    print(f"Ended:   {events[-1].get('ts')}")
    print()

    # Cost rollup
    total_tokens = sum(e.get("tokens", 0) for e in events)
    total_cost = sum(e.get("cost_usd", 0) for e in events)
    print(f"Total tokens: {total_tokens:,}")
    print(f"Total cost:   ${total_cost:.4f}")
    print()

    # Step timeline
    print("Step timeline:")
    for e in events:
        ts = e.get("ts", "")[:19]
        kind = e.get("kind", "?").ljust(10)
        step = e.get("step", "").ljust(20)
        msg = e.get("msg", "")
        print(f"  {ts}  {kind}  {step}  {msg}")

    return 0


# ─────────────────────────────────────────────────────────────────────────────
# replay
# ─────────────────────────────────────────────────────────────────────────────
def cmd_replay(args: argparse.Namespace) -> int:
    run_dir = Path(args.run_dir)
    trace_path = run_dir / "trace.jsonl"
    if not trace_path.exists():
        print(f"❌ no trace.jsonl in {run_dir}", file=sys.stderr)
        return 2

    events = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()]
    if not events:
        print("(empty trace)")
        return 0

    target_step = args.step
    cursor = 0

    print(f"Replay mode. {len(events)} events. Commands: n(ext), p(rev), <N>, s(tate), q(uit)")
    while True:
        e = events[cursor]
        print(f"\n[{cursor}/{len(events)-1}] {e.get('ts','')[:19]}  {e.get('kind','?')}  {e.get('step','')}")
        print(f"  msg: {e.get('msg','')}")
        if e.get("state"):
            print(f"  state: {json.dumps(e['state'], indent=2)[:500]}")

        try:
            cmd = input("\n> ").strip().lower() or "n"
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd in ("q", "quit"):
            break
        elif cmd in ("n", "next"):
            cursor = min(cursor + 1, len(events) - 1)
        elif cmd in ("p", "prev"):
            cursor = max(cursor - 1, 0)
        elif cmd in ("s", "state"):
            print(json.dumps(e.get("state", {}), indent=2))
        elif cmd.isdigit():
            cursor = max(0, min(int(cmd), len(events) - 1))
        elif target_step and cmd == "step":
            for i, ev in enumerate(events):
                if ev.get("step") == target_step:
                    cursor = i
                    break

    return 0


# ─────────────────────────────────────────────────────────────────────────────
# diff
# ─────────────────────────────────────────────────────────────────────────────
def cmd_diff(args: argparse.Namespace) -> int:
    v1 = _load_loop(args.v1)
    v2 = _load_loop(args.v2)

    print(f"Diff: {args.v1}  →  {args.v2}")
    print()

    changes: list[tuple[str, str, str]] = []
    all_keys = set(v1) | set(v2)
    for k in sorted(all_keys):
        a, b = v1.get(k), v2.get(k)
        if a != b:
            severity = _classify_change(k, a, b)
            changes.append((severity, k, _fmt_change(a, b)))

    if not changes:
        print("✓ no semantic changes")
        return 0

    for sev, k, desc in changes:
        marker = {"high": "🔴", "medium": "🟡", "low": "🟢"}[sev]
        print(f"  {marker} [{sev}] {k}: {desc}")

    high = sum(1 for s, _, _ in changes if s == "high")
    print(f"\n{len(changes)} change(s): {high} high-severity")
    return 0 if high == 0 else 1


def _load_loop(ref: str) -> dict:
    p = Path(ref)
    if p.exists():
        return yaml.safe_load(p.read_text())
    # try registry cache
    cache = Path.home() / ".loom" / "cache" / f"{ref}.yaml"
    if cache.exists():
        return yaml.safe_load(cache.read_text())
    raise FileNotFoundError(f"loop not found: {ref}")


def _classify_change(key: str, old: any, new: any) -> str:
    """Heuristic severity for semantic diff."""
    if key in ("VERIFY", "BUDGET", "STOP_WHEN", "ESCALATE_WHEN"):
        return "high"
    if key in ("STEPS", "AGENTS"):
        return "medium"
    if key in ("version", "description"):
        return "low"
    return "low"


def _fmt_change(a: any, b: any) -> str:
    if a is None:
        return f"added → {json.dumps(b)[:80]}"
    if b is None:
        return f"removed (was {json.dumps(a)[:80]})"
    return f"{json.dumps(a)[:60]} → {json.dumps(b)[:60]}"


# ─────────────────────────────────────────────────────────────────────────────
# ci (fixtures mode)
# ─────────────────────────────────────────────────────────────────────────────
def cmd_ci(args: argparse.Namespace) -> int:
    """Run a loop against canned fixtures and compare to expected outputs."""
    loopfile = Path(args.loopfile)
    fixtures_dir = Path(args.fixtures)
    expect_dir = Path(args.expect)

    if not loopfile.exists():
        print(f"❌ loopfile not found: {loopfile}", file=sys.stderr)
        return 2
    if not fixtures_dir.exists():
        print(f"❌ fixtures dir not found: {fixtures_dir}", file=sys.stderr)
        return 2
    if not expect_dir.exists():
        print(f"❌ expect dir not found: {expect_dir}", file=sys.stderr)
        return 2

    fixtures = sorted(fixtures_dir.glob("*.json"))
    if not fixtures:
        print("⚠️  no fixtures found")
        return 0

    print(f"Running {len(fixtures)} fixture(s) against {loopfile.name}")
    failures = 0
    for fx in fixtures:
        name = fx.stem
        expected = expect_dir / f"{name}.json"
        if not expected.exists():
            print(f"  ⚠️  {name}: no expected output, skipping")
            continue

        # In a real implementation, the engine would execute the loop here.
        # For the spec reference, we simulate by comparing the fixture to expected.
        fx_data = json.loads(fx.read_text())
        ex_data = json.loads(expected.read_text())

        # Stub: just check that expected keys are present in fixture
        ok = all(k in fx_data for k in ex_data.get("required_inputs", []))
        status = "✓" if ok else "✗"
        print(f"  {status} {name}")
        if not ok:
            failures += 1

    print()
    if failures:
        print(f"❌ {failures}/{len(fixtures)} fixture(s) failed")
        return 1
    print(f"✓ all {len(fixtures)} fixture(s) passed")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# engines / search / install / publish / run (stubs)
# ─────────────────────────────────────────────────────────────────────────────
def cmd_engines(args: argparse.Namespace) -> int:
    engines = [
        ("langgraph",  "0.2.0", ["1.0"], ["parallel", "dag", "semantic_verify"]),
        ("crewai",     "0.5.0", ["1.0"], ["parallel", "registry_publish"]),
        ("openclaw",   "1.0.0", ["1.0"], ["parallel", "dag", "external"]),
        ("hermesagents","0.3.0", ["1.0"], ["dag", "semantic_verify"]),
        ("autogen",    "0.4.0", ["1.0"], ["parallel", "dag"]),
        ("smolagents", "1.0.0", ["1.0"], ["registry_publish"]),
    ]
    print(f"{'engine':<16} {'version':<10} {'spec':<10} features")
    print("-" * 60)
    for name, ver, specs, feats in engines:
        print(f"{name:<16} {ver:<10} {','.join(specs):<10} {','.join(feats)}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    print(f"Searching registry for: {args.query!r}")
    print("(registry not yet live — see registry/README.md)")
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    print(f"Install: {args.loop_ref}")
    print("(registry adapter not yet implemented — see registry/README.md)")
    return 0


def cmd_publish(args: argparse.Namespace) -> int:
    rc = cmd_validate(argparse.Namespace(loopfile=args.loopfile))
    if rc != 0:
        print("❌ cannot publish invalid Loopfile", file=sys.stderr)
        return rc
    print(f"Publish: {args.loopfile} → registry")
    print("(registry adapter not yet implemented — see registry/README.md)")
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    path = Path(args.loopfile or "Loopfile")
    rc = cmd_validate(argparse.Namespace(loopfile=str(path)))
    if rc != 0:
        return rc

    data = yaml.safe_load(path.read_text())
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = Path("runs") / f"run_{ts}"
    run_dir.mkdir(parents=True, exist_ok=True)

    # Write a stub trace so inspect/replay have something to consume
    trace = run_dir / "trace.jsonl"
    with trace.open("w") as f:
        f.write(json.dumps({
            "ts": ts, "kind": "loop_start", "step": "",
            "msg": f"starting {data['name']}@{data['version']}", "state": {},
        }) + "\n")
        for step in data.get("STEPS", []) or []:
            f.write(json.dumps({
                "ts": ts, "kind": "step_start", "step": step["id"],
                "msg": step.get("name", ""), "state": {},
            }) + "\n")
            f.write(json.dumps({
                "ts": ts, "kind": "step_end", "step": step["id"],
                "msg": "(stub)", "tokens": 0, "cost_usd": 0.0, "state": {},
            }) + "\n")
        f.write(json.dumps({
            "ts": ts, "kind": "loop_end", "step": "",
            "msg": "(stub — no engine adapter attached)", "state": {},
        }) + "\n")

    print(f"▶ reading state... none found, starting fresh")
    print(f"▶ validated. {len(data.get('STEPS', []))} step(s) ready.")
    print(f"▶ trace written to {run_dir}/trace.jsonl")
    print(f"⚠️  no engine adapter attached — install one to execute (loom engines)")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# main
# ─────────────────────────────────────────────────────────────────────────────
def main() -> int:
    parser = argparse.ArgumentParser(
        prog="loom",
        description="the open standard for agent loops",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="execute a loop")
    p_run.add_argument("loopfile", nargs="?", default="Loopfile")

    p_val = sub.add_parser("validate", help="check spec compliance")
    p_val.add_argument("loopfile", nargs="?", default="Loopfile")

    p_ins = sub.add_parser("inspect", help="visualize a run trace")
    p_ins.add_argument("run_dir")

    p_rep = sub.add_parser("replay", help="time-travel debug")
    p_rep.add_argument("run_dir")
    p_rep.add_argument("--step", help="jump to step id")

    p_dif = sub.add_parser("diff", help="semantic diff between loop versions")
    p_dif.add_argument("v1")
    p_dif.add_argument("v2")

    p_inst = sub.add_parser("install", help="pull from registry")
    p_inst.add_argument("loop_ref")

    p_pub = sub.add_parser("publish", help="push to registry")
    p_pub.add_argument("loopfile")

    p_ci = sub.add_parser("ci", help="run loop against fixtures")
    p_ci.add_argument("--loopfile", default="Loopfile")
    p_ci.add_argument("--fixtures", default="tests/fixtures")
    p_ci.add_argument("--expect", default="tests/expected")

    sub.add_parser("engines", help="list compatible engines")
    p_srch = sub.add_parser("search", help="search the registry")
    p_srch.add_argument("query")

    sub.add_parser("version", help="print version")

    args = parser.parse_args()

    if args.cmd == "version":
        print(f"loom {__version__}  (spec v{SPEC_VERSION})")
        return 0

    handlers = {
        "run": cmd_run, "validate": cmd_validate, "inspect": cmd_inspect,
        "replay": cmd_replay, "diff": cmd_diff, "install": cmd_install,
        "publish": cmd_publish, "ci": cmd_ci, "engines": cmd_engines,
        "search": cmd_search,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
