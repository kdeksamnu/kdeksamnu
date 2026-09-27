import sqlite3
import hashlib
import time

def execute_encounter_02_alpha():
    conn = sqlite3.connect("sovereign_odyssey.db")
    cursor = conn.cursor()
    
    # Entity ENT_07 (Kaelen) executes Option Alpha: Threshold Inversion on the Timber Rail
    # Utilizing low CoM, 480 N/m modulus, and left-arm tension hook beneath the beam.
    
    timestamp = time.time()
    layer = 4 # Kinematic / Contact Tier
    logic_state = "B" # Belnap-Dunn Both (Hanging tension vs. forward transit)
    
    payload = (
        "ENCOUNTER_02_EXECUTE|"
        "ENTITY=ENT_07 (Kaelen)|"
        "ACTION=OPTION_ALPHA_THRESHOLD_INVERSION|"
        "SUBSTRATE=SUSPENDED_TIMBER_RAIL_0.25M|"
        "MECHANIC=OMEGA_CORE_DROP_AND_HOOK|"
        "STATUS=SUCCESSFUL_UNDERSLUNG_EVASION"
    )
    
    cursor.execute("SELECT lineage_hash FROM ash_strata ORDER BY id DESC LIMIT 1;")
    row = cursor.fetchone()
    parent_hash = row[0] if row else "GENESIS_" + ("0" * 56)
    
    raw = f"{timestamp}:{layer}:{logic_state}:{payload}:{parent_hash}".encode('utf-8')
    lineage_hash = hashlib.sha256(raw).hexdigest()
    
    cursor.execute("""
        INSERT INTO ash_strata (timestamp, layer_id, logic_state, event_payload, parent_hash, lineage_hash)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (timestamp, layer, logic_state, payload, parent_hash, lineage_hash))
    conn.commit()
    
    print("==========================================================================")
    print("      SOVEREIGN ODYSSEY // ENCOUNTER 02: OPTION ALPHA EXECUTION           ")
    print("==========================================================================")
    print(" [✓] Threshold Inversion Triggered : Underslung Kinetic Sling Activated")
    print(" [✓] Somatic Drop & Hook Complete  : CoM lowered below rail via Ω-Core lock")
    print(" [✓] Lantern Cone Evasion          : Gaze vector decoupled (215° / +45° offset)")
    print(f" [✓] Merkle Lineage Inscription   : {lineage_hash}")
    print("==========================================================================")
    conn.close()

if __name__ == "__main__":
    execute_encounter_02_alpha()
