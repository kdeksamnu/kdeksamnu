import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
from engine.main import app

client = TestClient(app)

def test_health_probe():
    """The machine must have a pulse."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "resonant"

def test_successful_spectral_ingest():
    """The happy path: a valid, continuous isomorphic pairing."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "teal_curiosity",
        "secondary_constant": "gold_joy",
        "magnitude": 7.5,
        "topological_continuity": True,
        "micro_fracture_detected": False
    }
    
    response = client.post("/api/v1/spectral/ingest", json=payload)
    
    assert response.status_code == 202
    assert response.json()["status"] == "integrated"
    assert "X-Process-Time-Ms" in response.headers

def test_rejects_malformed_magnitude_at_boundary():
    """Symmetric Negative Test: The router must reject out-of-bounds physics before the service even sees it."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "violet_fear",
        "magnitude": 15.0, # Violation: > 10.0
        "topological_continuity": True,
        "micro_fracture_detected": False
    }
    
    response = client.post("/api/v1/spectral/ingest", json=payload)
    
    # We demand a 422, not a 500. The boundary holds.
    assert response.status_code == 422
    assert "magnitude" in str(response.json()["detail"])

def test_quarantines_micro_fracture_events():
    """Symmetric Negative Test: The system must gracefully quarantine, not crash, on boundary conditions."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "bronze_obsidian_null",
        "magnitude": 9.9,
        "topological_continuity": True,
        "micro_fracture_detected": True # The boundary condition
    }
    
    response = client.post("/api/v1/spectral/ingest", json=payload)
    
    assert response.status_code == 202
    assert response.json()["status"] == "quarantined"
