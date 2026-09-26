import sqlite3

def enforce_lex_i():
    conn = sqlite3.connect("cathedral_ash_archive.db")
    cursor = conn.cursor()
    
    # Drop existing if present to ensure clean application
    cursor.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update;")
    cursor.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete;")
    
    # Create Lex I Immutability Triggers
    cursor.execute("""
        CREATE TRIGGER prevent_lex_i_update
        BEFORE UPDATE ON ash_strata
        BEGIN
            SELECT RAISE(FAIL, 'LEX I VIOLATION: Updates to historical Ash Archive strata are strictly forbidden.');
        END;
    """)
    
    cursor.execute("""
        CREATE TRIGGER prevent_lex_i_delete
        BEFORE DELETE ON ash_strata
        BEGIN
            SELECT RAISE(FAIL, 'LEX I VIOLATION: Deletions from historical Ash Archive strata are strictly forbidden.');
        END;
    """)
    
    conn.commit()
    conn.close()
    print("[+] Lex I Bare-Metal Immutability Triggers successfully anchored to cathedral_ash_archive.db via Python runtime.")

if __name__ == "__main__":
    enforce_lex_i()
