import asyncio
import hashlib
import json
import sqlite3
import time
import httpx

DB_PATH = "ash_archive_vault.db"
FORK_ENDPOINT = "http://localhost:8001/visuals/duplicate"
PRIMARY_PARENT_HASH = "fc3bb6f588210b4700fa0182f185900ec39ce3b37a45613a994f9dc16adbe187"

def init_vault():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS merkle_dag_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            target TEXT,
            somatic_integrity REAL,
            harmonic_scars INTEGER,
            state_hash TEXT,
            parent_hash TEXT,
            dag_status TEXT
        )
    """)
    conn.commit()
    conn.close()

async def sync_loop():
    init_vault()
    print("[CATHEDRAL-DAEMON] Ash Archive Merkle DAG Sync Daemon active.")
    
    async with httpx.AsyncClient() as client:
        while True:
            try:
                payload = {
                    "target": "Chaos-Subject",
                    "somatic_integrity": 0.6500,
                    "harmonic_scars": 11,
                    "logic_state": True,
                    "lineage_depth": "Depth 98 (Step 106 / 204)",
                    "parent_hash": PRIMARY_PARENT_HASH
                }
                
                response = await client.post(FORK_ENDPOINT, json=payload, timeout=5.0)
                if response.status_code == 200:
                    data = response.json().get("replicated_observer_node", {})
                    
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO merkle_dag_ledger 
                        (timestamp, target, somatic_integrity, harmonic_scars, state_hash, parent_hash, dag_status)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (
                        time.time(),
                        data.get("target"),
                        data.get("somatic_integrity"),
                        data.get("harmonic_scars"),
                        data.get("state_hash"),
                        data.get("parent_hash"),
                        data.get("dag_status")
                    ))
                    conn.commit()
                    conn.close()
                    print(f"[SYNC SUCCESS] Committed Hash: {data.get('state_hash')} | Status: {data.get('dag_status')}")
                else:
                    print(f"[SYNC WARNING] Endpoint returned status {response.status_code}")
            
            except Exception as e:
                print(f"[SYNC ERROR] Connection failure to fork endpoint: {e}")
            
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(sync_loop())
