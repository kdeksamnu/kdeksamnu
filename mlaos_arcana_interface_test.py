import sqlite3

def test_arcana_interface():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE arcana_cards (
            id TEXT PRIMARY KEY,
            name TEXT,
            card_type TEXT,
            cost_strain INTEGER,
            target TEXT,
            range_ft INTEGER,
            ash_interaction TEXT
        )
    """)
    
    cursor.execute("""
        INSERT INTO arcana_cards VALUES 
        ('ARC-01', 'Write-Ahead Collapse', 'Syntax', 2, 'Single_Entity', 30, 'Standard_Discard')
    """)
    conn.commit()
    
    cursor.execute("SELECT id, name, card_type, cost_strain, target, range_ft, ash_interaction FROM arcana_cards WHERE id = 'ARC-01'")
    card = cursor.fetchone()
    print(f"Verified Arcana Interface Mapping -> ID: {card[0]} | Name: {card[1]} | Type: {card[2]} | Strain Cost: {card[3]} | Target: {card[4]} | Range: {card[5]} ft | Ash Action: {card[6]}")
    conn.close()

if __name__ == "__main__":
    test_arcana_interface()
