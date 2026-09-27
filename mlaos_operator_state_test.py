import sqlite3

def verify_operator_strain_track():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE resonance_strain_track (
            operator_id TEXT PRIMARY KEY,
            current_strain INTEGER CHECK(current_strain BETWEEN 0 AND 6),
            paradox_accumulator INTEGER DEFAULT 0
        )
    """)
    cursor.execute("INSERT INTO resonance_strain_track VALUES ('ash_registrar_01', 4, 1)")
    conn.commit()
    
    cursor.execute("SELECT current_strain, paradox_accumulator FROM resonance_strain_track WHERE operator_id = 'ash_registrar_01'")
    row = cursor.fetchone()
    print(f"Verified Operator Strain: {row[0]} | Paradox Track: {row[1]}")
    conn.close()

if __name__ == "__main__":
    verify_operator_strain_track()
