import sqlite3
from datetime import datetime

class AppendOnlyLedger:
    def __init__(self, db_path: str = "ash_archive.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS event_log (
                    sequence_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT UNIQUE NOT NULL,
                    payload TEXT NOT NULL,
                    parent_hash TEXT NOT NULL,
                    current_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def append_event(self, event_id: str, payload: str, parent_hash: str, current_hash: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT OR IGNORE INTO event_log (event_id, payload, parent_hash, current_hash, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (event_id, payload, parent_hash, current_hash, datetime.utcnow().isoformat()))
            conn.commit()
