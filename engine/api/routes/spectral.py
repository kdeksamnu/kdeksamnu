import json
import os
import sqlite3
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from engine.core.merkle import MerkleArchiveVerifier
from engine.core.persistence import AppendOnlyLedger
from engine.schemas.spectral import SpectralResonanceIngest

router = APIRouter(prefix="/api/v1/spectral", tags=["spectral"])


def get_ledger() -> AppendOnlyLedger:
    db_url = os.environ.get("DATABASE_URL", "")
    if db_url.startswith("sqlite:///"):
        path = db_url.replace("sqlite:///", "")
    else:
        path = "ash_archive.db"
    return AppendOnlyLedger(path)


@router.post("/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_spectral_event(event: SpectralResonanceIngest):
    event_id_str = str(event.event_id)

    # Boundary handling: micro-fractures are quarantined gracefully
    if event.micro_fracture_detected:
        return {
            "status": "quarantined",
            "event_id": event_id_str,
            "observer_id": str(event.observer_id),
            "detail": "Micro-fracture detected; event quarantined under Lex I."
        }

    ledger = get_ledger()
    with sqlite3.connect(ledger.db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT current_hash FROM event_log ORDER BY sequence_id DESC LIMIT 1")
        row = cursor.fetchone()
        parent_hash = row[0] if row else "0" * 64
        dump_data = event.model_dump(mode="json") if hasattr(event, "model_dump") else event.dict()
        payload = json.dumps(dump_data, default=str, sort_keys=True)

    current_hash = MerkleArchiveVerifier.compute_hash(parent_hash, payload)

    try:
        ledger.append_event(event_id_str, payload, parent_hash, current_hash)
    except sqlite3.IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail=f"Merkle chain collision or duplicate event_id: {str(e)}"
        )

    return {
        "status": "integrated",
        "event_id": event_id_str,
        "parent_hash": parent_hash,
        "current_hash": current_hash
    }
