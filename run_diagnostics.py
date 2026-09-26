import glob
from engine.db.session import SessionLocal, DATABASE_URL
from engine.db.models import ObserverNode, SpectralEvent

print(f"[*] Active DATABASE_URL: {DATABASE_URL}")

db_files = glob.glob("*.db*") + glob.glob("*.sqlite*")
print(f"[*] SQLite files found: {db_files}")

db = SessionLocal()
try:
    observers = db.query(ObserverNode).all()
    print(f"[*] Observers in active DB ({len(observers)}):")
    for o in observers:
        print(f"    - Designation: {o.designation} | ID: {o.observer_id} | Integrity: {o.somatic_integrity}")
    
    total_events = db.query(SpectralEvent).count()
    print(f"[*] Total SpectralEvents in active DB: {total_events}")
finally:
    db.close()
