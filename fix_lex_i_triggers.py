#!/usr/bin/env python3
"""
FIX_LEX_I_TRIGGERS.PY
Re-binds bare-metal Lex I triggers to ensure strict fail-closed interception
on the ash_archive stratum table.
"""

import sqlite3

DB_PATH = "cathedral_ash_archive.db"

def main():
    print("[*] Re-forging Lex I Bare-Metal Triggers on Cathedral Ash Archive...")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # 1. Drop existing triggers to clear any shadow bindings
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update_archive;")
    cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete_archive;")

    # 2. Re-create strict BEFORE UPDATE and BEFORE DELETE triggers
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
    print("  [+] Triggers re-bound successfully.")

    # 3. Test interception
    cur.execute("SELECT event_id FROM ash_archive LIMIT 1;")
    row = cur.fetchone()
    if row:
        target_id = row[0]
        try:
            cur.execute(f"UPDATE ash_archive SET belnap_state = 'F' WHERE event_id = {target_id};")
            conn.commit()
            raise RuntimeError("FATAL: Lex I Breach! Update was permitted.")
        except sqlite3.IntegrityError as e:
            print(f"  [✓] Lex I Guard Confirmed: UPDATE successfully intercepted -> {e}")
    else:
        print("  [!] Table contains no strata to test.")

    conn.close()
    print("[✓] LEX I RE-SEAL COMPLETE.")

if __name__ == "__main__":
    main()
