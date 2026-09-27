import sqlite3

def initialize_character_classes():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE character_templates (
            class_id TEXT PRIMARY KEY,
            name TEXT,
            role TEXT,
            hp INTEGER,
            ac INTEGER,
            initiative_latency_ms REAL,
            movement_vector_fps INTEGER,
            syntax INTEGER,
            kinetics INTEGER,
            entropy INTEGER,
            density INTEGER,
            basalt INTEGER,
            recursion INTEGER
        );
        
        CREATE TABLE class_abilities (
            ability_id TEXT PRIMARY KEY,
            class_id TEXT,
            ability_name TEXT,
            strain_cost INTEGER,
            description TEXT,
            FOREIGN KEY(class_id) REFERENCES character_templates(class_id)
        );
    """)
    
    classes = [
        ('ASH-REGISTRAR', 'Ash Registrar', 'Support / Provenance Architect', 28, 14, 0.180, 30, 16, 12, 10, 14, 14, 16),
        ('LATENCY-BLADE', 'Latency Blade', 'Striker / Temporal Interrupter', 32, 15, 0.090, 45, 14, 16, 16, 12, 10, 14),
        ('SCAR-CARVER', 'Scar Carver', 'Frontline Tank / Paradox Engine', 42, 18, 0.240, 25, 10, 14, 14, 16, 16, 10)
    ]
    
    abilities = [
        ('AB-01', 'ASH-REGISTRAR', 'Historical Substitution', 2, 'Query Ash Archive to revert an ally status condition.'),
        ('AB-02', 'ASH-REGISTRAR', 'Stratum Geyser', 4, 'Erupt an active Scar. 3d8 Syntax damage and Locked (DC 15 save).'),
        ('AB-03', 'LATENCY-BLADE', 'Desync Step', 1, 'Teleport 30 ft between active Scar Anchors.'),
        ('AB-04', 'LATENCY-BLADE', 'Dialetheic Strike', 3, 'Parallel attack vectors (Branch Alpha & Beta). +1 Paradox on double hit.'),
        ('AB-05', 'SCAR-CARVER', 'Scar Drag', 1, 'Pull active Scar 20 ft toward self, dragging adjacent enemies.'),
        ('AB-06', 'SCAR-CARVER', 'Dialetheic Collapse', 5, 'Detonate all Scars within 30 ft. Triggers Ontological Cascade.')
    ]
    
    cursor.executemany("INSERT INTO character_templates VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", classes)
    cursor.executemany("INSERT INTO class_abilities VALUES (?, ?, ?, ?, ?)", abilities)
    conn.commit()
    
    print("==========================================================================")
    print("             MLAOS-PRIME: LEVEL-1 OPERATOR ARCHETYPES VERIFIED            ")
    print("==========================================================================")
    
    cursor.execute("SELECT class_id, name, role, hp, ac FROM character_templates")
    for row in cursor.fetchall():
        print(f"[{row[0]}] {row[1]} — Role: {row[2]} | HP: {row[3]} | AC: {row[4]}")
        
    conn.close()

if __name__ == "__main__":
    initialize_character_classes()
