from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from engine.db.session import get_db
from engine.db.models import ObserverNode, SpectralEvent
from engine.schemas.observer import ObserverProfileResponse, SpectralEventSummary

router = APIRouter(prefix="/api/v1/observers", tags=["Somatic Observers"])

@router.get(
    "/{observer_id}",
    summary="Retrieve Somatic Observer Profile",
    description="Returns the current integrity, scar count, and paginated history of a specific Warm Axis agent."
)
def get_observer_profile(
    observer_id: UUID,
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Max records to return"),
    db: Session = Depends(get_db)
) -> ObserverProfileResponse:
    # 1. Fetch the observer
    observer = db.query(ObserverNode).filter(ObserverNode.observer_id == observer_id).first()
    if not observer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Observer with ID {observer_id} not found in the Ash Archive."
        )

    # 2. Fetch paginated event history, ordered newest first
    events = (
        db.query(SpectralEvent)
        .filter(SpectralEvent.observer_id == observer_id)
        .order_by(SpectralEvent.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    # 3. Map to Pydantic schemas
    event_summaries = [
        SpectralEventSummary(
            event_id=event.event_id,
            primary_constant=event.primary_constant,
            secondary_constant=event.secondary_constant,
            logic_state=event.logic_state,
            harmonic_scar=event.harmonic_scar_applied,
            magnitude=event.magnitude,
            state_hash=event.state_hash,
            timestamp=event.timestamp
        )
        for event in events
    ]

    # 4. Calculate total witnessed (for pagination metadata)
    total_witnessed = db.query(SpectralEvent).filter(SpectralEvent.observer_id == observer_id).count()

    return ObserverProfileResponse(
        observer_id=observer.observer_id,
        designation=observer.designation,
        faction=observer.faction,
        ego_density=observer.ego_density,
        somatic_integrity=observer.somatic_integrity,
        harmonic_scars_total=observer.harmonic_scars_total,
        quarantine_events_total=observer.quarantine_events_total,
        created_at=observer.created_at,
        updated_at=observer.updated_at,
        event_history=event_summaries,
        total_events_witnessed=total_witnessed
    )
