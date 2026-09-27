import os

main_path = "main.py"
if os.path.exists(main_path):
    with open(main_path, "r") as f:
        content = f.read()
    
    if "/api/v1/ash/query/temporal" not in content:
        temporal_patch = """
@app.get("/api/v1/ash/query/temporal")
def query_temporal_strata(epoch: int = None):
    import sqlite3
    try:
        conn = sqlite3.connect("cathedral_ash_archive.db")
        cur = conn.cursor()
        if epoch is not None:
            cur.execute("SELECT node_hash, branch_name, epoch, merkle_root FROM ash_nodes WHERE epoch = ?", (epoch,))
        else:
            cur.execute("SELECT node_hash, branch_name, epoch, merkle_root FROM ash_nodes ORDER BY epoch ASC")
        rows = cur.fetchall()
        conn.close()
        return {
            "query_status": "SUCCESS",
            "governance": "Lex I",
            "strata_count": len(rows),
            "records": [{"node_hash": r[0], "branch": r[1], "epoch": r[2], "merkle_root": r[3]} for r in rows]
        }
    except Exception as e:
        return {"error": str(e)}
"""
        with open(main_path, "a") as f:
            f.write(temporal_patch)
        print("[OK] Temporal query route successfully injected into main.py.")
    else:
        print("[INFO] Temporal route already exists.")
