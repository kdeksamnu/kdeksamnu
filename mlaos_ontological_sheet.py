import sqlite3

def initialize_ontological_sheet():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE ontological_runtime_sheet (
            operator_id TEXT PRIMARY KEY,
            codename TEXT,
            class_archetype TEXT,
            runtime_epoch INTEGER,
            cornerstone_key TEXT,
            current_strain INTEGER CHECK(current_strain BETWEEN 0 AND 6),
            paradox_accumulator INTEGER CHECK(paradox_accumulator BETWEEN 0 AND 5)
        )
    """)
    
    cursor.execute("""
        INSERT INTO ontological_runtime_sheet VALUES 
        ('OP-0767', 'Riot Dre_atha', 'Ash Registrar', 12, '0x8F9A-3B21-CC44-E102', 4, 1)
    """)
    conn.commit()
    
    cursor.execute("SELECT operator_id, codename, class_archetype, current_strain, paradox_accumulator FROM ontological_runtime_sheet")
    row = cursor.fetchone()
    print(f"Initialized Sheet [{row[0]}] | Alias: {row[1]} | Class: {row[2]} | Strain: {row[3]} | Paradox: {row[4]}")
    conn.close()

if __name__ == "__main__":
    initialize_ontological_sheet()
