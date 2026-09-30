import hashlib
import re
from engine.db.session import SessionLocal
from engine.db.models import SpectralEvent

# 1. Print hashing logic from the ritual file
print("=== HASHING LOGIC IN RITUAL ===")
try:
    with open("rituals/the_grand_manifestation.py") as f:
        content = f.read()
    matches = [line for line in content.splitlines() if "sha256" in line or "state_hash" in line]
    for m in matches[:10]:
        print(f"  {m.strip()}")
except Exception as e:
    print(f"  Error reading file: {e}")

# 2. Inspect Depth 199 Event Attributes
db = SessionLocal()
try:
    event_id = "5ae05d47-a142-48dd-8fc9-df6450bf0228"
    ev = db.query(SpectralEvent).filter(SpectralEvent.event_id == event_id).first()
    
    print("\n=== DEPTH 199 RAW DATABASE ATTRIBUTES ===")
    print(f"  event_id:           {ev.event_id} (type: {type(ev.event_id)})")
    print(f"  observer_id:        {ev.observer_id} (type: {type(ev.observer_id)})")
    print(f"  parent_hash:        {ev.parent_hash}")
    print(f"  primary_constant:   {ev.primary_constant} (repr: {repr(ev.primary_constant)})")
    print(f"  secondary_constant: {ev.secondary_constant} (repr: {repr(ev.secondary_constant)})")
    print(f"  logic_state:        {ev.logic_state} (repr: {repr(ev.logic_state)})")
    print(f"  magnitude:          {ev.magnitude} (repr: {repr(ev.magnitude)})")
    print(f"  stored state_hash:  {ev.state_hash}")

    # Test common variations against stored hash: b6c6069c78ad4041f0233f3818674dffc95d534c38213550c88e5b9ea70c8d72
    pri = ev.primary_constant.value if hasattr(ev.primary_constant, "value") else str(ev.primary_constant)
    ls = ev.logic_state.value if hasattr(ev.logic_state, "value") else str(ev.logic_state)
    sec_val = ev.secondary_constant.value if hasattr(ev.secondary_constant, "value") else (str(ev.secondary_constant) if ev.secondary_constant else "")

    trials = {
        "Colon with float as-is": f"{ev.parent_hash}:{ev.event_id}:{ev.observer_id}:{pri}:{sec_val or 'NONE'}:{ls}:{ev.magnitude}",
        "Colon without sec if None": f"{ev.parent_hash}:{ev.event_id}:{ev.observer_id}:{pri}:{sec_val}:{ls}:{ev.magnitude:.4f}",
        "Colon without sec if None (raw float)": f"{ev.parent_hash}:{ev.event_id}:{ev.observer_id}:{pri}:{sec_val}:{ls}:{ev.magnitude}",
        "Pipe delimiter": f"{ev.parent_hash}|{ev.event_id}|{ev.observer_id}|{pri}|{sec_val or 'NONE'}|{ls}|{ev.magnitude}",
        "Concatenated (no delim)": f"{ev.parent_hash}{ev.event_id}{ev.observer_id}{pri}{sec_val}{ls}{ev.magnitude}",
    }

    print("\n=== TRIAL MATCHES ===")
    for label, raw_str in trials.items():
        h = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        match = (h == ev.state_hash)
        print(f"  [{'MATCH!' if match else 'FAIL'}] {label}")
        if match:
            print(f"  >>> Winning Canonical Template: {raw_str}")

    print("=====================\n")
finally:
    db.close()
