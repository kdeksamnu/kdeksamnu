"""Test isolation: never touch ash_archive.db.

engine.db.session reads DATABASE_URL when first imported, so it must be set here,
before any test module imports the engine. A temp file (not :memory:) is used because
the FastAPI TestClient runs the app in another thread, which would otherwise get its
own empty in-memory database.
"""
import os
import tempfile

import pytest

_TMPDIR = tempfile.mkdtemp(prefix="mlaos_test_")
os.environ["DATABASE_URL"] = f"sqlite:///{_TMPDIR}/test.db"


@pytest.fixture(autouse=True)
def fresh_database():
    """Drop and recreate every table before each test so the chain starts at genesis."""
    from engine.db.session import Base, engine, init_db

    init_db()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
