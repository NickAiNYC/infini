# Local LLM Adapter (Qwythos + llama.cpp)

> Runs INFINI Loopfiles fully offline on consumer hardware.
> No API key. No internet. Deterministic output.

## Status: Preview — live mode working with Qwythos GGUF

This adapter runs a real local LLM via [llama.cpp](https://github.com/ggml-org/llama.cpp)
to execute INFINI Loopfiles. It is the third engine in the portability proof
(Reference Engine, LangGraph, Local).

## What this unlocks

- INFINI's `--live` mode runs entirely offline, on consumer hardware
- No API keys, no cloud dependencies, no data leaving the machine
- Deterministic output at `--temp 0.0` for reproducible traces
- Portability: same Loopfile produces identical trace structure across
  Reference, LangGraph, and Local engines

## Setup

```bash
# 1. Install llama.cpp
brew install llama.cpp
# or: git clone https://github.com/ggml-org/llama.cpp && cd llama.cpp && make

# 2. Download the Qwythos GGUF
infini setup --download-qwythos
# Downloads to ~/.infini/models/qwythos-9b-q4_k_m.gguf

# 3. Run a Loopfile
infini run examples/hello-world/Loopfile.yaml --engine local --live
```

## Portability proof

```bash
infini run loop.yaml --engine local --trace local.json
infini run loop.yaml --engine langgraph --trace langgraph.json
infini diff local.json langgraph.json
# → Identical structure. Verified. Portable.
```

## How it works

1. The adapter parses the Loopfile into a structured prompt
2. `llama-cli` runs the GGUF model with the prompt
3. Output is parsed as JSON and mapped to INFINI trace format
4. Steps, tokens, and cost are recorded — cost is always $0.00

## Limitations

- Deterministic mode (`--temp 0.0`) preferred for reproducible traces
- Larger models (9B+) may need 8-16GB RAM
- Only agents with `prompt` fields are supported (role-only agents use
  a default system prompt derived from their `role`)
