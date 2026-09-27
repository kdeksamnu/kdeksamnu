import sqlite3
import hashlib
import time
import math
from typing import Tuple, Dict, Any

class BelnapDunn:
    NONE = "N"
    FALSE = "F"
    TRUE = "T"
    BOTH = "B"

    @classmethod
    def evaluate(cls, pro: bool, contra: bool) -> str:
        if pro and contra:
            return cls.BOTH  # Harmonic Scar: Contradiction load-bearing
        if pro:
            return cls.TRUE
        if contra:
            return cls.FALSE
        return cls.NONE

class KinematicResolver:
    @staticmethod
    def resolve_contact(v_incoming: Tuple[float, float, float], 
                        surface_normal: Tuple[float, float, float]) -> Tuple[Tuple[float, float, float], float]:
        mag = math.sqrt(sum(c**2 for c in surface_normal))
        if mag == 0.0:
            return v_incoming, 0.0
        n = tuple(c / mag for c in surface_normal)
        
        # Calculate normal load
        dot = sum(vi * ni for vi, ni in zip(v_incoming, n))
        
        # If moving into the surface, suppress normal component and extract tangential momentum
        if dot < 0.0:
            v_t = tuple(round(vi - (dot * ni), 4) for vi, ni in zip(v_incoming, n))
            absorbed_load = round(abs(dot), 4)
            return v_t, absorbed_load
        return v_incoming, 0.0

def init_campaign_db(db_path: str = "sovereign_odyssey.db"):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("PRAGMA journal_mode = WAL;")
    cur.execute("PRAGMA synchronous = NORMAL;")

    # 1. Nonary State Vector Ledger
    cur.execute("""
    CREATE TABLE IF NOT EXISTS entity_state (
        entity_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        anatomy TEXT NOT NULL,
        inscription_state TEXT NOT NULL,
        material_tier TEXT NOT NULL,
        vel_x REAL NOT NULL,
        vel_y REAL NOT NULL,
        vel_z REAL NOT NULL,
        gaze_azimuth REAL NOT NULL,
        provenance_root TEXT NOT NULL,
        updated_at REAL NOT NULL
    );
    """)

    # 2. Immutable Ash Archive Strata
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ash_strata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp REAL NOT NULL,
        layer_id INTEGER NOT NULL,
        logic_state TEXT NOT NULL,
        event_payload TEXT NOT NULL,
        parent_hash TEXT NOT NULL,
        lineage_hash TEXT NOT NULL
    );
    """)

    # 3. Enforce Lex I Immutability
    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS abort_strata_tampering
    BEFORE UPDATE ON ash_strata
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_BREACH: Strata in the Ash Archive cannot be modified.');
    END;
    """)

    cur.execute("""
    CREATE TRIGGER IF NOT EXISTS abort_strata_deletion
    BEFORE DELETE ON ash_strata
    BEGIN
        SELECT RAISE(FAIL, 'LEX_I_BREACH: Strata in the Ash Archive cannot be deleted.');
    END;
    """)

    conn.commit()
    return conn

def append_campaign_event(conn: sqlite3.Connection, layer: int, state: str, payload: str) -> str:
    cur = conn.cursor()
    cur.execute("SELECT lineage_hash FROM ash_strata ORDER BY id DESC LIMIT 1;")
    row = cur.fetchone()
    parent_hash = row[0] if row else "GENESIS_" + ("0" * 56)

    ts = time.time()
    raw = f"{ts}:{layer}:{state}:{payload}:{parent_hash}".encode('utf-8')
    lineage_hash = hashlib.sha256(raw).hexdigest()

    cur.execute("""
        INSERT INTO ash_strata (timestamp, layer_id, logic_state, event_payload, parent_hash, lineage_hash)
        VALUES (?, ?, ?, ?, ?, ?);
    """, (ts, layer, state, payload, parent_hash, lineage_hash))
    conn.commit()
    return lineage_hash

if __name__ == "__main__":
    db = init_campaign_db()

    print("[*] Instantiating Sovereign Odyssey Engine...")
    print("[*] Enacting Movement I: Initializing Protagonist Kaelen...")

    # Register Kaelen with Nonary State Vector
    cur = db.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO entity_state 
        VALUES ('ENT_01', 'Kaelen', 'Tensegrity_Fascia', 'B', 'Ballistic_Denim', 1.2, 0.0, 0.8, 45.0, 'PROV_CARTOGRAPHER_09', ?);
    """, (time.time(),))
    db.commit()

    # Simulate Movement IV: Contact Architecture Strike & Choir-Slip
    incoming_strike = (4.5, -6.0, 0.5)  # Heavy downward slash
    guard_normal = (0.0, 1.0, 0.0)      # Upward angled parry shield

    v_slip, load = KinematicResolver.resolve_contact(incoming_strike, guard_normal)
    combat_dialectic = BelnapDunn.evaluate(pro=True, contra=True)

    event_summary = (
        f"COMBAT_RESOLVE|ENT=Kaelen|STRIKE={incoming_strike}|NORMAL={guard_normal}|"
        f"SLIP_VECTOR={v_slip}|SHED_LOAD_KN={load}|LATTICE={combat_dialectic}"
    )

    h_event = append_campaign_event(db, layer=4, state=combat_dialectic, payload=event_summary)

    print(f"[✓] Stratum Sealed into Campaign Ledger.")
    print(f"    - Merkle Root  : {h_event}")
    print(f"    - Inscription  : Lattice {combat_dialectic} (Harmonic Scar Grounded)")
    print(f"    - Deflection   : Normal load of {load} kN shed; Tangential momentum preserved at {v_slip}")

    # Verify Lex I Enforcement
    try:
        cur.execute("UPDATE ash_strata SET event_payload = 'RETCON_VIOLATION' WHERE id = 1;")
    except sqlite3.DatabaseError as e:
        print(f"[✓] Lex I Active: Historical tampering rejected -> {e}")
