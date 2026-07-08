#!/usr/bin/env python3
"""Run a Loopfile across multiple engines and generate a comparison table.

Usage:
    python scripts/run_benchmarks.py <loopfile>
"""
import sys
import subprocess
import json
from pathlib import Path

def run_engine(loopfile: str, engine: str) -> dict:
    print(f"Running on {engine}...")
    output_dir = f"runs/benchmarks/{engine}"
    cmd = [sys.executable, "-m", "infini", "run", loopfile, "--engine", engine, "--mock", "-o", output_dir, "--quiet"]
    
    # We want to capture the run.json
    try:
        subprocess.run(cmd, check=False, capture_output=True, text=True)
        trace_path = Path(output_dir) / "run.json"
        if trace_path.exists():
            return json.loads(trace_path.read_text())
    except subprocess.CalledProcessError as e:
        print(f"Error running {engine}: {e.stderr}")
    
    return {}

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/run_benchmarks.py <loopfile>")
        sys.exit(1)
        
    loopfile = sys.argv[1]
    engines = ["infini", "langgraph", "crewai"]
    
    results = {}
    for engine in engines:
        trace = run_engine(loopfile, engine)
        if trace:
            results[engine] = trace
            
    if not results:
        print("No traces generated.")
        sys.exit(1)
        
    print("\n# Engine Execution Comparison\n")
    print("| Metric | " + " | ".join(engines) + " |")
    print("|--------|" + "|".join(["---" for _ in engines]) + "|")
    
    # Compare basic stats
    def row(name, extractor):
        vals = [str(extractor(results[e])) if e in results else "N/A" for e in engines]
        print(f"| {name} | " + " | ".join(vals) + " |")
        
    row("Status", lambda t: t.get("outcome", "unknown"))
    row("Iterations", lambda t: t.get("iterations", 0))
    row("Steps Executed", lambda t: len(t.get("steps", [])))
    row("Cost ($)", lambda t: f"${t.get('budget', {}).get('spent_dollars', 0):.4f}")
    row("Time (m)", lambda t: f"{t.get('budget', {}).get('spent_minutes', 0):.1f}")
    
    # Verify trace structure parity
    print("\n## Parity Check\n")
    ref = results.get("infini", {})
    ref_keys = set(ref.keys())
    
    for engine in engines:
        if engine == "infini": continue
        if engine not in results: continue
        
        target_keys = set(results[engine].keys())
        if ref_keys == target_keys:
            print(f"- **{engine}**: ✅ Identical trace schema to reference engine")
        else:
            missing = ref_keys - target_keys
            extra = target_keys - ref_keys
            print(f"- **{engine}**: ❌ Schema mismatch. Missing: {missing}, Extra: {extra}")
            
if __name__ == "__main__":
    main()
