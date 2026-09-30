from uuid import UUID
from typing import Optional
from pydantic import BaseModel, Field

class FactionCreate(BaseModel):
    designation: str = Field(..., description="The moniker of the ideological collective")
    description: Optional[str] = None

class BelnapDunnDistribution(BaseModel):
    true_count: int = Field(0, description="Classical True (T) - Harmonic alignment")
    false_count: int = Field(0, description="Classical False (F) - Negation")
    both_count: int = Field(0, description="Contradiction / Dialetheic tension (B) - Load-bearing fracture")
    neither_count: int = Field(0, description="Incomplete / Gap state (N) - Grounding void")

class FactionIntegrityMetric(BaseModel):
    faction_id: UUID
    designation: str
    active_observers: int
    mean_somatic_integrity: float = Field(..., ge=0.0, le=1.0, description="Average structural integrity of the verified cohort")
    total_harmonic_scars: int
    scarred_observer_count: int
    systemic_risk_level: str = Field(..., description="NOMINAL, DEGRADED, or CRITICAL")
    logic_distribution: BelnapDunnDistribution
    dialetheic_velocity: float = Field(..., description="Oscillation index (0.0 to 1.0) measuring rapid transitions into paradox")
    quarantined_observers: int = Field(0, description="Observers excluded from metrics due to lineage_intact == False")
