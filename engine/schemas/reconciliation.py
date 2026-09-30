
from uuid import UUID
from pydantic import BaseModel, Field

class ReconciliationEventPayload(BaseModel):
    """
    The Work-Coupled Annealing Protocol.
    Adheres to Lex I: Scars are monotonically non-decreasing.
    Integrity is annealed, never overwritten.
    """
    observer_id: UUID = Field(..., description="The somatic anchor to be annealed")
    work_magnitude: float = Field(
        ..., gt=0.0, le=1.0, 
        description="W_rec: The verified work expenditure logged on-chain"
    )
    scars_to_neutralize: int = Field(
        0, ge=0, 
        description="Discrete units of active tension resolved"
    )
    justification: str = Field(
        ..., min_length=10, 
        description="The cryptographic or administrative justification for this recovery"
    )
