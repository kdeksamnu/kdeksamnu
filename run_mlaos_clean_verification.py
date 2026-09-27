#!/usr/bin/env python3
"""
RUN_MLAO_CLEAN_VERIFICATION.PY (Complete Rewrite - Strict Isolation & Manual Transaction Control)
"""

import sqlite3
import hashlib
import time
import math
from dataclasses import dataclass
from typing import Tuple

DB_PATH = "cathedral_ash_archive.db"

@dataclass
class Vector3D:
    x: float
    y: float
    z: float

    def dot(self, other: 'Vector3D') -> float:
        return self.x * other.x + self.y * other.y + self.z * other.z

    def magnitude(self) -> float:
        return math.sqrt(self.dot(self))

    def normalize(self) -> 'Vector3D':
        mag = self.magnitude()
        return Vector3D(self.x / mag, self.y / mag, self.z / mag) if mag > 0 else Vector3D(0.0, 0.0, 0.0)

    def scale(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)

    def subtract(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __repr__(self) -> str:
        return f"[{self.x:.3f}, {self.y:.3f}, {self.z:.3f}]"

class AshArchiveRewrittenRuntime:
    def __init__(self, db_path=DB_PATH):
        # Disable implicit transactions to take absolute control of transaction boundaries
        self.conn = sqlite3.connect(db_path, isolation_level=None)
        self.cur = self.conn.cursor()
        self._init_schema()

    def _init_schema(self):
        self.cur.execute("BEGIN EXCLUSIVE;")
        try:
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS ash_archive (
                    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    parent_hash TEXT NOT NULL,
                    logical_clock INTEGER NOT NULL,
                    belnap_state TEXT NOT NULL,
                    desired_vector TEXT NOT NULL,
                    executed_vector TEXT NOT NULL,
                    strain_energy REAL NOT NULL,
                    lineage_hash TEXT NOT NULL,
                    timestamp REAL NOT NULL
                );
            """)
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS harmonic_scars (
                    scar_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id INTEGER NOT NULL,
                    spatial_coordinate TEXT NOT NULL,
                    load_bearing_capacity REAL NOT NULL,
                    FOREIGN KEY(event_id) REFERENCES ash_archive(event_id)
                );
            """)

            # Enforce Lex I Triggers via RAISE(ROLLBACK)
            self.cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_update_archive;")
            self.cur.execute("""
                CREATE TRIGGER prevent_lex_i_update_archive
                BEFORE UPDATE ON ash_archive
                BEGIN
                    SELECT RAISE(ROLLBACK, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
                END;
            """)
            self.cur.execute("DROP TRIGGER IF EXISTS prevent_lex_i_delete_archive;")
            self.cur.execute("""
                CREATE TRIGGER prevent_lex_i_delete_archive
                BEFORE DELETE ON ash_archive
                BEGIN
                    SELECT RAISE(ROLLBACK, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
                END;
            """)
            self.cur.execute("COMMIT;")
        except Exception as e:
            self.cur.execute("ROLLBACK;")
            raise e

    def get_latest_hash(self) -> str:
        self.cur.execute("SELECT lineage_hash FROM ash_archive ORDER BY event_id DESC LIMIT 1;")
        row = self.cur.fetchone()
        return row[0] if row else "GENESIS_ROOT_REWRITTEN_00000000"

    def commit_stratum(self, clock: int, state: str, v_d: Vector3D, v_exec: Vector3D, strain: float) -> Tuple[int, str]:
        parent_hash = self.get_latest_hash()
        ts = time.time()
        raw_payload = f"{parent_hash}:{clock}:{state}:{v_d}:{v_exec}:{strain:.4f}:{ts}"
        lineage_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

        self.cur.execute("BEGIN EXCLUSIVE;")
        try:
            self.cur.execute("""
                INSERT INTO ash_archive (parent_hash, logical_clock, belnap_state, desired_vector, executed_vector, strain_energy, lineage_hash, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """, (parent_hash, clock, state, str(v_d), str(v_exec), strain, lineage_hash, ts))
            
            event_id = self.cur.lastrowid
            if state == "B" and strain > 0.0:
                load_capacity = strain * 1.618
                self.cur.execute("""
                    INSERT INTO harmonic_scars (event_id, spatial_coordinate, load_bearing_capacity)
                    VALUES (?, ?, ?);
                """, (event_id, str(v_exec), load_capacity))
            self.cur.execute("COMMIT;")
        except Exception as e:
            self.cur.execute("ROLLBACK;")
            raise e

        return event_id, lineage_hash

def main():
    print("[*] Initializing Rewritten MLAOS-Prime Runtime...")
    archive = AshArchiveRewrittenRuntime()

    print("\n--- [PHASE 1: VOL. V PARACONSISTENT INGESTION] ---")
    belnap_state = "B"
    print(f"  [+] Belnap-Dunn Evaluated State: [{belnap_state}] (Both: Contradiction Retained)")

    print("\n--- [PHASE 2: VOL. XII TANGENTIAL CHOIR-SLIP] ---")
    v_desired = Vector3D(12.0, 0.0, 0.0)
    boundary_normal = Vector3D(-0.7071, 0.7071, 0.0)
    penetration = v_desired.dot(boundary_normal.normalize())
    v_slip = v_desired.subtract(boundary_normal.normalize().scale(penetration)) if penetration < 0 else v_desired
    strain = abs(penetration) if penetration < 0 else 0.0
    print(f"  [+] Kinematic Redirection: {v_slip} | Induced Strain: {strain:.3f} J")

    print("\n--- [PHASE 3: VOL. I LEX I INSCRIPTION & SCAR CRYSTALLIZATION] ---")
    event_id, lineage_hash = archive.commit_stratum(clock=301, state=belnap_state, v_d=v_desired, v_exec=v_slip, strain=strain)
    print(f"  [+] Event Committed: Index #{event_id}")
    print(f"  [+] Merkle Lineage Inscription: {lineage_hash}")

    print("\n--- [PHASE 4: BARE-METAL LEX I TRIGGER VERIFICATION] ---")
    archive.cur.execute("BEGIN EXCLUSIVE;")
    try:
        archive.cur.execute(f"UPDATE ash_archive SET belnap_state = 'T' WHERE event_id = {event_id};")
        archive.cur.execute("COMMIT;")
        raise RuntimeError("FATAL: Lex I Breach! Table permitted silent revision.")
    except sqlite3.IntegrityError as e:
        archive.cur.execute("ROLLBACK;")
        print(f"  [✓] Lex I Guard Confirmed: UPDATE successfully intercepted via ROLLBACK -> {e}")

    print("\n[✓] THREE-VOLUME CONVERGENCE SEALED: Memory Intact · Logic Sound · Motion Feasible.")

if __name__ == "__main__":
    main()
