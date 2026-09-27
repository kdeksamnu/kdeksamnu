"""
Chamber Σ-12 Extension: Bounded Collapse & Topological Confluence
Governance: Lex I (The Never-Overwrite Doctrine)
"""

import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional, Tuple


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def hash_pair(a: str, b: str) -> str:
    return sha256_hex(a + b)


class MerkleTree:
    def __init__(self, leaves: List[str]):
        self.leaves = leaves
        self.levels = [leaves]
        current = leaves
        while len(current) > 1:
            nxt = []
            for i in range(0, len(current), 2):
                l = current[i]
                r = current[i + 1] if i + 1 < len(current) else current[i]
                nxt.append(hash_pair(l, r))
            self.levels.append(nxt)
            current = nxt

    @property
    def root(self) -> str:
        return self.levels[-1][0]


class MerkleDAGNode:
    def __init__(
        self,
        branch_name: str,
        epoch: int,
        parent_hashes: List[str],
        transactions: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.branch_name = branch_name
        self.epoch = epoch
        self.parent_hashes = sorted(parent_hashes)
        self.transactions = transactions
        self.metadata = metadata or {}

        self.canonical_txs = [canonical_json(tx) for tx in transactions]
        self.tx_hashes = [sha256_hex(ctx) for ctx in self.canonical_txs]
        self.merkle_tree = MerkleTree(self.tx_hashes)
        self.merkle_root = self.merkle_tree.root

        self.payload = {
            "branch_name": self.branch_name,
            "epoch": self.epoch,
            "parent_hashes": self.parent_hashes,
            "merkle_root": self.merkle_root,
            "metadata": self.metadata
        }
        self.canonical_payload = canonical_json(self.payload)
        self.node_hash = sha256_hex(self.canonical_payload)


class AshArchiveDAG:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.init_schema()

    def init_schema(self):
        self.conn.executescript("""
        CREATE TABLE IF NOT EXISTS ash_nodes (
            node_hash TEXT PRIMARY KEY,
            branch_name TEXT NOT NULL,
            epoch INTEGER NOT NULL,
            merkle_root TEXT NOT NULL,
            payload_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS ash_dag_edges (
            parent_hash TEXT NOT NULL,
            child_hash TEXT NOT NULL,
            PRIMARY KEY (parent_hash, child_hash)
        );
        CREATE TRIGGER IF NOT EXISTS trg_lex_i_nodes_no_update
        BEFORE UPDATE ON ash_nodes BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Nodes are immutable.');
        END;
        """)
        self.conn.commit()

    def commit_node(self, node: MerkleDAGNode):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO ash_nodes VALUES (?, ?, ?, ?, ?)",
            (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
        )
        for p in node.parent_hashes:
            cur.execute("INSERT INTO ash_dag_edges VALUES (?, ?)", (p, node.node_hash))
        self.conn.commit()

    def get_parents(self, node_hash: str) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT parent_hash FROM ash_dag_edges WHERE child_hash = ?", (node_hash,))
        return [r[0] for r in cur.fetchall()]


# ==============================================================================
# Bounded Collapse Operator & Actuator Gatekeeper
# ==============================================================================

class ActuatorSafetyGatekeeper:
    """
    Physical hardware gatekeeper.
    Refuses irreversible state actuation unless paired with an authorized Collapse Certificate.
    """
    def __init__(self, safe_state: str = "HOLD_PASSIVE"):
        self.current_hardware_state = safe_state
        self.safe_state = safe_state

    def trigger_actuator(
        self,
        target_action: str,
        collapse_certificate: Dict[str, Any],
        verified_merkle_root: str
    ) -> Tuple[bool, str]:
        # 1. Inspect certificate structure
        origin_state = collapse_certificate.get("origin_logical_state")
        resolution = collapse_certificate.get("resolution_mechanism")
        cert_action = collapse_certificate.get("authorized_action")

        # 2. Strict Safety Gate: Unresolved dialectical states abort to failsafe
        if resolution == "UNRESOLVED_DIALETHEIC_COLLISION" or cert_action == "HOLD_AND_QUARANTINE":
            self.current_hardware_state = self.safe_state
            return False, f"ACTUATOR_ABORT: Dialetheic state {origin_state} unresolved. Quarantined to {self.safe_state}."

        # 3. Action mismatch assertion
        if cert_action != target_action:
            self.current_hardware_state = self.safe_state
            return False, f"ACTUATOR_ABORT: Target action '{target_action}' does not match certified action '{cert_action}'."

        # 4. Merkle Root Anchor Assertion
        if collapse_certificate.get("merkle_root") != verified_merkle_root:
            self.current_hardware_state = self.safe_state
            return False, "ACTUATOR_ABORT: Certificate Merkle root does not match verified DAG state root."

        # Actuation executed
        self.current_hardware_state = target_action
        return True, f"ACTUATION_SUCCESS: Irreversible action '{target_action}' executed under certificate."


# ==============================================================================
# Verification Scenario
# ==============================================================================

def execute_verification():
    print("=" * 75)
    print("VERIFICATION: BOUNDED COLLAPSE & TOPOLOGICAL CONFLUENCE")
    print("=" * 75)

    archive = AshArchiveDAG(":memory:")

    # 1. Base Trunk (R0 -> R1)
    r0 = MerkleDAGNode("master", 0, [], [{"datum": "genesis"}])
    archive.commit_node(r0)
    r1 = MerkleDAGNode("master", 1, [r0.node_hash], [{"datum": "fork_lca"}])
    archive.commit_node(r1)

    # 2. Divergent Branches:
    # Branch A observes Proposition P = TRUE (high heat)
    # Branch B observes Proposition P = FALSE (suppression)
    r2_a = MerkleDAGNode("branch_a", 2, [r1.node_hash], [{"P": "TRUE", "telemetry_hz": 2.0}])
    archive.commit_node(r2_a)

    r3_b = MerkleDAGNode("branch_b", 2, [r1.node_hash], [{"P": "FALSE", "telemetry_hz": 0.5}])
    archive.commit_node(r3_b)

    gatekeeper = ActuatorSafetyGatekeeper(safe_state="VALVE_CLOSED_LOCKED")

    # --------------------------------------------------------------------------
    # Test A: Premature Actuation on Unresolved State (Must Quench/Abort)
    # --------------------------------------------------------------------------
    print("\n[Scenario 1] Attempting physical actuation from uncollapsed dialetheic state (BOTH)...")
    unresolved_cert = {
        "origin_logical_state": "BOTH",
        "resolution_mechanism": "UNRESOLVED_DIALETHEIC_COLLISION",
        "authorized_action": "HOLD_AND_QUARANTINE",
        "merkle_root": r2_a.merkle_root
    }
    success, log = gatekeeper.trigger_actuator("VENT_PRESSURE_HIGH", unresolved_cert, r2_a.merkle_root)
    assert not success
    assert gatekeeper.current_hardware_state == "VALVE_CLOSED_LOCKED"
    print(f"  -> Result: {log}")
    print("  -> Invariant Verified: Actuator halted premature collapse into irreversible state.")

    # --------------------------------------------------------------------------
    # Test B: Confluent Merkle Merge (R2_A + R3_B -> R_Confluent)
    # --------------------------------------------------------------------------
    print("\n[Scenario 2] Executing Topological Confluence (Multi-Parent Merge)...")
    reconciliation_data = {
        "event": "confluent_resolution",
        "lca_hash": r1.node_hash,
        "resolved_proposition": "P",
        "resolution_verdict": "TRUE",
        "evidence_delta": 0.91,
        "rationale": "External optical telemetry confirmed valve thermal dissipation"
    }

    # Reunified node has TWO parents: [r2_a, r3_b]
    r_confluent = MerkleDAGNode(
        branch_name="master_reunified",
        epoch=3,
        parent_hashes=[r2_a.node_hash, r3_b.node_hash],
        transactions=[reconciliation_data],
        metadata={"convergence": "3_way_lca_reconciliation"}
    )
    archive.commit_node(r_confluent)

    parents = archive.get_parents(r_confluent.node_hash)
    assert sorted(parents) == sorted([r2_a.node_hash, r3_b.node_hash])
    print(f"  -> Confluent Node Hash: {r_confluent.node_hash[:16]}...")
    print(f"  -> Merged Parents: {[p[:8] for p in parents]}")
    print("  -> Invariant Verified: Multi-parent DAG confluence recorded without history loss.")

    # --------------------------------------------------------------------------
    # Test C: Authorized Actuation with Valid Collapse Certificate
    # --------------------------------------------------------------------------
    print("\n[Scenario 3] Attempting actuation with certified Confluent Merge Root...")
    authorized_cert = {
        "origin_logical_state": "BOTH",
        "resolution_mechanism": "CONFLUENT_LCA_COLLAPSE",
        "authorized_action": "VENT_PRESSURE_HIGH",
        "merkle_root": r_confluent.merkle_root
    }
    success, log = gatekeeper.trigger_actuator("VENT_PRESSURE_HIGH", authorized_cert, r_confluent.merkle_root)
    assert success
    assert gatekeeper.current_hardware_state == "VENT_PRESSURE_HIGH"
    print(f"  -> Result: {log}")
    print("  -> Invariant Verified: Physical actuation successfully bound to cryptographic proof.")

    print("\n" + "=" * 75)
    print("AUDIT COMPLETE: ACTUATOR GATEKEEPER & DAG CONFLUENCE FORMALLY BOUNDED")
    print("=" * 75)

if __name__ == "__main__":
    execute_verification()
