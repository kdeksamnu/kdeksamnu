import hashlib
import json
import time
from typing import Dict, List, Tuple, Optional

class MerkleTree:
    """Utility class to construct Merkle trees and generate inclusion proofs."""
    def __init__(self, leaves: List[str]):
        self.leaves = [self._hash(leaf) for leaf in leaves]
        self.tree = [self.leaves]
        self._build_tree()

    @staticmethod
    def _hash(data: str) -> str:
        return hashlib.sha256(data.encode('utf-8')).hexdigest()

    def _build_tree(self):
        while len(self.tree[-1]) > 1:
            current_layer = self.tree[-1]
            next_layer = []
            for i in range(0, len(current_layer), 2):
                left = current_layer[i]
                right = current_layer[i + 1] if i + 1 < len(current_layer) else left
                combined = hashlib.sha256((left + right).encode('utf-8')).hexdigest()
                next_layer.append(combined)
            self.tree.append(next_layer)

    def get_root(self) -> str:
        return self.tree[-1][0] if self.tree and self.tree[-1] else ""

    def get_proof(self, index: int) -> List[Tuple[str, str]]:
        """Generates proof path tuple: (sibling_hash, direction 'LEFT'|'RIGHT')."""
        proof = []
        for layer in range(len(self.tree) - 1):
            current_layer = self.tree[layer]
            is_right = (index % 2 == 1)
            sibling_index = index - 1 if is_right else index + 1
            
            if sibling_index < len(current_layer):
                sibling_hash = current_layer[sibling_index]
                direction = "LEFT" if is_right else "RIGHT"
                proof.append((sibling_hash, direction))
            else:
                proof.append((current_layer[index], "RIGHT"))
                
            index //= 2
        return proof


class ActuatorSafetyGatekeeper:
    """
    Actuator Safety Gatekeeper for Chamber Sigma-12.
    Verifies Merkle inclusion proofs against anchored ledger roots 
    prior to issuing hardware execution signals.
    """
    def __init__(self, anchored_roots: Optional[List[str]] = None):
        self.anchored_roots = set(anchored_roots or [])

    def register_anchored_root(self, root_hash: str):
        self.anchored_roots.add(root_hash)
        print(f"[GATEKEEPER ARCHIVE] Registered Anchored Merkle Root: {root_hash[:16]}...")

    @staticmethod
    def compute_leaf_hash(payload: Dict) -> str:
        serialized = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    def verify_inclusion_proof(
        self, 
        leaf_hash: str, 
        proof_path: List[Tuple[str, str]], 
        target_root: str
    ) -> bool:
        current_hash = leaf_hash
        for sibling_hash, direction in proof_path:
            if direction == "LEFT":
                combined = sibling_hash + current_hash
            else:
                combined = current_hash + sibling_hash
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        return current_hash == target_root

    def authorize_actuation(
        self, 
        actuator_id: str, 
        payload: Dict, 
        proof_path: List[Tuple[str, str]], 
        target_root: str
    ) -> Dict:
        leaf_hash = self.compute_leaf_hash(payload)
        print(f"\n[ACTUATOR GATEKEEPER] Evaluating Access Request for Hardware: {actuator_id}")
        print(f" - Payload Hash : {leaf_hash[:16]}...")
        print(f" - Target Root  : {target_root[:16]}...")

        if target_root not in self.anchored_roots:
            print(f"[SECURITY ALERT] Target Root {target_root[:16]}... NOT found in Anchored Ash Archive!")
            return {
                "status": "DENIED",
                "reason": "UNANCHORED_MERKLE_ROOT",
                "actuator_id": actuator_id,
                "timestamp": time.time()
            }

        is_valid = self.verify_inclusion_proof(leaf_hash, proof_path, target_root)
        if not is_valid:
            print(f"[SECURITY ALERT] Inclusion proof verification FAILED for {actuator_id}!")
            return {
                "status": "DENIED",
                "reason": "INVALID_MERKLE_INCLUSION_PROOF",
                "actuator_id": actuator_id,
                "timestamp": time.time()
            }

        collapse_certificate = hashlib.sha256(
            f"{leaf_hash}:{target_root}:{time.time()}".encode('utf-8')
        ).hexdigest()

        print(f"[ACCESS GRANTED] Merkle Proof Validated. Hardware Latch Engaged.")
        print(f" - Collapse Certificate (C_collapse): {collapse_certificate[:16]}...")

        return {
            "status": "AUTHORIZED",
            "actuator_id": actuator_id,
            "collapse_certificate": collapse_certificate,
            "target_root": target_root,
            "timestamp": time.time(),
            "hardware_signal": {
                "latch_voltage_mv": 3300,
                "duration_ms": 500,
                "state": "ACTIVE"
            }
        }

if __name__ == "__main__":
    payload_0 = {"actuator": "VALVE_SIGMA_01", "command": "OPEN", "pressure_target": 1.42}
    payload_1 = {"actuator": "PULSE_MOTOR_02", "command": "LATCH", "angle": 90.0}
    payload_2 = {"actuator": "RELAY_CATHEDRAL_04", "command": "DISCHARGE", "voltage": 24.0}
    payload_3 = {"actuator": "STASIS_FIELD_12", "command": "ENGAGE", "power_level": 0.85}

    leaves_raw = [
        json.dumps(payload_0, sort_keys=True),
        json.dumps(payload_1, sort_keys=True),
        json.dumps(payload_2, sort_keys=True),
        json.dumps(payload_3, sort_keys=True)
    ]

    tree = MerkleTree(leaves_raw)
    root = tree.get_root()

    gatekeeper = ActuatorSafetyGatekeeper()
    gatekeeper.register_anchored_root(root)

    target_payload = payload_1
    proof = tree.get_proof(index=1)
    
    result_valid = gatekeeper.authorize_actuation(
        actuator_id="PULSE_MOTOR_02",
        payload=target_payload,
        proof_path=proof,
        target_root=root
    )

    tampered_payload = {"actuator": "PULSE_MOTOR_02", "command": "OVERRIDE_MAX", "angle": 180.0}
    result_tampered = gatekeeper.authorize_actuation(
        actuator_id="PULSE_MOTOR_02",
        payload=tampered_payload,
        proof_path=proof,
        target_root=root
    )

    print("\n=================================================================")
    print("                    ACTUATION AUDIT SUMMARY                      ")
    print("=================================================================")
    print(f" Valid Request Status   : {result_valid['status']}")
    print(f" Tampered Request Status: {result_tampered['status']} ({result_tampered['reason']})")
    print("=================================================================")
