import sqlite3

def initialize_jrpg_party_sheets():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE jrpg_party_roster (
            unit_id TEXT PRIMARY KEY,
            name TEXT,
            job_class TEXT,
            hp INTEGER,
            max_hp INTEGER,
            mp INTEGER,
            max_mp INTEGER,
            atk INTEGER,
            def_stat INTEGER,
            mag INTEGER,
            spd INTEGER,
            signature_skill TEXT,
            arcana_affinity TEXT
        );
    """)
    
    party = [
        ('P1', 'Ash Registrar', 'Archive Mage', 280, 280, 120, 120, 18, 22, 45, 14, 'Historical Revert', 'Syntax / Basalt'),
        ('P2', 'Latency Blade', 'Temporal Striker', 320, 320, 80, 80, 48, 20, 25, 35, 'Desync Strike', 'Kinetics / Recursion'),
        ('P3', 'Scar Carver', 'Ontological Guardian', 420, 420, 60, 60, 32, 44, 18, 10, 'Scar Detonation', 'Entropy / Basalt')
    ]
    
    cursor.executemany("INSERT INTO jrpg_party_roster VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", party)
    conn.commit()
    
    print("==========================================================================")
    print("      MLAOS-PRIME // JRPG PARTY STAT SHEETS (LEVEL 10 VECTORS)            ")
    print("==========================================================================")
    
    cursor.execute("SELECT unit_id, name, job_class, hp, mp, atk, def_stat, mag, spd, signature_skill, arcana_affinity FROM jrpg_party_roster")
    for row in cursor.fetchall():
        print(f"[{row[0]}] {row[1]} ({row[2]})")
        print(f"    -> HP: {row[3]} | MP: {row[4]} | ATK: {row[5]} | DEF: {row[6]} | MAG: {row[7]} | SPD: {row[8]}")
        print(f"    -> Signature Skill: {row[9]} | Affinity: {row[10]}\n")
        
    print("[SUCCESS] JRPG party unit stat sheets compiled into authoritative runtime memory.")
    conn.close()

if __name__ == "__main__":
    initialize_jrpg_party_sheets()
