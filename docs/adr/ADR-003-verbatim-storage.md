# ADR-003: Verbatim Storage vs. Summarization

**Status:** Accepted
**Date:** 2026-06-28

## Context

INFINI needs a memory system. When an agent executes a step, its
output should be stored so future runs can learn from it.

Two approaches:
1. **Summarization:** Compress output via an LLM call before storage.
   Saves disk. Loses detail. Costs API tokens.
2. **Verbatim:** Store raw output as-is. Uses more disk. Loses nothing.
   Zero API cost.

The MemPalace project uses verbatim storage with FTS5 retrieval and
reports high retrieval accuracy because the full text is available for
search.

## Decision

Store all agent output verbatim in the `lessons` table. Use SQLite
FTS5 for full-text search retrieval.

- No summarization. No truncation. No API calls for memory.
- `memory.store_run_output()` writes the full output string.
- `memory.search_lessons()` uses FTS5 `MATCH` with BM25 ranking.
- Before each step, `memory.inject_context()` queries past lessons
  and injects them as system context.

## Consequences

**Positive:**
- Zero API cost for memory. No LLM calls needed to store or retrieve.
- Full fidelity. Nothing is lost in compression. When you search for
  "JWT implementation," you get the exact text that was stored.
- FTS5 is built into SQLite. No vector database, no embeddings, no
  external service.
- Retrieval is fast: sub-millisecond on 10K+ lessons.

**Negative:**
- Disk usage grows linearly with output volume. 10K runs × 5KB average
  = 50MB. Acceptable for local use; would need archival for scale.
- No semantic search. FTS5 does keyword matching, not meaning-based
  retrieval. A search for "authentication" won't find "auth" unless
  stemmed. Mitigation: future versions could add embedding-based
  search as an optional layer.
- No deduplication. If the same output is stored twice, it appears
  twice in search results. Mitigation: FTS5 BM25 ranking naturally
  de-duplicates by relevance.

## Attribution

The verbatim storage + FTS5 retrieval pattern is from
[MemPalace](https://github.com/mempalace/mempalace).
