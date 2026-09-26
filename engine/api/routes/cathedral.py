from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy import desc
import json
import time
from datetime import datetime, timezone

from engine.db.session import SessionLocal
from engine.db.models import Faction, ObserverNode, SpectralEvent
from engine.schemas.cathedral import CathedralTelemetryPayload, ObserverVisualState

router = APIRouter(prefix="/api/v1/cathedral", tags=["The Glass Cathedral"])

@router.get("/stream/{faction_id}")
def stream_cathedral_state(faction_id: str):
    """
    Strictly synchronous SSE stream. Prevents event-loop blocking 
    and ensures the TCP connection remains immortal.
    """
    def event_generator():
        while True:
            db = SessionLocal()
            try:
                faction = db.query(Faction).filter(Faction.id == faction_id).first()
                if not faction:
                    yield f"data: {json.dumps({'error': 'Faction not found'})}\n\n"
                    break

                observers = db.query(ObserverNode).filter(ObserverNode.faction_id == faction_id).all()
                visual_observers = []

                for obs in observers:
                    recent_events = db.query(SpectralEvent).filter(
                        SpectralEvent.observer_id == obs.observer_id
                    ).order_by(desc(SpectralEvent.timestamp)).limit(10).all()
                    
                    thermal_load = sum(e.magnitude for e in recent_events if e.logic_state.value == "Both")
                    dominant_state = recent_events[0].logic_state.value if recent_events else "Neither"

                    visual_observers.append(ObserverVisualState(
                        observer_id=obs.observer_id,
                        designation=obs.designation,
                        somatic_integrity=obs.somatic_integrity,
                        active_harmonic_scars=obs.active_harmonic_scars,
                        thermal_load=round(thermal_load, 4),
                        dialetheic_velocity=0.0,
                        dominant_logic_state=dominant_state,
                        spectral_phase=0.0
                    ))

                payload = CathedralTelemetryPayload(
                    sequence_id=int(datetime.now(timezone.utc).timestamp() * 1000),
                    timestamp=datetime.now(timezone.utc).isoformat(),
                    faction_id=faction.id,
                    observers=visual_observers
                )

                yield f"data: {payload.model_dump_json()}\n\n"
            finally:
                db.close()
            
            time.sleep(0.5) # 2Hz pulse, strictly synchronous

    return StreamingResponse(event_generator(), media_type="text/event-stream")
