import json
import hashlib
import time

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def record_actuation_telemetry():
    with open("active_certificate.json", "r") as f:
        cert = json.load(f)

    # Simulated physical actuation & telemetry feedback
    actuation_record = {
        "event_type": "PHYSICAL_ACTUATION_COMMITTED",
        "certificate_id": cert["certificate_id"],
        "target_node_hash": cert["target_node_hash"],
        "action_executed": cert["authorized_action"],
        "timestamp_epoch": time.time(),
        "telemetry_post_actuation": {
            "valve_position": 1.0,           # Fully open
            "manifold_pressure_psi": 14.7,    # Normalized
            "thermal_delta_rate_hz": 0.0      # Quenched
        },
        "actuator_status": "LATCHED_EXECUTION"
    }

    payload_canonical = json.dumps(actuation_record, sort_keys=True, separators=(',', ':'))
    record_hash = sha256_hex(payload_canonical)

    print("=" * 60)
    print("CATHEDRAL-ENGINE // POST-ACTUATION TELEMETRY INSCRIPTION")
    print("=" * 60)
    print(f"Action:          {actuation_record['action_executed']}")
    print(f"Certificate:     {cert['certificate_id']}")
    print(f"Valve State:     OPEN (1.0)")
    print(f"Thermal State:   QUENCHED (0.0 Hz)")
    print(f"Inscription ID:  {record_hash}")
    print("[STATUS] Lex I Inscription Ready for Ash Archive Trunk Commit.")

if __name__ == "__main__":
    record_actuation_telemetry()
