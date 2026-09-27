import sqlite3
import json
import hashlib

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def canonical_json(obj: dict) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

def commit_actuation_node():
    conn = sqlite3.connect("cathedral_engine_sigma12.db")
    conn.execute("PRAGMA foreign_keys = ON;")
    
    # Define payload reflecting the latched actuation telemetry
    payload = {
        "event_type": "PHYSICAL_ACTUATION_COMMITTED",
        "certificate_id": "sha256_hash",
        "action_executed": "OPEN_HIGH_PRESSURE_VALVE",
        "valve_position": 1.0,
        "manifold_pressure_psi": 14.7,
        "thermal_delta_rate_hz": 0.0,
        "actuator_status": "LATCHED_EXECUTION"
    }
    
    canonical_payload = canonical_json(payload)
    node_hash = sha256_hex(canonical_payload)
    merkle_root = sha256_hex(node_hash + "telemetry_leaf")
    
    # Retrieve active confluent parent hash from DB
    cursor = conn.cursor()
    cursor.execute("SELECT node_hash FROM ash_nodes ORDER BY rowid DESC LIMIT 1;")
    row = cursor.fetchone()
    parent_hash = row[0] if row else "0dff0620e63d72a6"
    
    try:
        cursor.execute(
            """
            INSERT INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (node_hash, "master_reunified", 4, merkle_root, canonical_payload)
        )
        cursor.execute(
            """
            INSERT INTO ash_dag_edges (parent_hash, child_hash, edge_type)
            VALUES (?, ?, ?)
            """,
            (parent_hash, node_hash, "actuation_commit")
        )
        conn.commit()
        print(f"[CHAMBER Σ-7] Telemetry node successfully committed to Ash Archive DAG.")
        print(f"Node Hash:  {node_hash}")
        print(f"Parent Edge: {parent_hash[:16]}... -> {node_hash[:16]}...")
    except sqlite3.IntegrityError as e:
        print(f"[LEX I BREACH INTERCEPTED]: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    commit_actuation_node()
