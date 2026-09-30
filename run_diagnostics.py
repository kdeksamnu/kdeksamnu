import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from engine.db.session import Base
from engine.db.models import ObserverNode, Faction, SpectralEvent

db_path = "./ash_archive.db"
db_url = f"sqlite:///{db_path}"
print(f"[*] Binding to Unified URL: {db_url}")

engine = create_engine(db_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Explicitly bind and create tables across the shared metadata registry
ObserverNode.__table__.create(bind=engine, checkfirst=True)
Faction.__table__.create(bind=engine, checkfirst=True)
SpectralEvent.__table__.create(bind=engine, checkfirst=True)

print("[+] Ash Archive tables materialized via explicit table binding.")

db = SessionLocal()
try:
    observers = db.query(ObserverNode).all()
    print(f"[+] Successfully queried observer_nodes. Count: {len(observers)}")
    for obs in observers:
        print(f"    - Observer: {obs.designation} (Integrity: {obs.somatic_integrity})")
except Exception as e:
    print(f"[-] Diagnostic query exception: {e}")
finally:
    db.close()
