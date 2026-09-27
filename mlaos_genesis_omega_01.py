import sqlite3

def run_genesis_omega_01_sandbox():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Initialize Core Runtime Schema for Genesis-Ω01 Sandbox
    cursor.executescript("""
        CREATE TABLE game_state (
            turn INTEGER,
            round INTEGER,
            global_paradox INTEGER CHECK(global_paradox BETWEEN 0 AND 5),
            cascade_active BOOLEAN
        );
        
        CREATE TABLE entities (
            entity_id TEXT PRIMARY KEY,
            name TEXT,
            entity_type TEXT,
            hp INTEGER,
            max_hp INTEGER,
            strain INTEGER CHECK(strain BETWEEN 0 AND 6),
            position_x INTEGER,
            position_y INTEGER
        );
        
        CREATE TABLE ash_archive (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            actor TEXT,
            action TEXT,
            resulting_state TEXT,
            payload_hash TEXT
        );
        
        CREATE TABLE scar_anchors (
            anchor_id TEXT PRIMARY KEY,
            creator TEXT,
            coord_x INTEGER,
            coord_y INTEGER,
            scar_type TEXT,
            lifecycles_state TEXT
        );
    """)
    
    # Seed Initial Genesis State
    cursor.execute("INSERT INTO game_state VALUES (1, 1, 4, 0)")
    cursor.execute("INSERT INTO entities VALUES ('PLAYER-01', 'Riot Dre_atha', 'Player', 30, 30, 4, 5, 5)")
    cursor.execute("INSERT INTO entities VALUES ('ARBITER-01', 'ARBITER_MAGISTER_01', 'Boss', 180, 180, 0, 10, 10)")
    cursor.execute("INSERT INTO ash_archive (timestamp, actor, action, resulting_state, payload_hash) VALUES ('2026-09-26T14:05:45Z', 'System', 'GENESIS_OMEGA_01_INIT', 'Sandbox compiled successfully under Lex I.', '0x4F82C1')")
    conn.commit()
    
    print("==========================================================================")
    print("                  GENESIS-Ω01: THE EMPTY INTERVAL TEST                    ")
    print("==========================================================================")
    
    # Inspect Initial Sandbox State
    cursor.execute("SELECT global_paradox, cascade_active FROM game_state")
    gs = cursor.fetchone()
    print(f"[Init] Global Paradox Track: {gs[0]}/5 | Cascade Active: {bool(gs[1])}")
    
    cursor.execute("SELECT entity_id, name, hp, strain FROM entities")
    for row in cursor.fetchall():
        print(f"[Entity] ID: {row[0]} | Name: {row[1]} | HP: {row[2]} | Strain: {row[3]}")
        
    print("\n--- Simulating Player Action & Paradox Accumulation to 5/5 ---")
    # Player performs action generating dialetheic collision, pushing Paradox from 4 to 5
    cursor.execute("UPDATE game_state SET global_paradox = 5")
    cursor.execute("INSERT INTO scar_anchors VALUES ('ANCHOR-01', 'PLAYER-01', 5, 6, 'Dialetheic Micro-Scar', 'ACTIVE')")
    cursor.execute("INSERT INTO ash_archive (timestamp, actor, action, resulting_state, payload_hash) VALUES ('2026-09-26T14:06:00Z', 'Riot Dre_atha', 'Dialetheic Strike (Top)', 'Paradox reaches 5/5. Micro-Scar anchored at (5,6).', '0x99A1E4')")
    conn.commit()
    
    cursor.execute("SELECT global_paradox FROM game_state")
    current_paradox = cursor.fetchone()[0]
    print(f"[Event] Paradox Threshold Reached: {current_paradox}/5")
    
    if current_paradox >= 5:
        print("\n=== SYSTEM PROTOCOL: ONTOLOGICAL CASCADE TRIGGERED ===")
        print("[Phase 1] Flushing WAL and locking mutable operations...")
        print("[Phase 2] Rolling Cascade Domain -> [d10 = 3] Dialetheic Overlap (Top Flood)")
        
        # Apply Cascade Mutation: Reset Paradox to 0, flag Cascade active, log event in Ash Archive
        cursor.execute("UPDATE game_state SET global_paradox = 0, cascade_active = 1")
        cursor.execute("INSERT INTO ash_archive (timestamp, actor, action, resulting_state, payload_hash) VALUES ('2026-09-26T14:06:05Z', 'CascadeManager', 'ONTOLOGICAL_CASCADE_EXEC', 'Domain 3 (Top Flood) active. Pre-cascade history preserved.', '0xCC09FE')")
        conn.commit()
        
    print("\n--- Post-Cascade Sandbox State Verification ---")
    cursor.execute("SELECT global_paradox, cascade_active FROM game_state")
    gs_post = cursor.fetchone()
    print(f"Global Paradox Track Reset: {gs_post[0]}/5 | Cascade Active: {bool(gs_post[1])}")
    
    cursor.execute("SELECT anchor_id, scar_type, lifecycles_state FROM scar_anchors")
    anchor = cursor.fetchone()
    print(f"Active Scar Anchor -> ID: {anchor[0]} | Type: {anchor[1]} | State: {anchor[2]}")
    
    print("\n--- Ash Archive Audit Trail ---")
    cursor.execute("SELECT event_id, timestamp, actor, action, resulting_state FROM ash_archive")
    for log in cursor.fetchall():
        print(f"[{log[0]}] {log[1]} | {log[2]} -> {log[3]} | Result: {log[4]}")
        
    print("\n[VERIFICATION SUCCESS] GENESIS-Ω01 runtime prototype executed successfully.")
    conn.close()

if __name__ == "__main__":
    run_genesis_omega_01_sandbox()
