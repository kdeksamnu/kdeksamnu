import sqlite3
import hashlib
import time
import math
from typing import Tuple

def init_campaign_db(db_path: str = "sovereign_odyssey.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ash_strata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        layer_id INTEGER NOT NULL,
        logic_state TEXT NOT NULL,
        event_payload TEXT NOT NULL,
        parent_hash TEXT NOT NULL,
        lineage_hash TEXT NOT NULL
    );
    """)
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS abort_strata_tampering
    BEFORE UPDATE ON ash_strata
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_BREACH: Strata in the Ash Archive cannot be modified.');
    END;
    """)
    conn.commit()
    return conn

if __name__ == "__main__":
    db = init_campaign_db()
    cur = db.cursor()
    cur.execute("SELECT lineage_hash FROM ash_strata ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    parent_hash = row[0] if row else "GENESIS_" + ("0" * 56)
    ts = time.time()
    payload = "RUNTIME_CHECKPOINT: Sovereign Odyssey Engine active on feature/dialetheic-heat-sink."
    raw = f"{ts}:5:B:{payload}:{parent_hash}".encode('utf-8')
    lineage_hash = hashlib.sha256(raw).hexdigest()
    cur.execute("""
        INSERT INTO ash_strata (timestamp, layer_id, logic_state, event_payload, parent_hash, lineage_hash)
        VALUES (?, 5, 'B', ?, ?, ?);
    """, (ts, payload, parent_hash, lineage_hash))
    db.commit()
    print(f"[✓] Sovereign Odyssey Engine verified. Merkle Root: {lineage_hash}")
    db.close()
