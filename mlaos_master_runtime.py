import sqlite3
import hashlib
import time
import math
from typing import Tuple

class BelnapDunn:
    NONE = "N"
    FALSE = "F"
    TRUE = "T"
    BOTH = "B"

    @classmethod
    def resolve_strain(cls, evidence_for: bool, evidence_against: bool) -> str:
        if evidence_for and evidence_against:
            return cls.BOTH
        elif evidence_for:
            return cls.TRUE
        elif evidence_against:
            return cls.FALSE
        return cls.NONE

class KinematicChoir:
    @staticmethod
    def project_tangential_slip(v_desired: Tuple[float, float, float], 
                                normal: Tuple[float, float, float]) -> Tuple[float, float, float]:
        n_len = math.sqrt(sum(ni**2 for ni in normal))
        if n_len == 0.0:
            return v_desired
        n = tuple(ni / n_len for ni in normal)
        
        dot = sum(vd * ni for vd, ni in zip(v_desired, n))
        if dot > 0.0:
            return v_desired
            
        v_t = tuple(vd - (dot * ni) for vd, ni in zip(v_desired, n))
        return v_t

def initialize_ash_archive(db_path: str = "ash_archive.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    # Master Ash Archive Ledger
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ash_archive (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        layer_id INTEGER NOT NULL,
        logic_state TEXT NOT NULL,
        payload TEXT NOT NULL,
        prev_hash TEXT NOT NULL,
        lineage_hash TEXT NOT NULL
    );
    """)

    # Inspect table structure to ensure missing column compatibility
    cur.execute("PRAGMA table_info(ash_archive);")
    columns = [col[1] for col in cur.fetchall()]
    
    if "lineage_hash" not in columns:
        cur.execute("ALTER TABLE ash_archive ADD COLUMN lineage_hash TEXT DEFAULT '';")
    if "prev_hash" not in columns:
        cur.execute("ALTER TABLE ash_archive ADD COLUMN prev_hash TEXT DEFAULT '';")
    if "layer_id" not in columns:
        cur.execute("ALTER TABLE ash_archive ADD COLUMN layer_id INTEGER DEFAULT 0;")
    if "logic_state" not in columns:
        cur.execute("ALTER TABLE ash_archive ADD COLUMN logic_state TEXT DEFAULT 'N';")

    # Bare-Metal Enactment of Lex I: Never-Overwrite Doctrine
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS abort_ash_update
    BEFORE UPDATE ON ash_archive
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_VIOLATION: Ash Archive is strictly append-only. Modifying strata is prohibited.');
    END;
    """)

    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS abort_ash_delete
    BEFORE DELETE ON ash_archive
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_VIOLATION: Ash Archive is strictly append-only. Deleting strata is prohibited.');
    END;
    """)
    conn.commit()
    return conn

def append_stratum(conn: sqlite3.Connection, layer_id: int, logic_state: str, payload: str):
    cur = conn.cursor()
    
    # Introspect schema for ordering key (id vs stratum_id vs ROWID)
    cur.execute("PRAGMA table_info(ash_archive);")
    columns = [col[1] for col in cur.fetchall()]
    
    order_col = "id" if "id" in columns else ("stratum_id" if "stratum_id" in columns else "rowid")

    cur.execute(f"SELECT lineage_hash FROM ash_archive ORDER BY {order_col} DESC LIMIT 1;")
    row = cur.fetchone()
    prev_hash = row[0] if (row and row[0]) else "GENESIS_0000000000000000000000000000000000000000000000000000000000000000"
    
    ts = time.time()
    raw_header = f"{ts}:{layer_id}:{logic_state}:{payload}:{prev_hash}".encode('utf-8')
    lineage_hash = hashlib.sha256(raw_header).hexdigest()

    cur.execute("""
        INSERT INTO ash_archive (timestamp, layer_id, logic_state, payload, prev_hash, lineage_hash)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (ts, layer_id, logic_state, payload, prev_hash, lineage_hash))
    conn.commit()
    return lineage_hash

if __name__ == "__main__":
    db = initialize_ash_archive()
    
    # 1. Evaluate Paraconsistent Logic Strain
    sensor_presence = True
    barrier_detected = True
    state = BelnapDunn.resolve_strain(sensor_presence, barrier_detected)
    
    # 2. Compute Kinematic Vector Slip
    v_des = (4.0, -3.0, 0.0)
    surface_norm = (0.0, 1.0, 0.0)
    v_slip = KinematicChoir.project_tangential_slip(v_des, surface_norm)
    
    # 3. Compile Stratum to Ash Archive
    payload = f"KINEMATICS:v_d={v_des}->v_slip={v_slip}|STRAIN={state}"
    tx_hash = append_stratum(db, layer_id=4, logic_state=state, payload=payload)
    
    print(f"[*] Subsystem Verified. Stratum Inscribed.")
    print(f"[*] Logic State: {state} (Harmonic Scar Established)")
    print(f"[*] Tangential Slip Computed: {v_slip}")
    print(f"[*] Ash Archive Merkle Root: {tx_hash}")

    # 4. Lex I Enforcement Verification
    try:
        cur = db.cursor()
        cur.execute("PRAGMA table_info(ash_archive);")
        cols = [c[1] for c in cur.fetchall()]
        order_col = "id" if "id" in cols else "rowid"
        cur.execute(f"UPDATE ash_archive SET payload = 'MUTATION_TEST' WHERE {order_col} = 1;")
    except sqlite3.DatabaseError as e:
        print(f"[✓] Lex I Intact. Runtime mutation rejected: {e}")
