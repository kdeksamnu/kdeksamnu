
import math
from enum import Enum
from typing import Any, Optional
from uuid import UUID, uuid4
from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_validator

class SpectralConstant(str, Enum):
    GOLD_JOY = "gold_joy"
    TEAL_CURIOSITY = "teal_curiosity"
    BLUE_SORROW = "blue_sorrow"
    RED_ANGER = "red_anger"
    VIOLET_FEAR = "violet_fear"
    EMERALD_LOVE = "emerald_love"
    BRONZE_OBSIDIAN_NULL = "bronze_obsidian_null"

class LogicState(str, Enum):
    TRUE = "True"
    FALSE = "False"
    BOTH = "Both"
    NEITHER = "Neither"

class SpectralResonanceIngest(BaseModel):
    event_id: UUID = Field(default_factory=uuid4)
    observer_id: UUID = Field(...)
    primary_constant: SpectralConstant = Field(...)
    secondary_constant: Optional[SpectralConstant] = Field(None)
    magnitude: float = Field(..., ge=0.0, le=10.0)
    harmonic_phase: float = Field(default=0.0, description="Wave phase in radians, topologically normalized to S^1")
    topological_continuity: bool = Field(True)
    micro_fracture_detected: bool = Field(False)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("topological_continuity")
    @classmethod
    def enforce_continuity(cls, v: bool) -> bool:
        if not v:
            raise ValueError("Topological continuity violation.")
        return v

    @field_validator("secondary_constant")
    @classmethod
    def validate_distinct_pairing(cls, v: Optional[SpectralConstant], info: Any) -> Optional[SpectralConstant]:
        primary = info.data.get("primary_constant")
        if v and v == primary:
            raise ValueError("Secondary constant must be distinct from primary.")
        return v

    @field_validator("harmonic_phase", mode="before")
    @classmethod
    def wrap_to_circle(cls, v: float) -> float:
        if not isinstance(v, (int, float)):
            raise ValueError("harmonic_phase must be a numeric value")
        two_pi = 2.0 * math.pi
        wrapped = v % two_pi
        if abs(wrapped - two_pi) < 1e-12 or wrapped < 0:
            wrapped = 0.0
        return round(wrapped, 6)

    def resolve_logic_state(self) -> LogicState:
        from engine.core.spectral_matrix import SpectralResolver
        return SpectralResolver.resolve_interaction(
            self.primary_constant, 
            self.secondary_constant, 
            self.harmonic_phase
        )
