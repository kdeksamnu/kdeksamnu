from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from engine.db.session import get_db
from engine.db.models import Faction
from engine.schemas.faction import FactionCreate
from engine.core.services import FactionAggregationService

router = APIRouter(prefix="/api/v1/factions", tags=["Ideological Collectives"])

@router.post("/", status_code=status.HTTP_201_CREATED, summary="Forge a new Ideological Collective")
def create_faction(payload: FactionCreate, db: Session = Depends(get_db)):
    faction = Faction(designation=payload.designation, description=payload.description)
    db.add(faction)
    db.commit()
    db.refresh(faction)
    return {"id": str(faction.id), "designation": faction.designation}

@router.get("/{faction_id}/health", summary="Macro-Scale Factional Health")
def get_faction_health(faction_id: UUID, db: Session = Depends(get_db)):
    health = FactionAggregationService.get_faction_health(faction_id, db)
    if not health:
        raise HTTPException(status_code=404, detail="Faction not found in the registry.")
    return health
