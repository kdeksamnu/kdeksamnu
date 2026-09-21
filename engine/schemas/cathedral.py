from uuid import UUID
from typing import List
from pydantic import BaseModel, Field

class ObserverVisualState(BaseModel):
    observer_id: UUID
    designation: str
    somatic_integrity: float = Field(..., ge=0.0, le=1.0)
    thermal_load: float = Field(..., ge=0.0)
    dialetheic_velocity: float = Field(..., ge=0.0, le=1.0)
    active_harmonic_scars: int = Field(..., ge=0)
    state_gradient: List[float] = Field(default=[0.0, 0.0, 0.0])
    logic_state_encoded: float = Field(..., ge=0.0, le=1.0)

class CathedralTelemetryPayload(BaseModel):
    sequence_id: int = Field(..., description="Monotonically increasing vector clock to prevent network desynchronization")
    timestamp: str
    faction_id: UUID
    observers: List[ObserverVisualState]
