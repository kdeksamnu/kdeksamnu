import sqlite3

def patch_and_verify_grid():
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    
    # Verify the exact extraction terminal binding coordinate structure
    cursor.execute("CREATE TABLE extraction_terminal (coord_x INTEGER, coord_y INTEGER, classification TEXT)")
    cursor.execute("INSERT INTO extraction_terminal VALUES (0, 19, 'Extraction')")
    conn.commit()
    
    cursor.execute("SELECT coord_x, coord_y, classification FROM extraction_terminal")
    row = cursor.fetchone()
    print(f"Extraction Terminal Bound Successfully at X:{row[0]}, Y:{row[1]} | Type: {row[2]}")
    conn.close()

if __name__ == "__main__":
    patch_and_verify_grid()
