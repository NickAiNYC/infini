"""SQLite coordination bus.

Architecture stolen from Squad (https://github.com/mco-org/squad):
- tasks table: manager assigns, workers claim
- messages table: agent-to-agent communication
- lessons table: verbatim memory (stolen from MemPalace)

No ORM. No Redis. Just sqlite3 and the filesystem.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_PATH = os.environ.get(
    "INFINI_DB_PATH",
    str(Path.home() / ".infini" / "infini.db"),
)

SCHEMA = """
-- Tasks table (manager assigns, workers claim)
-- Attribution: schema pattern from Squad (https://github.com/mco-org/squad)
CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    body TEXT,
    status TEXT DEFAULT 'pending',
    assigned_to TEXT,
    parent_task_id TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP,
    summary TEXT,
    FOREIGN KEY(parent_task_id) REFERENCES tasks(id)
);

-- Messages bus (agent-to-agent chat)
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id TEXT,
    sender TEXT,
    content TEXT,
    msg_type TEXT DEFAULT 'log',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(task_id) REFERENCES tasks(id)
);

-- Lessons/Memory (verbatim, no summarization)
-- Attribution: concept from MemPalace (https://github.com/mempalace/mempalace)
CREATE TABLE IF NOT EXISTS lessons (
    id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    context TEXT,
    embedding BLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 virtual table for full-text search on lessons
CREATE VIRTUAL TABLE IF NOT EXISTS lessons_fts USING fts5(
    content,
    content='lessons',
    content_rowid='rowid'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS lessons_ai AFTER INSERT ON lessons BEGIN
    INSERT INTO lessons_fts(rowid, content) VALUES (new.rowid, new.content);
END;
CREATE TRIGGER IF NOT EXISTS lessons_ad AFTER DELETE ON lessons BEGIN
    INSERT INTO lessons_fts(lessons_fts, rowid, content) VALUES('delete', old.rowid, old.content);
END;
CREATE TRIGGER IF NOT EXISTS lessons_au AFTER UPDATE ON lessons BEGIN
    INSERT INTO lessons_fts(lessons_fts, rowid, content) VALUES('delete', old.rowid, old.content);
    INSERT INTO lessons_fts(rowid, content) VALUES (new.rowid, new.content);
END;

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_assigned ON tasks(assigned_to);
CREATE INDEX IF NOT EXISTS idx_messages_task ON messages(task_id);
"""


def get_db(db_path: str | None = None) -> sqlite3.Connection:
    """Get a SQLite connection. Initializes the DB on first call."""
    path = db_path or DEFAULT_DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    # FK enforcement is off by default — we keep it off for robustness
    # (messages may reference task IDs from other sessions)
    conn.executescript(SCHEMA)
    conn.commit()
    return conn


def init_db(db_path: str | None = None) -> Path:
    """Initialize the DB. Called on first CLI run."""
    conn = get_db(db_path)
    path = Path(db_path or DEFAULT_DB_PATH)
    conn.close()
    return path
