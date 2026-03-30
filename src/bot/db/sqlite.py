from __future__ import annotations

from pathlib import Path

import aiosqlite

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS chat_settings (
        chat_id INTEGER PRIMARY KEY,
        is_paused INTEGER NOT NULL DEFAULT 0,
        system_prompt TEXT NOT NULL,
        current_model_slug TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS cooldown_state (
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        last_request_at REAL NOT NULL,
        PRIMARY KEY (chat_id, user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS active_requests (
        chat_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        started_at REAL NOT NULL,
        request_key TEXT NOT NULL,
        PRIMARY KEY (chat_id, user_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS admin_audit_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        chat_id INTEGER NOT NULL,
        actor_user_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        old_value_json TEXT NULL,
        new_value_json TEXT NULL,
        created_at TEXT NOT NULL
    )
    """,
]


async def connect(sqlite_path: str, busy_timeout_ms: int) -> aiosqlite.Connection:
    path = Path(sqlite_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    db = await aiosqlite.connect(str(path))
    db.row_factory = aiosqlite.Row
    await db.execute(f"PRAGMA busy_timeout = {int(busy_timeout_ms)}")
    await db.execute("PRAGMA journal_mode = WAL")
    return db


async def initialize_database(db: aiosqlite.Connection) -> None:
    for statement in SCHEMA_STATEMENTS:
        await db.execute(statement)
    await db.commit()
