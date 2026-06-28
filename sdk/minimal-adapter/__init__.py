"""Minimal INFINI adapter — PARSE only.

Copy this file, rename the class, and implement RUN/VERIFY/INSPECT/REPLAY
as needed. Each capability you implement should be flipped to true in
adapter.yaml.
"""
from __future__ import annotations

from pathlib import Path

# The SDK base class (when the SDK is installed as a package)
try:
    from infini.sdk import Adapter, Capability
    from infini.types import Loopfile
except ImportError:
    # Fallback for when running standalone (before SDK is pip-installed)
    Adapter = object
    Capability = None
    Loopfile = dict


class MinimalAdapter(Adapter):
    """Parse-only adapter. Extend by implementing more capabilities."""

    name = "minimal"
    spec = "LOOPFILE-1.0"
    type = "execution"
    description = "Minimal adapter — PARSE only. Use as a starting point."
    min_engine_version = "0.1.0"
    tools = []
    agent_roles = {}
    trace_extensions = {}
    delegates = {}

    def parse(self, loopfile_yaml: str) -> Loopfile:
        """Parse and validate a Loopfile YAML string.

        This is the only required capability. Use the SDK's schema
        validator, or jsonschema directly.
        """
        import yaml
        from jsonschema import Draft202012Validator

        # Load the schema (shipped with infini-cli)
        import importlib.resources
        schema = importlib.resources.files("infini").joinpath("schema.json").read_text()
        schema_obj = __import__("json").loads(schema)

        data = yaml.safe_load(loopfile_yaml)
        Draft202012Validator(schema_obj).validate(data)
        return data

    # Uncomment and implement these as you add capabilities:

    # def run(self, loopfile: Loopfile, state) -> "State":
    #     """Execute the STEPS DAG. Return the final state."""
    #     raise NotImplementedError("RUN not yet implemented")

    # def verify(self, loopfile: Loopfile, state) -> "VerifyResult":
    #     """Run syntactic + semantic checks. Return pass/fail + confidence."""
    #     raise NotImplementedError("VERIFY not yet implemented")

    # def inspect(self, run_dir: Path) -> "Trace":
    #     """Load a run's trace from run_dir/run.json."""
    #     raise NotImplementedError("INSPECT not yet implemented")

    # def replay(self, run_dir: Path, from_step: str, mutations: dict) -> "Trace":
    #     """Replay a run from a step, with optional input mutations."""
    #     raise NotImplementedError("REPLAY not yet implemented")

    # def diff(self, v1: Loopfile, v2: Loopfile) -> "Diff":
    #     """Produce a semantic diff between two Loopfiles."""
    #     raise NotImplementedError("DIFF not yet implemented")


# Entry point for the adapter registry
ADAPTER = MinimalAdapter
