#!/bin/bash
# INFINI Portability Proof — Side-by-Side Demo
# Record this with asciinema or screen recording
# Title: "Same Loopfile. Two Engines. Identical Traces. That's INFINI."

set -e

echo "═══════════════════════════════════════════════════════════"
echo "  INFINI Portability Proof"
echo "  Same Loopfile. Two Engines. Identical Traces."
echo "═══════════════════════════════════════════════════════════"
echo ""

# 0. Show the Loopfile
echo "The Loopfile: examples/hello-world/Loopfile.yaml"
echo ""
cat examples/hello-world/Loopfile.yaml
echo ""

# 1. Run on Reference Engine
echo "Running on INFINI Reference Engine..."
echo "─────────────────────────────────────────"
infini run examples/hello-world/Loopfile.yaml --mock --engine infini -o runs/reference/ -q
echo ""
echo "Trace summary:"
python3 -c "
import json
t = json.load(open('runs/reference/run.json'))
print(f'  engine: {t[\"engine\"][\"type\"]}')
print(f'  outcome: {t[\"outcome\"]}')
print(f'  steps: {len(t[\"steps\"])}')
print(f'  cost: \${t[\"budget\"][\"spent_dollars\"]:.2f}')
"
echo ""

# 2. Run on LangGraph
echo "Running on LangGraph Adapter..."
echo "─────────────────────────────────────────"
infini run examples/hello-world/Loopfile.yaml --mock --engine langgraph -o runs/langgraph/ -q
echo ""
echo "Trace summary:"
python3 -c "
import json
t = json.load(open('runs/langgraph/run.json'))
print(f'  engine: {t[\"engine\"][\"type\"]}')
print(f'  outcome: {t[\"outcome\"]}')
print(f'  steps: {len(t[\"steps\"])}')
print(f'  cost: \${t[\"budget\"][\"spent_dollars\"]:.2f}')
"
echo ""

# 3. Diff the traces
echo "Diffing traces..."
echo "─────────────────────────────────────────"
infini diff runs/reference/run.json runs/langgraph/run.json
echo ""

# 4. The payoff
echo "═══════════════════════════════════════════════════════════"
echo "  Same Loopfile. Two Engines. Identical Trace Format."
echo ""
echo "  That's INFINI portability."
echo "  pip install infini-cli"
echo "═══════════════════════════════════════════════════════════"
