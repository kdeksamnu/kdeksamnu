import os

main_path = "main.py"
if os.path.exists(main_path):
    with open(main_path, "r") as f:
        content = f.read()
    
    print("[OK] Reading existing main.py...")
    if "/health" not in content:
        print("[INFO] Injecting /health and Ash Archive Merkle root routes into main.py...")
        patch = """
@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "system": "MLAOS-Prime Cathedral-Engine", "governance": "Lex I"}

@app.get("/api/v1/ash/merkle/root")
def get_merkle_root():
    import sqlite3
    try:
        conn = sqlite3.connect("cathedral_ash_archive.db")
        cur = conn.cursor()
        cur.execute("SELECT merkle_root FROM ash_nodes ORDER BY rowid DESC LIMIT 1;")
        row = cur.fetchone()
        conn.close()
        return {"terminal_merkle_root": row[0] if row else "NO_NODES_COMMITTED"}
    except Exception as e:
        return {"error": str(e)}
"""
        with open(main_path, "a") as f:
            f.write(patch)
        print("[OK] main.py successfully patched with telemetry routes.")
    else:
        print("[OK] Telemetry routes already present in main.py.")
else:
    print("[ERROR] main.py not found in working directory.")
