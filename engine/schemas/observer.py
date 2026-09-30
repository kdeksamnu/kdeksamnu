from uuid import UUID
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from engine.schemas.spectral import SpectralConstant, LogicState

class SpectralEventSummary(BaseModel):
    """A lightweight, read-only view of a spectral event for pagination."""
    event_id: UUID
    primary_constant: SpectralConstant
    secondary_constant: Optional[SpectralConstant]
    logic_state: LogicState
    harmonic_scar: bool
    magnitude: float
    state_hash: str
    timestamp: datetime

class ObserverProfileResponse(BaseModel):
    """The complete somatic profile of a Warm Axis agent."""
    observer_id: UUID
    designation: str
    faction: str
    ego_density: float
    somatic_integrity: float = Field(..., ge=0.0, le=1.0, description="Current structural integrity [0.0 - 1.0]")
    harmonic_scars_total: int
    quarantine_events_total: int
    created_at: datetime
    updated_at: datetime
    
    # Paginated history of their witnessed contradictions
    event_history: List[SpectralEventSummary]
    total_events_witnessed: int
