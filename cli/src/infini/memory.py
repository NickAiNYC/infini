"""Eternal memory — verbatim storage and FTS5 retrieval.

Attribution: Wings/Rooms/Drawers indexing concept from MemPalace
(https://github.com/mempalace/mempalace). No summarization. No truncation.
All stdout/stderr stored verbatim.
"""
from __future__ import annotations

import json
import uuid
from typing import Optional

from .db import get_db


def store_lesson(content: str, context: dict | None = None) -> str:
    """Store a lesson verbatim. No summarization. No truncation.

    Returns the lesson ID.
    """
    conn = get_db()
    lesson_id = f"L-{uuid.uuid4().hex[:8]}"
    ctx = json.dumps(context) if context else None
    conn.execute(
        "INSERT INTO lessons (id, content, context) VALUES (?, ?, ?)",
        (lesson_id, content, ctx),
    )
    conn.commit()
    conn.close()
    return lesson_id


def search_lessons(query: str, limit: int = 5) -> list[dict]:
    """Full-text search on lessons using SQLite FTS5.

    Returns matching lessons ordered by relevance.
    """
    conn = get_db()
    try:
        rows = conn.execute(
            "SELECT l.id, l.content, l.context, l.created_at, "
            "bm25(lessons_fts) as rank "
            "FROM lessons_fts JOIN lessons l ON l.rowid = lessons_fts.rowid "
            "WHERE lessons_fts MATCH ? "
            "ORDER BY rank LIMIT ?",
            (query, limit),
        ).fetchall()
    except Exception:
        # FTS5 might not be available on all SQLite builds
        rows = conn.execute(
            "SELECT id, content, context, created_at FROM lessons "
            "WHERE content LIKE ? ORDER BY created_at DESC LIMIT ?",
            (f"%{query}%", limit),
        ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def recent_lessons(limit: int = 100) -> list[dict]:
    """Get the N most recent lessons."""
    conn = get_db()
    rows = conn.execute(
        "SELECT id, content, context, created_at FROM lessons ORDER BY created_at DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def inject_context(query: str, limit: int = 5) -> str:
    """Search lessons and format results as injectable system context.

    Called before executing any step to give the agent 'infinite memory'
    without API calls.
    """
    results = search_lessons(query, limit=limit)
    if not results:
        return ""
    lines = ["## Relevant lessons from memory:"]
    for r in results:
        ctx = json.loads(r["context"]) if r.get("context") else {}
        source = ctx.get("loopfile", "unknown")
        lines.append(f"- [{r['created_at']}] ({source}): {r['content']}")
    return "\n".join(lines)


def store_run_output(loopfile_name: str, step_id: str, step_name: str, output: str) -> None:
    """Store step output verbatim as a lesson."""
    store_lesson(
        content=f"[{loopfile_name}:{step_id}:{step_name}] {output}",
        context={"loopfile": loopfile_name, "step": step_id, "step_name": step_name},
    )
