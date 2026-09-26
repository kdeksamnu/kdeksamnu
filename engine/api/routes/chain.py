from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from engine.db.session import get_db
from engine.core.services import ChainVerificationService
from engine.schemas.chain import ChainVerificationResponse

router = APIRouter(prefix="/api/v1/spectral/chain", tags=["Cryptographic Audit"])

@router.get(
    "/verify",
    response_model=ChainVerificationResponse,
    summary="Cryptographic Lineage Audit",
    description="Recursively traverses the Merkle DAG from a terminal state_hash to the Genesis block, verifying every node."
)
def verify_spectral_chain(
    state_hash: str = Query(..., description="The terminal state_hash to audit"),
    db: Session = Depends(get_db)
):
    if len(state_hash) != 64:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="state_hash must be a 64-character SHA-256 hex string."
        )
    
    return ChainVerificationService.verify_chain_lineage(state_hash, db)
