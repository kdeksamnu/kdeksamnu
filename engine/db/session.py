import os
import importlib
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ash_archive.db")

db_engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Exported as both 'engine' and 'db_engine' for compatibility
engine = db_engine

@event.listens_for(db_engine, "connect")
def configure_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL;")
    cursor.execute("PRAGMA busy_timeout=10000;")
    cursor.execute("PRAGMA synchronous=NORMAL;")
    cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initializes the database schema by binding models to the engine."""
    importlib.import_module("engine.db.models")
    Base.metadata.create_all(bind=db_engine)
