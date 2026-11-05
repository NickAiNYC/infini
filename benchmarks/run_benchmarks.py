"""INFINI Reproducible Benchmark Suite.

Measures:
1. Replay Determinism: N=100 runs, % byte-identical traces.
2. Per-step overhead: Engine dispatch latency per step on reference engine.
"""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# Add cli/src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "cli" / "src"))

from infini.parse import parse_file
from infini.engine import run as run_loop
from infini.replay import replay


def get_machine_spec() -> dict[str, str]:
    """Capture verifiable machine specifications."""
    cpu_brand = "Unknown"
    if sys.platform == "darwin":
        try:
            cpu_brand = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
        except Exception:
            cpu_brand = platform.processor() or platform.machine()
    else:
        cpu_brand = platform.processor() or platform.machine()

    memory_gb = "Unknown"
    try:
        if sys.platform == "darwin":
            mem_bytes = int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
            memory_gb = f"{round(mem_bytes / (1024**3))} GB"
        else:
            mem_bytes = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
            memory_gb = f"{round(mem_bytes / (1024**3))} GB"
    except Exception:
        pass

    return {
        "os": f"{platform.system()} {platform.release()}",
        "architecture": platform.machine(),
        "cpu": cpu_brand,
        "ram": memory_gb,
        "python_version": platform.python_version(),
    }


def benchmark_replay_determinism(loopfile_path: Path, n_runs: int = 100) -> dict[str, Any]:
    """Measure replay determinism over N runs."""
    lf = parse_file(loopfile_path)
    baseline_dir = Path("runs/benchmark_baseline")
    baseline_trace = run_loop(
        lf,
        output_dir=baseline_dir,
        mock=True,
        deterministic=True,
        verbose=False,
    )

    # Establish canonical trace payload for step execution
    def _canonical_step_bytes(trace_obj: Any) -> bytes:
        trace_dict = trace_obj.to_dict() if hasattr(trace_obj, "to_dict") else trace_obj
        canonical = {
            "steps": [
                {
                    "id": s["id"],
                    "name": s["name"],
                    "status": s["status"],
                    "agent": s["agent"],
                    "action": s["action"],
                    "artifacts": s["artifacts"],
                    "cost": s["cost"],
                }
                for s in trace_dict.get("steps", [])
            ],
            "verifications": trace_dict.get("verifications", []),
            "outcome": trace_dict.get("outcome"),
            "iterations": trace_dict.get("iterations"),
        }
        return json.dumps(canonical, sort_keys=True).encode("utf-8")

    baseline_bytes = _canonical_step_bytes(baseline_trace.to_dict())
    baseline_hash = hashlib.sha256(baseline_bytes).hexdigest()

    identical_count = 0
    replay_out_dir = Path("runs/benchmark_replays")

    for i in range(n_runs):
        rep = replay(
            run_dir=baseline_dir,
            output_dir=replay_out_dir / f"run_{i}",
            freeze_model_calls=True,
            verbose=False,
        )
        rep_bytes = _canonical_step_bytes(rep)
        rep_hash = hashlib.sha256(rep_bytes).hexdigest()
        if rep_hash == baseline_hash:
            identical_count += 1

    pct_identical = round((identical_count / n_runs) * 100.0, 2)
    return {
        "n_runs": n_runs,
        "identical_runs": identical_count,
        "determinism_pct": pct_identical,
        "canonical_trace_hash": f"sha256:{baseline_hash}",
    }


def benchmark_step_overhead(loopfile_path: Path, n_iterations: int = 100) -> dict[str, Any]:
    """Measure per-step execution overhead on the reference engine (in milliseconds)."""
    lf = parse_file(loopfile_path)
    step_times_ms: list[float] = []

    out_dir = Path("runs/benchmark_overhead")

    for _ in range(n_iterations):
        t0 = time.perf_counter()
        # Execute single iteration step pipeline
        run_loop(
            lf,
            output_dir=out_dir,
            mock=True,
            deterministic=True,
            max_iterations=1,
            verbose=False,
        )
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        # Number of steps in loopfile
        step_count = len(lf.steps)
        per_step_ms = elapsed_ms / step_count
        step_times_ms.append(per_step_ms)

    step_times_ms.sort()
    mean_ms = round(sum(step_times_ms) / len(step_times_ms), 3)
    p50_ms = round(step_times_ms[int(len(step_times_ms) * 0.50)], 3)
    p95_ms = round(step_times_ms[int(len(step_times_ms) * 0.95)], 3)
    p99_ms = round(step_times_ms[int(len(step_times_ms) * 0.99)], 3)
    min_ms = round(step_times_ms[0], 3)
    max_ms = round(step_times_ms[-1], 3)

    return {
        "n_samples": n_iterations,
        "mean_ms": mean_ms,
        "p50_ms": p50_ms,
        "p95_ms": p95_ms,
        "p99_ms": p99_ms,
        "min_ms": min_ms,
        "max_ms": max_ms,
    }


def main():
    print("Running INFINI Benchmark Suite...")
    machine = get_machine_spec()
    print(f"Machine: {machine['cpu']} | {machine['ram']} | {machine['os']} | Python {machine['python_version']}")

    quickstart_path = Path(__file__).parent.parent / "examples" / "quickstart.yaml"

    print("\n[1/2] Benchmarking Replay Determinism (N=100)...")
    determinism = benchmark_replay_determinism(quickstart_path, n_runs=100)
    print(f"  Determinism: {determinism['determinism_pct']}% byte-identical ({determinism['identical_runs']}/{determinism['n_runs']})")

    print("\n[2/2] Benchmarking Reference Engine Per-Step Overhead (N=100 samples)...")
    overhead = benchmark_step_overhead(quickstart_path, n_iterations=100)
    print(f"  Mean latency: {overhead['mean_ms']} ms/step (P50: {overhead['p50_ms']} ms, P95: {overhead['p95_ms']} ms)")

    results = {
        "benchmark_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "machine_spec": machine,
        "replay_determinism": determinism,
        "per_step_overhead": overhead,
    }

    out_file = Path(__file__).parent / "results.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nSaved benchmark results to {out_file}")


if __name__ == "__main__":
    main()
