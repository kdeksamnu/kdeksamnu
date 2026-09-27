import sqlite3

def initialize_index_threshold_grid():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    cursor.executescript("""
        CREATE TABLE grid_tiles (
            coord_x INTEGER,
            coord_y INTEGER,
            terrain_type TEXT,
            hazard_effect TEXT,
            PRIMARY KEY (coord_x, coord_y)
        );
        
        CREATE TABLE scenario_entities (
            entity_id TEXT PRIMARY KEY,
            name TEXT,
            role TEXT,
            pos_x INTEGER,
            pos_y INTEGER
        );
    """)
    
    # Populate key landmark coordinates for Gap 03: The Index Threshold (16x20 grid, X:0-15, Y:0-19)
    # Player Starts: P1 (01,03), P2 (14,03), P3 (07,02)
    # Scar Anchors: S1 (04,09), S2 (11,09), S3 (07,18)
    # Index Threshold Altar: (08,11) to (09,12)
    # Extraction Terminal: (00,19)
    landmarks = [
        (1, 3, 'Player_Start', 'None'),
        (14, 3, 'Player_Start', 'None'),
        (7, 2, 'Player_Start', 'None'),
        (4, 9, 'Scar_Anchor', 'Dialetheic Anchor Node'),
        (11, 9, 'Scar_Anchor', 'Dialetheic Anchor Node'),
        (7, 18, 'Scar_Anchor', 'Dialetheic Anchor Node'),
        (8, 11, 'Index_Threshold', 'Central Altar Core'),
        (9, 11, 'Index_Threshold', 'Central Altar Core'),
        (8, 12, 'Index_Threshold', 'Central Altar Core'),
        (9, 12, 'Index_Threshold', 'Central Altar Core'),
        (0, 19, 'Extraction_Terminal', 'Stabilization Exit'),
    ]
    
    cursor.executemany("INSERT INTO grid_tiles VALUES (?, ?, ?, ?)", landmarks)
    
    entities = [
        ('P1', 'Ash Registrar', 'Player', 1, 3),
        ('P2', 'Latency Blade', 'Player', 14, 3),
        ('P3', 'Scar Carver', 'Player', 7, 2),
        ('ARBITER-01', 'ARBITER_MAGISTER_01', 'Boss', 0, 19)
    ]
    
    cursor.executemany("INSERT INTO scenario_entities VALUES (?, ?, ?, ?, ?)", entities)
    conn.commit()
    
    print("==========================================================================")
    print("           GAP 03: THE INDEX THRESHOLD — BATTLEFIELD TOPOGRAPHY           ")
    print("==========================================================================")
    
    cursor.execute("SELECT entity_id, name, role, pos_x, pos_y FROM scenario_entities")
    for row in cursor.fetchall():
        print(f"Entity [{row[0]}] {row[1]} ({row[2]}) positioned at X:{row[3]}, Y:{row[4]}")
        
    cursor.execute("SELECT coord_x, coord_y, terrain_type, hazard_effect FROM grid_tiles")
    print("\n[Key Strategic Nodes Initialized]")
    for row in cursor.fetchall():
        print(f"Coordinate ({row[0]}, {row[1]}) -> Type: {row[2]} | Effect: {row[3]}")
        
    conn.close()

if __name__ == "__main__":
    initialize_index_threshold_grid()
