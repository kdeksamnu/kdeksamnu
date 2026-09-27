#!/usr/bin/env python3
"""
FIX_AND_RUN_RUNTIME.PY
Adapts schema of existing cathedral_ash_archive.db to include lineage_hash,
enforces Lex I triggers, and executes the three-volume convergence test.
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

class AshArchiveAdaptiveRuntime:
    def __init__(self, db_path=DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._ensure_schema_compliance()

    def _ensure_schema_compliance(self):
        # 1. Create table if missing entirely
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

        # 2. Inspect existing columns for migration if table pre-existed
        self.cur.execute("PRAGMA table_info(ash_archive);")
        columns = {row[1] for row in self.cur.fetchall()}

        required_columns = {
            "parent_hash": "TEXT NOT NULL DEFAULT 'GENESIS_ROOT'",
            "logical_clock": "INTEGER NOT NULL DEFAULT 0",
            "belnap_state": "TEXT NOT NULL DEFAULT 'N'",
            "desired_vector": "TEXT NOT NULL DEFAULT '[0,0,0]'",
            "executed_vector": "TEXT NOT NULL DEFAULT '[0,0,0]'",
            "strain_energy": "REAL NOT NULL DEFAULT 0.0",
            "lineage_hash": "TEXT NOT NULL DEFAULT 'PENDING_HASH'",
            "timestamp": "REAL NOT NULL DEFAULT 0.0"
        }

        for col_name, col_def in required_columns.items():
            if col_name not in columns:
                print(f"  [!] Migrating Schema: Adding missing column [{col_name}]...")
                self.cur.execute(f"ALTER TABLE ash_archive ADD COLUMN {col_name} {col_def};")

        # 3. Harmonic scars table
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS harmonic_scars (
                scar_id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id INTEGER NOT NULL,
                spatial_coordinate TEXT NOT NULL,
                load_bearing_capacity REAL NOT NULL,
                FOREIGN KEY(event_id) REFERENCES ash_archive(event_id)
            );
        """)

        # 4. Enforce Lex I Never-Overwrite Doctrine Triggers
        self.cur.execute("""
            DROP TRIGGER IF EXISTS prevent_lex_i_update_archive;
        """)
        self.cur.execute("""
            CREATE TRIGGER prevent_lex_i_update_archive
            BEFORE UPDATE ON ash_archive
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
            END;
        """)

        self.cur.execute("""
            DROP TRIGGER IF EXISTS prevent_lex_i_delete_archive;
        """)
        self.cur.execute("""
            CREATE TRIGGER prevent_lex_i_delete_archive
            BEFORE DELETE ON ash_archive
            BEGIN
                SELECT RAISE(FAIL, 'LEX I VIOLATION: Ash Archive historical strata are immutable.');
            END;
        """)
        self.conn.commit()

    def get_latest_hash(self) -> str:
        self.cur.execute("SELECT lineage_hash FROM ash_archive ORDER BY event_id DESC LIMIT 1;")
        row = self.cur.fetchone()
        return row[0] if row and row[0] != 'PENDING_HASH' else "GENESIS_ROOT_a4f8e12d00000000"

    def commit_stratum(self, clock: int, state: str, v_d: Vector3D, v_exec: Vector3D, strain: float) -> Tuple[int, str]:
        parent_hash = self.get_latest_hash()
        ts = time.time()
        raw_payload = f"{parent_hash}:{clock}:{state}:{v_d}:{v_exec}:{strain:.4f}:{ts}"
        lineage_hash = hashlib.sha256(raw_payload.encode()).hexdigest()

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

        self.conn.commit()
        return event_id, lineage_hash

def main():
    print("[*] Initializing Adaptive MLAOS-Prime Foundation Engine...")
    archive = AshArchiveAdaptiveRuntime()

    v_desired = Vector3D(12.0, 0.0, 0.0)
    boundary_normal = Vector3D(-0.7071, 0.7071, 0.0)
    
    # Choir-Slip calculation
    penetration = v_desired.dot(boundary_normal.normalize())
    v_slip = v_desired.subtract(boundary_normal.normalize().scale(penetration)) if penetration < 0 else v_desired
    strain = abs(penetration) if penetration < 0 else 0.0

    print(f"  [+] Executed Tangent Vector: {v_slip} | Strain: {strain:.3f} J")

    event_id, lineage_hash = archive.commit_stratum(
        clock=301, 
        state="B", 
        v_d=v_desired, 
        v_exec=v_slip, 
        strain=strain
    )
    print(f"  [+] Stratum Inscribed Successfully: Index #{event_id}")
    print(f"  [+] Merkle Lineage Inscription: {lineage_hash}")

    # Verify Lex I Guard
    try:
        archive.cur.execute(f"UPDATE ash_archive SET belnap_state = 'T' WHERE event_id = {event_id};")
        raise RuntimeError("FATAL: Lex I Breach! Table permitted silent revision.")
    except sqlite3.IntegrityError as e:
        print(f"  [✓] Lex I Guard Confirmed: UPDATE intercepted -> {e}")

    print("\n[✓] CONVERGENCE REPAIRED AND SEALED UNDER LEX I.")

if __name__ == "__main__":
    main()
