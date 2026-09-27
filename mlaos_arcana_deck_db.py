import sqlite3

def initialize_arcana_registry():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE arcana_deck (
            id TEXT PRIMARY KEY,
            name TEXT,
            card_type TEXT,
            cost_strain INTEGER,
            target TEXT,
            range_ft INTEGER,
            effect_description TEXT
        )
    """)
    
    cards = [
        ('ARC-01', 'WAL Write', 'Syntax', 1, 'Self', 0, 'Immediately logs current location to Ash Archive. If downed, revert HP to 1.'),
        ('ARC-02', 'Desync Shear', 'Kinetics', 2, 'Single Entity', 30, 'Deal 2d8 Kinetic damage. Target next reaction costs +1 Strain.'),
        ('ARC-03', 'Basalt Lithify', 'Basalt', 1, 'Self / Ally', 15, 'Grant +4 Armor Density for 1 round. Converts movement to 0 ft.'),
        ('ARC-04', 'Paradox Siphon', 'Entropy', 3, 'Scar Node', 40, 'Reduce global Paradox by -1. Create 10ft Hazard Zone (1d10 Void).'),
        ('ARC-05', 'Recursive Echo', 'Recursion', 2, 'Self', 0, 'Re-execute last non-Ultimate ability used this round at 50% effectiveness.'),
        ('ARC-06', 'Scar Detonation', 'Basalt', 3, 'Scar Node', 60, 'Force targeted Scar to erupt. 3d6 Physical damage to adjacent entities.'),
        ('ARC-07', 'Frame-Skip', 'Kinetics', 1, 'Self', 0, 'Teleport 15 ft along line of sight. Bypasses opportunity attacks.'),
        ('ARC-08', 'Syntax Abort', 'Syntax', 2, 'Single Entity', 40, 'Counter incoming enemy ability. DC 15 Syntax check or lose action.'),
        ('ARC-09', 'Dialetheic Flare', 'Entropy', 2, 'Single Entity', 30, 'Force target check to evaluate as Top. 2d10 Void and +1 Paradox.'),
        ('ARC-10', 'Basalt Anchor', 'Basalt', 1, 'Scar Node', 30, 'Lock an active Scar. Immune to purging or Cascades for 2 rounds.'),
        ('ARC-11', 'Memory Purge', 'Recursion', 0, 'Self', 0, 'Burn 2 cards from Active Hand into Ash Heap to reduce Strain by -2.'),
        ('ARC-12', 'Lex I Injunction', 'Syntax', 4, 'Area 15ft', 30, 'Enforce Lex I spatial invariance across target radius.')
    ]
    
    cursor.executemany("INSERT INTO arcana_deck VALUES (?, ?, ?, ?, ?, ?, ?)", cards)
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM arcana_deck")
    count = cursor.fetchone()[0]
    print(f"[SUCCESS] Initialized Ignition Arcana Registry with {count} canonical runtime cards.")
    
    cursor.execute("SELECT id, name, card_type, cost_strain FROM arcana_deck LIMIT 5")
    for row in cursor.fetchall():
        print(f"Card {row[0]} | Name: {row[1]} | Type: {row[2]} | Strain Cost: {row[3]}")
        
    conn.close()

if __name__ == "__main__":
    initialize_arcana_registry()
