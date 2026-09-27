from fastapi import FastAPI
from engine.api.routes import visuals, spectral

app = FastAPI(title="MLAOS-Prime // Cathedral-Engine Core")

app.include_router(visuals.router)
app.include_router(spectral.router)

@app.get("/")
def read_root():
    return {"status": "resonant", "engine": "MLAOS-Prime"}

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
