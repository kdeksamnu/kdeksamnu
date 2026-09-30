import hashlib
import uuid
from engine.db.session import SessionLocal
from engine.core.services import ChainVerificationService

db = SessionLocal()
try:
    terminal_hash = "ad012a7d664681367b0069e50ab7820dad0f2612ebf2e39f381cd09aaf18ffce"
    report = ChainVerificationService.verify_chain_lineage(terminal_hash, db)

    print("\n=== TESTING SCHEMA EVOLUTION ON ROOT NODES ===")
    failed_steps = [s for s in report.lineage if not s.valid]
    
    for step in failed_steps:
        # Fetch raw db record
        ev = db.execute(
            f"SELECT primary_constant, secondary_constant, logic_state, magnitude FROM spectral_events WHERE event_id = '{step.event_id.hex}'"
        ).fetchone()
        
        pri = ev[0]
        sec_val = ev[1] if ev[1] else "NONE"
        sec_null = ev[1] if ev[1] else "null"
        ls = ev[2]
        mag = ev[3]

        # Test 7-field variants (v0.1)
        raw_none = f"{step.parent_hash}:{step.event_id}:{step.current_hash if False else ''}"  # test script below
