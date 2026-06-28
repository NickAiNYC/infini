"""Tests for the Loopfile parser and schema validation."""
import pytest
from pathlib import Path

from infini.parse import parse, parse_file, ParseError


VALID_LOOPFILE = """\
LOOPFILE: "1.0"
name: test-loop
version: 1.0.0
OBJECTIVE: "Test objective."
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS:
  - { id: s1, name: step1, action: do_thing, uses: builder, produces: [out.txt] }
VERIFY:
  syntactic: ["out.txt:exists"]
  semantic: ["judge:quality>=80"]
  confidence_threshold: 80
BUDGET: { dollars: 5, minutes: 10 }
STOP_WHEN: ["all_verify_passed"]
"""


def test_parse_valid_loopfile():
    """A valid Loopfile parses without error."""
    lf = parse(VALID_LOOPFILE)
    assert lf.name == "test-loop"
    assert lf.version == "1.0.0"
    assert lf.spec_version == "1.0"
    assert len(lf.agents) == 1
    assert len(lf.steps) == 1
    assert lf.steps[0].id == "s1"
    assert lf.verify.confidence_threshold == 80
    assert lf.budget.dollars == 5


def test_parse_invalid_yaml():
    """Invalid YAML raises ParseError."""
    with pytest.raises(ParseError):
        parse("LOOPFILE: [invalid")


def test_parse_missing_required_field():
    """Missing required field raises ParseError."""
    yaml = """
LOOPFILE: "1.0"
name: test
version: 1.0.0
OBJECTIVE: "test"
AGENTS:
  - { name: builder, role: builder, model_tier: sonnet }
STEPS:
  - { id: s1, name: s, action: a, uses: builder }
VERIFY:
  syntactic: []
  semantic: []
  confidence_threshold: 80
BUDGET: { dollars: 5, minutes: 10 }
"""
    with pytest.raises(ParseError):
        parse(yaml)  # missing STOP_WHEN


def test_parse_tools_block_accepted():
    """The TOOLS block (MCP) should be accepted by the schema."""
    yaml = VALID_LOOPFILE + 'TOOLS:\n  - { mcp: "example.com/mcp/server" }\n'
    lf = parse(yaml)
    assert lf.engine is None  # ENGINE not set


def test_parse_file_not_found():
    """Non-existent file raises ParseError."""
    with pytest.raises(ParseError):
        parse_file("/nonexistent/path/Loopfile.yaml")
