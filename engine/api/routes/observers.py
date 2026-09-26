from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from engine.db.session import SessionLocal
from engine.db.models import ObserverNode

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/observers/")
def get_observers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    observers = db.query(ObserverNode).offset(skip).limit(limit).all()
    return [
        {
            "observer_id": str(obs.observer_id),
            "designation": obs.designation,
            "somatic_integrity": obs.somatic_integrity,
            "ego_density": obs.ego_density,
            "harmonic_scars_total": obs.harmonic_scars_total,
            "lineage_intact": obs.lineage_intact
        }
        for obs in observers
    ]
