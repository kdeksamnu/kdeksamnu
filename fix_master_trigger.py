#!/usr/init/env python3
"""
FIX_MASTER_TRIGGER.PY
Purges stale triggers and enforces strict RAISE(ROLLBACK) on cathedral_ash_archive.db
"""

import sqlite3

DB_PATH = "cathedral_ash_archive.db"

def main():
    print("[*] Re-forging Master Lex I Triggers...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Drop existing stale triggers
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update_master;")
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete_master;")
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update_archive;")
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete_archive;")

    # Re-create strict rollback triggers
    cur.execute("""
        CREATE TRIGGER prevent_lex_i_update_master
        BEFORE UPDATE ON ash_archive
        BEGIN
            SELECT RAISE(ROLLBACK, 'LEX I BREACH: Historical strata are immutable.');
        END;
    """)

    cur.execute("""
        CREATE TRIGGER prevent_lex_i_delete_master
        BEFORE DELETE ON ash_archive
        BEGIN
            SELECT RAISE(ROLLBACK, 'LEX I BREACH: Historical strata are immutable.');
        END;
    """)
    conn.commit()

    # Test interception immediately
    cur.execute("SELECT event_id FROM ash_archive ORDER BY event_id DESC LIMIT 1;")
    row = cur.fetchone()
    if row:
        target_id = row[0]
        try:
            conn.execute("BEGIN IMMEDIATE;")
            cur.execute(f"UPDATE ash_archive SET belnap_state = 'T' WHERE event_id = {target_id};")
            conn.commit()
            raise RuntimeError("FATAL: Lex I Breach! Table permitted silent revision.")
        except sqlite3.IntegrityError as e:
            conn.rollback()
            print(f"  [✓] Master Lex I Guard Confirmed: UPDATE successfully intercepted -> {e}")
    else:
        print("  [!] Ash Archive table is currently empty.")

    conn.close()
    print("[✓] MASTER TRIGGER RE-SEAL COMPLETE.")

if __name__ == "__main__":
    main()
