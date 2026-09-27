import json
import sqlite3
from sigma12_forking_engine import (
    MerkleDAGNode, AshArchiveDAG, canonical_json
)

def commit_post_actuation_trunk():
    # Connect to the active database where the confluent node exists
    archive = AshArchiveDAG("cathedral_engine_sigma12.db")

    # Load post-actuation record
    with open("active_certificate.json", "r") as f:
        cert = json.load(f)

    # Telemetry leaf payload
    post_actuation_tx = {
        "event": "POST_ACTUATION_LATCH",
        "certificate_id": cert["certificate_id"],
        "action_executed": cert["authorized_action"],
        "valve_state": 1.0,
        "thermal_delta_hz": 0.0,
        "status": "QUENCHED_EQUILIBRIUM"
    }

    # Retrieve the actual latest node hash dynamically from the active database
    confluent_node_hash = archive.get_latest_node_hash()
    if not confluent_node_hash:
        print("[ERROR] No valid parent node found in active database.")
        return

    # Create the unified successor trunk node
    r_actuated_trunk = MerkleDAGNode(
        branch_name="master_unified_trunk",
        epoch=4,
        parent_hashes=[confluent_node_hash],
        transactions=[post_actuation_tx],
        metadata={
            "telemetry_state": "QUENCHED",
            "actuation_target": cert["authorized_action"]
        }
    )

    # Inscribe to SQLite Merkle DAG under Lex I
    archive.commit_node(r_actuated_trunk)

    # Extract inclusion proof for the actuation event
    tx_hash = r_actuated_trunk.tx_hashes[0]
    proof = r_actuated_trunk.merkle_tree.get_proof(0)

    print("=" * 65)
    print("CATHEDRAL-ENGINE // POST-ACTUATION TRUNK SEALED")
    print("=" * 65)
    print(f"Parent Confluent Hash: {confluent_node_hash[:16]}...")
    print(f"New Trunk Node Hash:   {r_actuated_trunk.node_hash[:16]}...")
    print(f"New Merkle Root:       {r_actuated_trunk.merkle_root[:16]}...")
    print(f"Actuation Leaf Hash:   {tx_hash[:16]}...")
    print(f"Proof Path Elements:   {len(proof)}")
    print("[STATUS] Operational Cycle Complete: Superposition -> Confluence -> Actuation -> Quenched Inscription.")

if __name__ == "__main__":
    commit_post_actuation_trunk()
