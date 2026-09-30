import hashlib
import sqlite3
from typing import Dict, Any

class MerkleArchiveVerifier:
    @staticmethod
    def compute_hash(parent_hash: str, payload: str) -> str:
        raw = f"{parent_hash}:{payload}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    @classmethod
    def verify_chain(cls, db_path: str = "ash_archive.db") -> Dict[str, Any]:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT event_id, payload, parent_hash, current_hash FROM event_log ORDER BY sequence_id ASC")
            rows = cursor.fetchall()

        if not rows:
            return {"valid": True, "depth": 0, "terminal_hash": "0"*64}

        prev_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        depth = 0

        for event_id, payload, parent_hash, current_hash in rows:
            if parent_hash != prev_hash:
                return {"valid": False, "failed_at": event_id, "reason": "Parent hash mismatch"}
            
            calculated = cls.compute_hash(parent_hash, payload)
            if calculated != current_hash:
                return {"valid": False, "failed_at": event_id, "reason": "Hash collision or corruption"}

            prev_hash = current_hash
            depth += 1

        return {"valid": True, "depth": depth, "terminal_hash": prev_hash}
