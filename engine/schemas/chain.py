from uuid import UUID
from typing import List, Optional
from pydantic import BaseModel, Field

class VerificationStep(BaseModel):
    depth: int
    event_id: UUID
    parent_hash: str
    current_hash: str = Field(..., description="The stored state_hash in the ledger")
    calculated_hash: str = Field(..., description="The recomputed SHA-256 signature")
    valid: bool

class ChainVerificationResponse(BaseModel):
    terminal_hash: str
    genesis_hash: str
    depth_traversed: int
    is_valid: bool
    broken_at_depth: Optional[int] = Field(None, description="The depth where the chain fractured, if any")
    lineage: List[VerificationStep]
