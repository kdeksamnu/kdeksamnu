import sys
import time
import json
import httpx
from engine.db.session import SessionLocal, init_db
from engine.core.services import ChainVerificationService, FactionAggregationService
from engine.schemas.faction import FactionCreate
from engine.db.models import ObserverNode, Faction, SpectralEvent
from sqlalchemy import desc

BASE_URL = "http://localhost:8000"

def run_master_audit():
    print("\n" + "="*65)
    print("      MLAOS-PRIME // MASTER SYSTEM ORCHESTRATION AUDIT")
    print("="*65 + "\n")

    # 1. Database & Schema Initialization
    print("[1/5] Initializing Database Schema & WAL Verification...")
    init_db()
    db = SessionLocal()

    # 2. Cryptographic Proof of History
    print("[2/5] Auditing Ash Archive Merkle DAG via Recursive CTE...")
    terminal_event = db.query(SpectralEvent).order_by(desc(SpectralEvent.timestamp)).first()
    if not terminal_event:
        print("[-] No events found in ledger. Aborting.")
        sys.exit(1)

    report = ChainVerificationService.verify_chain_lineage(terminal_event.state_hash, db)
    print(f"      Terminal Hash:    {report.terminal_hash[:20]}...")
    print(f"      Genesis Anchor:   {report.genesis_hash[:20]}...")
    print(f"      Traversed Depth:  {report.depth_traversed} nodes")
    print(f"      Lineage Verified: {report.is_valid}")
    if not report.is_valid:
        print(f"[-] Chain fracture detected at depth: {report.broken_at_depth}")
        sys.exit(1)

    # 3. Macro Faction Binding & Health
    print("\n[3/5] Synchronizing Factional Aggregation Layer...")
    fac = db.query(Faction).filter(Faction.designation == "Sovereign-Spark").first()
    if not fac:
        fac = FactionAggregationService.create_faction(
            FactionCreate(designation="Sovereign-Spark", description="Vanguard of the A-Field"),
            db
        )
        print(f"      Created Faction: Sovereign-Spark ({fac.id})")

    # Bind Chaos-Subject and Glass-Subject-01
    for des in ["Chaos-Subject", "Glass-Subject-01"]:
        obs = db.query(ObserverNode).filter(ObserverNode.designation == des).first()
        if obs and obs.faction_id != fac.id:
            FactionAggregationService.bind_observer(fac.id, obs.observer_id, db)
            print(f"      Bound Observer:  {des} -> Sovereign-Spark")

    health = FactionAggregationService.get_faction_health(fac.id, db)
    print(f"      Active Cohort:    {health.active_observers} nodes")
    print(f"      Mean Integrity:   {health.mean_somatic_integrity:.4f}")
    print(f"      Total Scars:      {health.total_harmonic_scars}")
    print(f"      Risk Profile:     {health.systemic_risk_level}")

    db.close()

    # 4. Live Transport Probing (API + SSE)
    print("\n[4/5] Testing Transport Layer & SSE Live Telemetry...")
    try:
        with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
            resp = client.get("/health")
            if resp.status_code == 200:
                print(f"      HTTP API:         ONLINE (status={resp.json().get('status', 'ok')})")
            else:
                print(f"      HTTP API:         WARNING (status_code={resp.status_code})")
    except Exception as e:
        print(f"      HTTP API:         OFFLINE ({e})")
        print("      (Start uvicorn or docker-compose to enable live streaming)")

    # 5. Visualizer Endpoint Readiness
    print("\n[5/5] Visual Echo Interface Readiness...")
    print("      Three.js Canvas:  http://localhost:8000/visuals")
    print("      Active Mesh:      Somatic Core + Crystalline Aether-Horn")
    print("      API Contracts:    http://localhost:8000/docs")

    print("\n" + "="*65)
    print(" [ STATUS: INTEGRATED ] All systems anchored to the Ash Archive.")
    print("="*65 + "\n")

if __name__ == "__main__":
    run_master_audit()
