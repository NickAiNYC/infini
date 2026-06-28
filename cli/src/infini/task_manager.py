"""Task manager — CRUD for tasks and messages.

Attribution: task lifecycle pattern from Squad (https://github.com/mco-org/squad)
"""
from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Optional

from .db import get_db


def create_task(title: str, body: str = "", assigned_to: str = "", parent_id: str = "") -> dict:
    """Create a new task. Returns the task dict."""
    conn = get_db()
    task_id = f"T-{uuid.uuid4().hex[:8]}"
    conn.execute(
        "INSERT INTO tasks (id, title, body, status, assigned_to, parent_task_id) VALUES (?, ?, ?, 'pending', ?, ?)",
        (task_id, title, body, assigned_to or None, parent_id or None),
    )
    conn.execute(
        "INSERT INTO messages (task_id, sender, content, msg_type) VALUES (?, 'manager', ?, 'log')",
        (task_id, f"Task created: {title}"),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row)


def ack_task(task_id: str, worker: str = "") -> dict | None:
    """Acknowledge a task (set status to 'acked')."""
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET status = 'acked', updated_at = ?, assigned_to = COALESCE(?, assigned_to) WHERE id = ?",
        (datetime.now().isoformat(), worker or None, task_id),
    )
    if worker:
        conn.execute(
            "INSERT INTO messages (task_id, sender, content, msg_type) VALUES (?, ?, 'Task acked', 'log')",
            (task_id, worker),
        )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def complete_task(task_id: str, summary: str = "") -> dict | None:
    """Mark a task complete with a summary."""
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET status = 'complete', summary = ?, updated_at = ? WHERE id = ?",
        (summary, datetime.now().isoformat(), task_id),
    )
    conn.execute(
        "INSERT INTO messages (task_id, sender, content, msg_type) VALUES (?, 'worker', ?, 'result')",
        (task_id, summary),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def fail_task(task_id: str, reason: str = "") -> dict | None:
    """Mark a task as failed."""
    conn = get_db()
    conn.execute(
        "UPDATE tasks SET status = 'failed', summary = ?, updated_at = ? WHERE id = ?",
        (reason, datetime.now().isoformat(), task_id),
    )
    conn.execute(
        "INSERT INTO messages (task_id, sender, content, msg_type) VALUES (?, 'worker', ?, 'log')",
        (task_id, f"Task failed: {reason}"),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def list_tasks(status: str = "pending") -> list[dict]:
    """List tasks by status. Default: pending."""
    conn = get_db()
    if status == "all":
        rows = conn.execute("SELECT * FROM tasks ORDER BY created_at DESC").fetchall()
    else:
        rows = conn.execute("SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC", (status,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_task(task_id: str) -> dict | None:
    """Get a single task by ID."""
    conn = get_db()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row) if row else None


def send_message(task_id: str, sender: str, content: str, msg_type: str = "log") -> None:
    """Send a message on the bus."""
    conn = get_db()
    conn.execute(
        "INSERT INTO messages (task_id, sender, content, msg_type) VALUES (?, ?, ?, ?)",
        (task_id, sender, content, msg_type),
    )
    conn.commit()
    conn.close()


def get_messages(task_id: str) -> list[dict]:
    """Get all messages for a task."""
    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM messages WHERE task_id = ? ORDER BY created_at", (task_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def wait_task(task_id: str, timeout: int = 300, poll_interval: float = 1.0) -> dict | None:
    """Block until task reaches 'complete' or 'failed' status.
    Attribution: --wait pattern from Squad (https://github.com/mco-org/squad)
    """
    start = time.time()
    while time.time() - start < timeout:
        task = get_task(task_id)
        if task and task["status"] in ("complete", "failed"):
            return task
        time.sleep(poll_interval)
    return None
