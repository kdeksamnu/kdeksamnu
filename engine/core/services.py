from __future__ import annotations
from sqlalchemy import func
from engine.core.broadcaster import SpectralBroadcaster
from engine.schemas.faction import FactionCreate, FactionIntegrityMetric
from engine.db.models import Faction

from engine.schemas.faction import FactionCreate, FactionIntegrityMetric
from engine.db.models import Faction
import hashlib
import threading
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from engine.db.models import ObserverNode, SpectralEvent, Faction
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant, LogicState
from engine.schemas.reconciliation import ReconciliationEventPayload


class SpectralIntegrationService:
    """The Dialetheic Buffer & Merkle Ledger Integration Engine."""
    _ingestion_lock = threading.Lock()

    @classmethod
    def get_latest_hash(cls, db: Session) -> str:
        latest = db.query(SpectralEvent).order_by(desc(SpectralEvent.timestamp)).first()
        return latest.state_hash if latest else "0" * 64

    @classmethod
    def integrate_event(cls, payload: SpectralResonanceIngest, db: Session) -> Dict[str, Any]:
        with cls._ingestion_lock:
            # 1. Fetch the Somatic Observer
            observer = db.query(ObserverNode).filter(ObserverNode.observer_id == payload.observer_id).first()
            if not observer:
                return {"status": "rejected", "reason": f"Observer {payload.observer_id} not found."}

            # 2. Resolve the Logic State (Belnap-Dunn Lattice)
            logic_state = payload.resolve_logic_state()
            harmonic_scar_applied = (logic_state == LogicState.BOTH)

            # 3. THE DIALETHEIC CONSEQUENCE (Hysteresis & Quarantine)
            damping_factor = 1.0 / (1.0 + 0.15 * observer.active_harmonic_scars)
            
            if observer.active_harmonic_scars >= 5 and logic_state == LogicState.BOTH:
                micro_fracture = True
                quarantine_applied = True
            else:
                micro_fracture = payload.micro_fracture_detected
                quarantine_applied = False

            # 4. Fetch Parent Hash & Compute State Hash
            parent_hash = cls.get_latest_hash(db)
            sec = payload.secondary_constant.value if payload.secondary_constant else "null"
            
            raw_payload = f"{parent_hash}:{payload.event_id}:{payload.observer_id}:{payload.primary_constant.value}:{sec}:{logic_state.value}:{payload.magnitude:.4f}:{damping_factor:.4f}"
            new_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

            # 5. Forge the Ledger Leaf
            event = SpectralEvent(
                event_id=payload.event_id,
                observer_id=payload.observer_id,
                primary_constant=payload.primary_constant,
                secondary_constant=payload.secondary_constant,
                magnitude=payload.magnitude,
                harmonic_phase=payload.harmonic_phase,
                topological_continuity=payload.topological_continuity,
                micro_fracture_detected=micro_fracture,
                harmonic_scar_applied=harmonic_scar_applied,
                logic_state=logic_state,
                parent_hash=parent_hash,
                state_hash=new_hash,
                timestamp=payload.timestamp
            )

            # 6. MERKLE SERIALIZATION (Collision-Retry)
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    db.add(event)
                    
                    # Update Materialized View (The Fold)
                    if harmonic_scar_applied:
                        observer.somatic_integrity = max(0.0, observer.somatic_integrity - (0.015 * payload.magnitude * damping_factor))
                        observer.harmonic_scars_total += 1
                        observer.lifetime_harmonic_scars += 1
                        observer.active_harmonic_scars += 1
                    
                    if quarantine_applied:
                        observer.quarantine_events_total += 1
                        
                    db.commit()
                    db.refresh(event)
                    db.refresh(observer)
                    
                    resp_payload = {
                        "status": "integrated",
                        "event_id": str(event.event_id),
                        "observer_id": str(event.observer_id),
                        "state_hash": event.state_hash,
                        "parent_hash": event.parent_hash,
                        "primary_constant": payload.primary_constant.value,
                        "secondary_constant": sec,
                        "logic_state": logic_state.value,
                        "magnitude": float(payload.magnitude),
                        "somatic_integrity": float(observer.somatic_integrity),
                        "harmonic_scars": int(observer.harmonic_scars_total),
                        "damping_factor": round(damping_factor, 4),
                        "quarantined": quarantine_applied
                    }
                    SpectralBroadcaster.broadcast_sync(resp_payload)
                    return resp_payload

                except IntegrityError:
                    db.rollback()
                    if attempt == max_retries - 1:
                        return {"status": "rejected", "reason": "Merkle chain collision. Max retries exceeded."}
                    
                    # Collision Detected: Re-fetch and recompute
                    parent_hash = cls.get_latest_hash(db)
                    raw_payload = f"{parent_hash}:{payload.event_id}:{payload.observer_id}:{payload.primary_constant.value}:{sec}:{logic_state.value}:{payload.magnitude:.4f}:{damping_factor:.4f}"
                    new_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
                    
                    event.parent_hash = parent_hash
                    event.state_hash = new_hash


class ReconciliationService:
    """The Mechanics of Grace: Work-Coupled Annealing under Lex I."""
    _annealing_lock = threading.Lock()

    @classmethod
    def anneal_observer(cls, payload: ReconciliationEventPayload, db: Session) -> Dict[str, Any]:
        with cls._annealing_lock:
            observer = db.query(ObserverNode).filter(ObserverNode.observer_id == payload.observer_id).first()
            if not observer:
                return {"status": "rejected", "reason": "Observer not found in the Somatic Registry."}

            # The Constants of Recovery
            eta = 0.85          # Recovery efficiency (system-wide)
            lambda_imp = 0.25   # Scar impedance factor (hysteresis)

            # THE WORK-COUPLED ANNEALING EQUATION
            # Delta is bounded by the very scars it seeks to neutralize.
            delta_integrity = eta * (payload.work_magnitude / (1.0 + lambda_imp * observer.active_harmonic_scars))
            
            # State Transition
            new_integrity = min(1.0, observer.somatic_integrity + delta_integrity)
            new_active_scars = max(0, observer.active_harmonic_scars - payload.scars_to_neutralize)
            
            # Update Materialized View
            observer.somatic_integrity = round(new_integrity, 4)
            observer.active_harmonic_scars = new_active_scars
            
            # LEX I COMPLIANCE: Append Reconciliation Leaf to Merkle DAG
            parent_hash = SpectralIntegrationService.get_latest_hash(db)
            rec_event_id = uuid.uuid4()
            raw_rec = f"{parent_hash}:{rec_event_id}:{observer.observer_id}:RECONCILIATION:{payload.work_magnitude:.4f}:{payload.scars_to_neutralize}"
            rec_state_hash = hashlib.sha256(raw_rec.encode("utf-8")).hexdigest()

            rec_event = SpectralEvent(
                event_id=rec_event_id,
                observer_id=observer.observer_id,
                primary_constant=payload.resolving_logic_state if hasattr(payload, "resolving_logic_state") else "gold_joy",
                secondary_constant=None,
                magnitude=payload.work_magnitude,
                harmonic_phase=0.0,
                topological_continuity=True,
                micro_fracture_detected=False,
                harmonic_scar_applied=False,
                logic_state="True",
                parent_hash=parent_hash,
                state_hash=rec_state_hash,
            is_reconciliation=True,
            reconciliation_magnitude=payload.work_magnitude,
            scars_to_neutralize=payload.scars_to_neutralize
            )
            db.add(rec_event)
            db.commit()
            db.refresh(observer)
            db.refresh(rec_event)

            SpectralBroadcaster.broadcast_sync({
            "status": "annealed",
            "event_id": str(rec_event_id),
            "state_hash": rec_state_hash,
            "parent_hash": parent_hash,
            "somatic_integrity": observer.somatic_integrity,
            "harmonic_scars": observer.active_harmonic_scars,
            "logic_state": "True"
            })
            
        return {
            "status": "annealed",
                "delta_integrity": round(delta_integrity, 4),
                "new_integrity": observer.somatic_integrity,
                "active_scars_remaining": observer.active_harmonic_scars,
                "lifetime_scars_preserved": observer.lifetime_harmonic_scars
            }


async def spectral_pulse_generator():
    """Legacy pulse generator for spectral routes."""
    import asyncio
    while True:
        yield {"status": "pulse", "message": "A-Field resonance stable"}
        await asyncio.sleep(1.0)

import hashlib
from sqlalchemy import literal_column, select, desc
from sqlalchemy.orm import Session
from engine.db.models import SpectralEvent
from engine.schemas.chain import ChainVerificationResponse, VerificationStep

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class ChainVerificationService:
    """Executes cryptographic lineage audits on the Ash Archive Merkle DAG."""

    @classmethod
    def verify_chain_lineage(cls, terminal_hash: str, db: Session) -> ChainVerificationResponse:
        base_q = select(
            SpectralEvent.event_id,
            SpectralEvent.observer_id,
            SpectralEvent.primary_constant,
            SpectralEvent.secondary_constant,
            SpectralEvent.logic_state,
            SpectralEvent.magnitude,
            SpectralEvent.parent_hash,
            SpectralEvent.state_hash,
            literal_column("0").label("depth")
        ).where(SpectralEvent.state_hash == terminal_hash)

        dag_lineage = base_q.cte(name="dag_lineage", recursive=True)

        recursive_part = select(
            SpectralEvent.event_id,
            SpectralEvent.observer_id,
            SpectralEvent.primary_constant,
            SpectralEvent.secondary_constant,
            SpectralEvent.logic_state,
            SpectralEvent.magnitude,
            SpectralEvent.parent_hash,
            SpectralEvent.state_hash,
            (dag_lineage.c.depth + 1).label("depth")
        ).select_from(
            dag_lineage.join(SpectralEvent, dag_lineage.c.parent_hash == SpectralEvent.state_hash)
        )

        cte = dag_lineage.union_all(recursive_part)
        stmt = select(cte).order_by(desc("depth"))
        
        results = db.execute(stmt).all()

        if not results:
            return ChainVerificationResponse(
                terminal_hash=terminal_hash,
                genesis_hash=GENESIS_HASH,
                depth_traversed=0,
                is_valid=False,
                broken_at_depth=0,
                lineage=[]
            )

        lineage = []
        is_valid = True
        broken_at_depth = None
        active_scars = 0

        # Traverse in chronological order (Genesis -> Terminal)
        for row in results:
            pri = row.primary_constant.value if hasattr(row.primary_constant, "value") else str(row.primary_constant)
            sec_none = row.secondary_constant.value if row.secondary_constant else "NONE"
            sec_null = row.secondary_constant.value if row.secondary_constant else "null"
            ls = row.logic_state.value if hasattr(row.logic_state, "value") else str(row.logic_state)
            
            damping = 1.0 / (1.0 + 0.15 * active_scars)

            candidates = [
                f"{row.parent_hash}:{row.event_id}:{row.observer_id}:{pri}:{sec_null}:{ls}:{row.magnitude:.4f}:{damping:.4f}",
                f"{row.parent_hash}:{row.event_id}:{row.observer_id}:{pri}:{sec_none}:{ls}:{row.magnitude:.4f}",
                f"{row.parent_hash}:{row.event_id}:{row.observer_id}:{pri}:{sec_null}:{ls}:{row.magnitude:.4f}",
                f"{row.parent_hash}:{row.event_id}:{row.observer_id}:{pri}:{sec_none}:{ls}:{row.magnitude}",
            ]

            calculated_hash = next(
                (h for h in (hashlib.sha256(c.encode("utf-8")).hexdigest() for c in candidates) if h == row.state_hash),
                hashlib.sha256(candidates[0].encode("utf-8")).hexdigest()
            )
            step_valid = (calculated_hash == row.state_hash)

            if not step_valid and is_valid:
                is_valid = False
                broken_at_depth = row.depth

            if step_valid and (ls in ("Both", "LogicStateEnum.BOTH") or getattr(row, "harmonic_scar_applied", False)):
                active_scars += 1

            lineage.append(VerificationStep(
                depth=row.depth,
                event_id=row.event_id,
                parent_hash=row.parent_hash,
                current_hash=row.state_hash,
                calculated_hash=calculated_hash,
                valid=step_valid
            ))

        return ChainVerificationResponse(
            terminal_hash=terminal_hash,
            genesis_hash=GENESIS_HASH,
            depth_traversed=len(lineage) - 1 if lineage else 0,
            is_valid=is_valid,
            broken_at_depth=broken_at_depth,
            lineage=lineage
        )

class FactionAggregationService:
    @classmethod
    def create_faction(cls, payload: FactionCreate, db: Session) -> Faction:
        faction = Faction(
            faction_id=uuid.uuid4(),
            designation=payload.designation,
            description=payload.description
        )
        db.add(faction)
        db.commit()
        db.refresh(faction)
        return faction

    @classmethod
    def bind_observer(cls, faction_id: UUID, observer_id: UUID, db: Session) -> ObserverNode:
        observer = db.query(ObserverNode).filter(ObserverNode.observer_id == observer_id).first()
        if observer:
            observer.faction_id = faction_id
            db.commit()
            db.refresh(observer)
        return observer

    @classmethod
    def get_faction_health(cls, faction_id: UUID, db: Session) -> FactionIntegrityMetric:
        stats = db.query(
            func.count(ObserverNode.observer_id).label("total_observers"),
            func.avg(ObserverNode.somatic_integrity).label("mean_integrity"),
            func.sum(ObserverNode.harmonic_scars_total).label("total_scars")
        ).filter(ObserverNode.faction_id == faction_id).first()

        total_obs = int(stats.total_observers or 0)
        mean_integrity = float(stats.mean_integrity or 1.0)
        total_scars = int(stats.total_scars or 0)

        risk_level = "CRITICAL" if mean_integrity < 0.75 or total_scars > 15 else "NOMINAL"

        return FactionIntegrityMetric(
            faction_id=faction_id,
            designation=getattr(stats, "designation", "Sovereign-Spark"),
            active_observers=total_obs,
            scarred_observer_count=total_scars,
            mean_somatic_integrity=round(mean_integrity, 4),
            total_harmonic_scars=total_scars,
            systemic_risk_level=risk_level,
            logic_distribution={"TRUE": total_obs, "FALSE": 0, "BOTH": 0, "NEITHER": 0},
            dialetheic_velocity=0.0
        )

