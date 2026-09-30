import hashlib
from engine.db.session import SessionLocal
from engine.core.services import ChainVerificationService

db = SessionLocal()
try:
    terminal_hash = "ad012a7d664681367b0069e50ab7820dad0f2612ebf2e39f381cd09aaf18ffce"
    report = ChainVerificationService.verify_chain_lineage(terminal_hash, db)

    # report.lineage is ordered by desc(depth), which is Genesis (oldest) -> Terminal (latest)
    active_scars = 0
    passed = 0
    failed = 0

    for step in report.lineage:
        # Fetch row attributes from db
        ev = [r for r in db.execute(
            f"SELECT primary_constant, secondary_constant, logic_state, magnitude, harmonic_scar_applied FROM spectral_events WHERE event_id = '{step.event_id.hex}'"
        )][0]

        pri = ev[0]
        sec = ev[1] if ev[1] else "null"
        ls = ev[2]
        mag = ev[3]
        scar_applied = ev[4]

        damping = 1.0 / (1.0 + 0.15 * active_scars)
        raw = f"{step.parent_hash}:{step.event_id}:{report.lineage[0].event_id if False else ''}"  # will do clean query
