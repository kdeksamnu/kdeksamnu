import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import sqlite3

from engine.core.persistence import AppendOnlyLedger
from engine.core.merkle import MerkleArchiveVerifier

router = APIRouter(prefix="/api/v1/spectral", tags=["spectral"])
ledger = AppendOnlyLedger("ash_archive.db")

class SpectralEvent(BaseModel):
    event_id: str
    observer_id: str
    primary_constant: str
    secondary_constant: str
    magnitude: float
    harmonic_phase: float
    topological_continuity: bool
    micro_fracture_detected: bool

@router.post("/ingest")
def ingest_spectral_event(event: SpectralEvent):
    with sqlite3.connect(ledger.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_hash FROM event_log ORDER BY sequence_id DESC LIMIT 1")
        row = cursor.fetchone()
        parent_hash = row[0] if row else "0000000000000000000000000000000000000000000000000000000000000000"
        payload = json.dumps(event.dict(), sort_keys=True)
    current_hash = MerkleArchiveVerifier.compute_hash(parent_hash, payload)

    try:
        ledger.append_event(event.event_id, payload, parent_hash, current_hash)
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=409, 
            detail=f"Merkle chain collision or duplicate event_id: {str(e)}"
        )
    
    return {
        "status": "resonant",
        "event_id": event.event_id,
        "parent_hash": parent_hash,
        "current_hash": current_hash
    }
