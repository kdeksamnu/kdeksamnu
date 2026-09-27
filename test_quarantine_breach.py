import json
from validate_certificate import verify_collapse_certificate

# Generate sub-threshold certificate
sub_threshold_cert = {
  "certificate_id": "sha256_sub_threshold",
  "origin_logical_state": "BOTH",
  "target_node_hash": "node_hash_in_active_dag",
  "resolution_mechanism": "CONFLUENT_LCA_COLLAPSE",
  "symmetry_breaking_metric": {
    "metric": "sensor_consensus_delta",
    "value": 0.710,
    "threshold": 0.850
  },
  "authorized_action": "OPEN_HIGH_PRESSURE_VALVE",
  "risk_index": 0.88,
  "failsafe_action": "HOLD_AND_QUARANTINE"
}

with open("quarantine_test_cert.json", "w") as f:
    json.dump(sub_threshold_cert, f, indent=2)

print("\n--- INJECTING SUB-THRESHOLD CERTIFICATE (Delta: 0.710 < 0.850) ---")
try:
    verify_collapse_certificate("quarantine_test_cert.json")
except Exception as e:
    print(f"[EXPECTED ABORT] Safety Gatekeeper Activated: {e}")
