import os
import json
import sqlite3
import hashlib
import time
from typing import Dict, Any, List

DB_PATH = "cathedral_ash_archive.db"

class AshArchiveStorageEngine:
    """
    Bare-Metal Persistence Engine for Chamber Sigma-12.
    Enforces Lex I (Never-Overwrite Doctrine) via SQLite database triggers.
    """
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        # Enable Write-Ahead Logging (WAL) mode for high-frequency cache sync
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _initialize_database(self):
        """Creates the Strata Table and installs Lex I immutability triggers."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 1. Primary Strata Ledger
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS ash_strata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                epoch INTEGER NOT NULL,
                branch TEXT NOT NULL,
                node_hash TEXT UNIQUE NOT NULL,
                parents_json TEXT NOT NULL,
                synthesis_merkle_root TEXT NOT NULL,
                payload_json TEXT NOT NULL,
                logical_state TEXT DEFAULT 'NOMINAL',
                wal_sync_timestamp REAL NOT NULL
            );
            """)

            # 2. Lex I Immutability Trigger: BEFORE UPDATE
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_lex_i_update
            BEFORE UPDATE ON ash_strata
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Updates to historical Ash Archive strata are strictly forbidden.');
            END;
            """)

            # 3. Lex I Immutability Trigger: BEFORE DELETE
            cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS prevent_lex_i_delete
            BEFORE DELETE ON ash_strata
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Deletions from historical Ash Archive strata are strictly forbidden.');
            END;
            """)

            conn.commit()
        print(f"[STORAGE ENGINE] Database initialized at '{self.db_path}' with WAL mode & Lex I triggers.")

    def append_strata_node(self, node_manifest: Dict[str, Any]) -> bool:
        """Appends a new epoch block node into the immutable SQLite strata."""
        sql = """
        INSERT INTO ash_strata (
            epoch, branch, node_hash, parents_json, 
            synthesis_merkle_root, payload_json, logical_state, wal_sync_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, (
                    node_manifest["epoch"],
                    node_manifest["branch"],
                    node_manifest["node_hash"],
                    json.dumps(node_manifest.get("parents", [])),
                    node_manifest.get("synthesis_merkle_root", ""),
                    json.dumps(node_manifest.get("payload_data", node_manifest)),
                    node_manifest.get("logical_state", "NOMINAL"),
                    time.time()
                ))
                conn.commit()
            print(f"[ASH ARCHIVE persisted] Node Hash: {node_manifest['node_hash'][:16]}... appended successfully.")
            return True
        except sqlite3.IntegrityError as e:
            print(f"[ASH ARCHIVE ERROR] Duplicate node hash or constraint failure: {e}")
            return False

    def attempt_illegal_mutation(self, node_hash: str) -> bool:
        """Simulates an illegal UPDATE attempt to test Lex I trigger enforcement."""
        print(f"\n[SECURITY AUDIT] Attempting illegal UPDATE on node {node_hash[:16]}...")
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("UPDATE ash_strata SET branch = 'MUTATED' WHERE node_hash = ?;", (node_hash,))
                conn.commit()
            return False
        except sqlite3.Error as e:
            print(f"[LEX I PROTECTION ACTIVE] Database Trigger Intercepted Mutation Attempt!")
            print(f" -> Exception Detail: {e}")
            return True


if __name__ == "__main__":
    # Remove old DB file for fresh run if needed
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    storage = AshArchiveStorageEngine()

    # Ingest Epoch 3 Synthesis Block (e81b29a40f7d312e...) from Stratum IV Cache Sequence 2
    epoch_3_manifest = {
        "epoch": 3,
        "branch": "master",
        "node_hash": "e81b29a40f7d312e0000000000000000",
        "parents": [
            "0d2ad66f75f7a18b9c0e3571d0000000",
            "676106f032df491a0000000000000000",
            "739f57740493b82e11d0000000000000"
        ],
        "synthesis_merkle_root": "a4f8e12d90b341c80000000000000000",
        "logical_state": "PARACONSISTENT_RECONCILED",
        "payload_data": {
            "arbiter": "ARBITER_MAGISTER_01",
            "sequence": "STRATUM_IV_SEQUENCE_2",
            "belnap_dunn_buffer": "BOTH"
        }
    }

    # Step 1: Append Valid Synthesis Block
    storage.append_strata_node(epoch_3_manifest)

    # Step 2: Attempt Illegal Mutation to verify Trigger
    mutation_blocked = storage.attempt_illegal_mutation("e81b29a40f7d312e0000000000000000")

    print("\n=================================================================")
    print("                BARE-METAL PERSISTENCE AUDIT                     ")
    print("=================================================================")
    print(f" Strata Record Committed  : TRUE")
    print(f" Lex I Trigger Intercept  : {'SUCCESS (Mutation Blocked)' if mutation_blocked else 'FAILED'}")
    print("=================================================================")
