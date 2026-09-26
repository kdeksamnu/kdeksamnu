import pytest
from uuid import uuid4
from engine.schemas.spectral import SpectralResonanceIngest, SpectralConstant

def test_valid_spectral_ingest():
    """The happy path: a perfectly balanced isomorphic pairing."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "teal_curiosity",
        "secondary_constant": "gold_joy",
        "magnitude": 7.5,
        "topological_continuity": True,
        "micro_fracture_detected": False
    }
    
    # If this raises no exception, the architecture holds.
    model = SpectralResonanceIngest(**payload)
    assert model.primary_constant == SpectralConstant.TEAL_CURIOSITY
    assert model.magnitude == 7.5

def test_rejects_redundant_isomorphic_pairing():
    """Symmetric Negative Test: The system must reject a constant paired with itself."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "red_anger",
        "secondary_constant": "red_anger", # The violation
        "magnitude": 5.0,
        "topological_continuity": True,
        "micro_fracture_detected": False
    }
    
    with pytest.raises(ValueError) as exc_info:
        SpectralResonanceIngest(**payload)
    
    assert "distinct from primary" in str(exc_info.value)

def test_rejects_out_of_bounds_magnitude():
    """Symmetric Negative Test: Magnitude must remain within the 0-10 physical bounds."""
    payload = {
        "observer_id": str(uuid4()),
        "primary_constant": "violet_fear",
        "magnitude": 15.0, # The violation
        "topological_continuity": True,
        "micro_fracture_detected": False
    }
    
    with pytest.raises(ValueError) as exc_info:
        SpectralResonanceIngest(**payload)
    
    assert "less than or equal to 10.0" in str(exc_info.value)
