"""Proving grounds for the complete isomorphic pipeline lifecycle."""
import uuid
import pytest
from sqlalchemy.orm import Session

from engine.db.session import SessionLocal, init_db
from engine.db.models import Faction, ObserverNode, SpectralEvent
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant, LogicState
from engine.core.services import SpectralIntegrationService

@pytest.fixture(autouse=True)
def setup_database():
    """Ensure schema is initialized before each test."""
    init_db()

def test_isomorphic_pipeline_lifecycle() -> None:
    db: Session = SessionLocal()
    try:
        # 0. Provision unique test faction and observer to satisfy UNIQUE constraints
        unique_tag = f"Test-Faction-{uuid.uuid4().hex[:8]}"
        faction = Faction(designation=unique_tag, description="Invariant proving grounds")
        db.add(faction)
        db.commit()
        db.refresh(faction)

        observer = ObserverNode(
            designation=f"Test-Observer-{uuid.uuid4().hex[:8]}", 
            faction_id=faction.id, 
            somatic_integrity=1.0
        )
        db.add(observer)
        db.commit()
        db.refresh(observer)

        # 1. Ingest standard resonance (Gold Joy)
        payload_std = SpectralResonanceIngest(
            observer_id=observer.observer_id,
            primary_constant=SpectralConstant.GOLD_JOY,
            magnitude=8.5,
            harmonic_phase=1.57
        )
        
        res_std = SpectralIntegrationService.integrate_event(payload_std, db)
        assert res_std["status"] == "integrated"
        assert res_std["logic_state"] == LogicState.TRUE.value
        assert res_std["parent_hash"] == "0" * 64

        # 2. Ingest dialetheic contradiction (Gold Joy + Blue Sorrow -> Both)
        payload_contradiction = SpectralResonanceIngest(
            observer_id=observer.observer_id,
            primary_constant=SpectralConstant.GOLD_JOY,
            secondary_constant=SpectralConstant.BLUE_SORROW,
            magnitude=9.0,
            harmonic_phase=3.14
        )
        res_conflict = SpectralIntegrationService.integrate_event(payload_contradiction, db)
        assert res_conflict["status"] == "integrated"
        assert res_conflict["logic_state"] == LogicState.BOTH.value
        assert res_conflict["harmonic_scar"] is True
        assert res_conflict["parent_hash"] == res_std["state_hash"]

        # 3. Verify Merkle Chain integrity in database
        leaf_last = db.query(SpectralEvent).filter_by(event_id=payload_contradiction.event_id).first()
        leaf_first = db.query(SpectralEvent).filter_by(event_id=payload_std.event_id).first()

        assert leaf_last is not None
        assert leaf_first is not None
        assert leaf_last.parent_hash == leaf_first.state_hash
        assert len(leaf_last.state_hash) == 64

    finally:
        db.close()
