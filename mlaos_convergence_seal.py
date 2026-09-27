import sqlite3
import hashlib
import time
import math
from typing import Tuple, Dict, Any

class BelnapDunnLattice:
    NONE = "N"
    FALSE = "F"
    TRUE = "T"
    BOTH = "B"

    @classmethod
    def arbitrate(cls, pro: bool, contra: bool) -> str:
        if pro and contra:
            return cls.BOTH
        if pro:
            return cls.TRUE
        if contra:
            return cls.FALSE
        return cls.NONE

class OuterChoirKinematics:
    @staticmethod
    def compute_slip(v_d: Tuple[float, float, float], 
                     normal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        mag = math.sqrt(sum(c**2 for c in normal))
        if mag == 0.0:
            return v_d
        n = tuple(c / mag for c in normal)
        dot = sum(vd * ni for vd, ni in zip(v_d, n))
        
        # If moving against surface, suppress normal penetration and preserve tangential slip
        if dot < 0.0:
            return tuple(round(vd - (dot * ni), 6) for vd, ni in zip(v_d, n))
        return v_d

def inspect_and_prepare_db(db_path: str = "ash_archive.db") -> Tuple[sqlite3.Connection, Dict[str, Dict[str, Any]]]:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    # Check table existence
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ash_archive';")
    if not cur.fetchone():
        cur.execute("""
        CREATE TABLE ash_archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL NOT NULL,
            layer_id INTEGER NOT NULL,
            logic_state TEXT NOT NULL,
            payload TEXT NOT NULL,
            parent_hash TEXT NOT NULL,
            lineage_hash TEXT NOT NULL
        );
        """)
        conn.commit()

    # Introspect columns: {col_name: {"type": col_type, "notnull": bool, "dflt_value": any}}
    cur.execute("PRAGMA table_info(ash_archive);")
    cols = {row[1]: {"type": row[2], "notnull": bool(row[3]), "dflt": row[4]} for row in cur.fetchall()}

    # Enforce Lex I Immutable Triggers
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS lex_i_guard_update
    BEFORE UPDATE ON ash_archive
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_VIOLATION: Ash Archive is strictly append-only. Modifying strata is prohibited.');
    END;
    """)

    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS lex_i_guard_delete
    BEFORE DELETE ON ash_archive
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_VIOLATION: Ash Archive is strictly append-only. Deleting strata is prohibited.');
    END;
    """)
    conn.commit()
    return conn, cols

def get_last_lineage_hash(cur: sqlite3.Cursor, cols: Dict[str, Any]) -> str:
    order_col = "id" if "id" in cols else ("stratum_id" if "stratum_id" in cols else "rowid")
    
    # Try preferred hash column candidates
    candidate_hash_cols = [c for c in ["lineage_hash", "hash", "merkle_root", "stratum_hash"] if c in cols]
    if not candidate_hash_cols:
        return "GENESIS_" + ("0" * 56)
    
    target_col = candidate_hash_cols[0]
    cur.execute(f"SELECT {target_col} FROM ash_archive WHERE {target_col} IS NOT NULL AND {target_col} != '' ORDER BY {order_col} DESC LIMIT 1;")
    row = cur.fetchone()
    return row[0] if (row and row[0]) else "GENESIS_" + ("0" * 56)

def append_canonical_stratum(conn: sqlite3.Connection, cols: Dict[str, Any], layer_id: int, logic_state: str, payload_str: str) -> str:
    cur = conn.cursor()
    prev_hash = get_last_lineage_hash(cur, cols)
    ts = time.time()

    # Cryptographic Merkle recurrence
    raw_header = f"{ts}:{layer_id}:{logic_state}:{payload_str}:{prev_hash}".encode("utf-8")
    lineage_hash = hashlib.sha256(raw_header).hexdigest()

    # Dynamic Field Mapping to reconcile historical schemas
    val_map = {
        "timestamp": ts,
        "time": ts,
        "created_at": ts,
        "layer_id": layer_id,
        "layer": layer_id,
        "logic_state": logic_state,
        "state": logic_state,
        "payload": payload_str,
        "event_data": payload_str,
        "data": payload_str,
        "manifest": payload_str,
        "parent_hash": prev_hash,
        "prev_hash": prev_hash,
        "lineage_hash": lineage_hash,
        "hash": lineage_hash,
        "merkle_root": lineage_hash
    }

    insert_cols = []
    insert_vals = []

    # Map available columns
    for col_name, meta in cols.items():
        if col_name in ["id", "rowid"] and "AUTOINCREMENT" in meta["type"].upper():
            continue
        if col_name in val_map:
            insert_cols.append(col_name)
            insert_vals.append(val_map[col_name])
        elif meta["notnull"] and meta["dflt"] is None:
            # Satisfy unanticipated NOT NULL columns safely
            fallback_val = 0 if "INT" in meta["type"].upper() or "REAL" in meta["type"].upper() else ""
            insert_cols.append(col_name)
            insert_vals.append(fallback_val)

    # If payload column is completely absent, add it and populate it
    if not any(c in cols for c in ["payload", "event_data", "data", "manifest"]):
        cur.execute("ALTER TABLE ash_archive ADD COLUMN payload TEXT DEFAULT '';")
        insert_cols.append("payload")
        insert_vals.append(payload_str)

    placeholders = ", ".join(["?"] * len(insert_cols))
    col_clause = ", ".join(insert_cols)
    sql = f"INSERT INTO ash_archive ({col_clause}) VALUES ({placeholders});"

    cur.execute(sql, tuple(insert_vals))
    conn.commit()
    return lineage_hash

if __name__ == "__main__":
    db, schema_cols = inspect_and_prepare_db()

    # 1. Vol. V: Paraconsistent Arbitration (Dialetheic Contradiction)
    state = BelnapDunnLattice.arbitrate(pro=True, contra=True)

    # 2. Vol. XII: Kinematic Tangential Slip Calculation
    v_des = (3.5, -4.2, 1.2)
    norm = (0.0, 1.0, 0.0)
    v_slip = OuterChoirKinematics.compute_slip(v_des, norm)

    # 3. Vol. I: Append to Ash Archive Merkle Strata
    payload_manifest = f"REVISION:OMEGA-SC-04|SLIP={v_slip}|DIALETHEIA={state}|STATUS=CONVERGED"
    tx_hash = append_canonical_stratum(db, schema_cols, layer_id=9, logic_state=state, payload_str=payload_manifest)

    print(f"[✓] Ash Archive Inscribed and Reconciled.")
    print(f"    - Merkle Lineage Hash : {tx_hash}")
    print(f"    - Belnap-Dunn State   : {state} (Harmonic Scar Grounded)")
    print(f"    - Tangential Slip     : {v_slip}")

    # 4. Lex I Immutability Verification
    try:
        cur = db.cursor()
        order_key = "id" if "id" in schema_cols else "rowid"
        cur.execute(f"UPDATE ash_archive SET {list(schema_cols.keys())[1]} = 'MUTATION_BREACH' WHERE {order_key} = 1;")
    except sqlite3.DatabaseError as err:
        print(f"[✓] Lex I Active: Direct mutation rejected -> {err}")
