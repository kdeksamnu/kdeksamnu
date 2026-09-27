import sqlite3
import random

def simulate_ontological_cascade():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE paradox_economy (
            global_paradox INTEGER CHECK(global_paradox BETWEEN 0 AND 5),
            cascade_active BOOLEAN,
            active_domain_roll INTEGER
        )
    """)
    
    cursor.execute("""
        CREATE TABLE operator_strain (
            operator_id TEXT PRIMARY KEY,
            strain INTEGER,
            hp INTEGER
        )
    """)
    
    cursor.execute("INSERT INTO paradox_economy VALUES (5, 0, NULL)")
    cursor.execute("INSERT INTO operator_strain VALUES ('ash_registrar_01', 4, 30)")
    conn.commit()
    
    print("--- PARADOX THRESHOLD REACHED: 5/5 ---")
    print("[Phase 1: Immediate System Freeze & WAL Flush Triggered]")
    
    # Flush Strain, apply Syntax Damage (1d6 per strain point cleared, simulated roll = 3 per strain)
    cursor.execute("SELECT operator_id, strain, hp FROM operator_strain WHERE operator_id = 'ash_registrar_01'")
    op = cursor.fetchone()
    strain_cleared = op[1]
    syntax_damage = strain_cleared * 3  # simulated average/roll
    new_hp = op[2] - syntax_damage
    
    cursor.execute("UPDATE operator_strain SET strain = 0, hp = ? WHERE operator_id = 'ash_registrar_01'", (new_hp,))
    cursor.execute("UPDATE paradox_economy SET global_paradox = 0, cascade_active = 1, active_domain_roll = 3")
    conn.commit()
    
    cursor.execute("SELECT global_paradox, cascade_active, active_domain_roll FROM paradox_economy")
    econ = cursor.fetchone()
    
    cursor.execute("SELECT operator_id, strain, hp FROM operator_strain WHERE operator_id = 'ash_registrar_01'")
    updated_op = cursor.fetchone()
    
    print(f"Global Paradox Track Reset: {econ[0]}/5 | Cascade Active: {bool(econ[1])}")
    print(f"Ontological Cascade Domain Rolled: [d10 = {econ[2]}] -> Dialetheic Overlap (Top Flood)")
    print(f"Operator [{updated_op[0]}] Strain Reset: {updated_op[1]} | HP after Syntax Damage ({syntax_damage}): {updated_op[2]}")
    conn.close()

if __name__ == "__main__":
    simulate_ontological_cascade()
