from __future__ import annotations

import aiosqlite


class BaseRepository:
    def __init__(self, db: aiosqlite.Connection) -> None:
        self.db = db
