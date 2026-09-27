#!/usr/bin/env python3
"""
FIX_AND_VERIFY_LEX_I.PY
Ensures genesis seeding of the ash_archive table and verifies Lex I immutability triggers.
"""

import sqlite3
import time
import hashlib

DB_PATH = "cathedral_ash_archive.db"

def main():
    print("[*] Booting Lex I Genesis Verification Harness...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Ensure schema exists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ash_archive (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            parent_hash TEXT NOT NULL,
            logical_clock INTEGER NOT NULL,
            belnap_state TEXT NOT NULL,
            desired_vector TEXT NOT NULL,
            executed_vector TEXT NOT NULL,
            strain_energy REAL NOT NULL,
            lineage_hash TEXT NOT NULL,
            timestamp REAL NOT NULL
        );
    """)

    # 2. Re-bind triggers securely
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update_archive;")
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete_archive;")

    cur.execute("""
        CREATE TRIGGER prevent_lex_i_update_archive
        BEFORE UPDATE ON ash_archive
        BEGIN
            SELECT RAISE(FAIL, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
        END;
    """)

    cur.execute("""
        CREATE TRIGGER prevent_lex_i_delete_archive
        BEFORE DELETE ON ash_archive
        BEGIN
            SELECT RAISE(FAIL, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
        END;
    """)
    conn.commit()

    # 3. Ensure at least one genesis stratum exists to test against
    cur.execute("SELECT COUNT(*) FROM ash_archive;")
    if cur.fetchone()[0] == 0:
        print("  [+] Seeding Genesis Stratum into Ash Archive...")
        ts = time.time()
        genesis_hash = hashlib.sha256(b"GENESIS_ROOT_SEED").hexdigest()
        cur.execute("""
            INSERT INTO ash_archive (parent_hash, logical_clock, belnap_state, desired_vector, executed_vector, strain_energy, lineage_hash, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """, ("GENESIS_ROOT_00000000", 0, "N", "[0,0,0]", "[0,0,0]", 0.0, genesis_hash, ts))
        conn.commit()

    # 4. Retrieve target event_id safely
    cur.execute("SELECT event_id FROM ash_archive ORDER BY event_id ASC LIMIT 1;")
    row = cur.fetchone()
    if not row:
        raise RuntimeError("FATAL: Failed to retrieve or seed valid ash_archive event row.")
    
    target_id = row[0]
    print(f"  [+] Target Stratum Acquired for Mutation Test: Index #{target_id}")

    # 5. Execute Lex I Interception Test
    try:
        cur.execute(f"UPDATE ash_archive SET belnap_state = 'F' WHERE event_id = {target_id};")
        conn.commit()
        raise RuntimeError("FATAL: Lex I Breach! SQLite permitted silent stratum update.")
    except sqlite3.IntegrityError as e:
        print(f"  [✓] Lex I Guard Confirmed: UPDATE successfully intercepted -> {e}")

    conn.close()
    print("[✓] CATHEDRAL ASH ARCHIVE SEALED AND VERIFIED UNDER LEX I.")

if __name__ == "__main__":
    main()
