import sqlite3

def test_master_merkle_core():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Initialize Relic & Holder Schema
    cursor.execute("""
        CREATE TABLE inventory (
            item_id TEXT PRIMARY KEY,
            item_name TEXT,
            relic_tier TEXT,
            basalt_bonus INTEGER,
            latency_penalty_ms REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE global_state (
            paradox_track INTEGER,
            immutable_zone_active BOOLEAN
        )
    """)
    
    # Insert Relic into Inventory and Global State
    cursor.execute("INSERT INTO inventory VALUES ('RELIC-001', 'Master Merkle Core', 'Sovereign', 2, 1.120)")
    cursor.execute("INSERT INTO global_state VALUES (5, 0)")
    conn.commit()
    
    print("--- MASTER MERKLE CORE: EQUIPPED ---")
    cursor.execute("SELECT basalt_bonus, latency_penalty_ms FROM inventory WHERE item_id = 'RELIC-001'")
    inv = cursor.fetchone()
    print(f"Passives Applied -> Basalt Bonus: +{inv[0]} | Initiative Latency Penalty: +{inv[1]} ms")
    
    # Simulate Active Ability: Root-Directory Rewrite (Paradox 5/5 -> 0/5)
    cursor.execute("UPDATE global_state SET paradox_track = 0")
    conn.commit()
    
    cursor.execute("SELECT paradox_track FROM global_state")
    paradox = cursor.fetchone()[0]
    print(f"Active Ability [Root-Directory Rewrite] Executed -> Global Paradox Track Reset to: {paradox}/5")
    
    # Simulate Ultimate Consumption: Lithic Foundation
    cursor.execute("DELETE FROM inventory WHERE item_id = 'RELIC-001'")
    cursor.execute("UPDATE global_state SET immutable_zone_active = 1")
    conn.commit()
    
    cursor.execute("SELECT immutable_zone_active FROM global_state")
    zone = cursor.fetchone()[0]
    print(f"Ultimate Consumption [Lithic Foundation] -> Zone Permanently Locked Under Lex I: {bool(zone)}")
    conn.close()

if __name__ == "__main__":
    test_master_merkle_core()
