import hashlib
import json
import time
from typing import List, Dict, Optional

# =====================================================================
# MODULE: CHAMBER Σ-11 (MERKLE VERIFICATION)
# =====================================================================
class ChamberSigma11:
    """
    Cryptographic verification module ensuring the immutable integrity 
    of state transitions prior to DAG ingestion.
    """
    @staticmethod
    def generate_truth_hash(event_payload: Dict, parent_hashes: List[str]) -> str:
        """Generates a Merkle-compliant cryptographic seal for the event."""
        block_content = {
            "timestamp": time.time(),
            "parents": sorted(parent_hashes),
            "payload": event_payload
        }
        serialized_block = json.dumps(block_content, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized_block).hexdigest()

    @staticmethod
    def verify_lineage(node_hash: str, event_payload: Dict, parent_hashes: List[str], timestamp: float) -> bool:
        """Validates that a node's hash matches its constituent payload and ancestry."""
        block_content = {
            "timestamp": timestamp,
            "parents": sorted(parent_hashes),
            "payload": event_payload
        }
        serialized_block = json.dumps(block_content, sort_keys=True).encode('utf-8')
        calculated_hash = hashlib.sha256(serialized_block).hexdigest()
        return node_hash == calculated_hash


# =====================================================================
# MODULE: TRUTH-STATE DAG & ASH ARCHIVE
# =====================================================================
class TruthStateNode:
    def __init__(self, node_hash: str, parent_hashes: List[str], payload: Dict, timestamp: float):
        self.node_hash = node_hash
        self.parent_hashes = parent_hashes
        self.payload = payload
        self.timestamp = timestamp
        # Ontological state is locked upon initialization (Never-Overwrite)
        self._is_sealed = True 

class TruthStateDAG:
    def __init__(self):
        # Genesis state initialization
        self.nodes: Dict[str, TruthStateNode] = {}
        self.frontier: List[str] = [] # Tracks the current DAG leaves

    def append_node(self, node: TruthStateNode):
        """Appends a verified node to the DAG and updates the frontier."""
        self.nodes[node.node_hash] = node
        
        # Remove parents from the frontier (they are no longer leaves)
        for parent_hash in node.parent_hashes:
            if parent_hash in self.frontier:
                self.frontier.remove(parent_hash)
                
        # Add the new node to the frontier
        self.frontier.append(node.node_hash)
        
        # Trigger event emission to the Ash Archive (Simulated)
        self._commit_to_ash_archive(node)

    def _commit_to_ash_archive(self, node: TruthStateNode):
        """Simulates the append-only write to deep storage."""
        print(f"[ASH ARCHIVE] Committed Truth-State: {node.node_hash[:8]}... | Parents: {len(node.parent_hashes)}")


# =====================================================================
# MAIN INGESTION PIPELINE
# =====================================================================
def ingest_event(dag: TruthStateDAG, sigma_11: ChamberSigma11, payload: Dict, forced_parents: Optional[List[str]] = None) -> str:
    """
    The Magisterial Kernel's primary ingestion loop. 
    Routes raw events through Σ-11 verification before DAG integration.
    """
    print(f"\n[INGESTION] Receiving event: {payload.get('action', 'UNKNOWN')}")
    
    # 1. Determine Ancestry
    parent_hashes = forced_parents if forced_parents is not None else dag.frontier.copy()
    
    # 2. Chamber Σ-11 Verification & Hashing
    timestamp = time.time()
    truth_hash = sigma_11.generate_truth_hash(payload, parent_hashes)
    print(f"[Σ-11] Truth-Hash Generated: {truth_hash}")
    
    # Optional: Redundant sanity check to ensure Σ-11 logic holds
    if not sigma_11.verify_lineage(truth_hash, payload, parent_hashes, timestamp):
        raise ValueError("[FATAL] Chamber Σ-11 Merkle Verification Failed. Event rejected.")
    
    # 3. Construct Immutable Truth-State Node
    new_node = TruthStateNode(
        node_hash=truth_hash,
        parent_hashes=parent_hashes,
        payload=payload,
        timestamp=timestamp
    )
    
    # 4. Append to Truth-State DAG
    dag.append_node(new_node)
    return truth_hash

# =====================================================================
# RUNTIME EXECUTION
# =====================================================================
if __name__ == "__main__":
    dag = TruthStateDAG()
    chamber_sigma_11 = ChamberSigma11()
    
    genesis_payload = {"action": "SYSTEM_INITIALIZE", "state": "KENOMA_VOID"}
    ingest_event(dag, chamber_sigma_11, genesis_payload, forced_parents=["00000000000000000000000000000000"])
    
    event_1 = {"action": "CHARACTER_SPAWN", "entity": "The Wanderer", "location": "The Index Threshold"}
    ingest_event(dag, chamber_sigma_11, event_1)
    
    event_2 = {"action": "WORLD_LAW_SHIFT", "parameter": "GRAVITY_CONST", "value": 0.8}
    ingest_event(dag, chamber_sigma_11, event_2)
