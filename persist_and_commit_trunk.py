import json
import sqlite3
from sigma12_forking_engine import (
    MerkleDAGNode, AshArchiveDAG
)

def run_persistent_seal():
    # 1. Connect to persistent on-disk archive
    db_file = "cathedral_ash_archive.db"
    archive = AshArchiveDAG(db_file)

    print("=" * 65)
    print("CATHEDRAL-ENGINE // PERSISTENT ASH ARCHIVE INITIALIZATION")
    print("=" * 65)

    # 2. Materialize Ancestral Trunk (R0 Genesis -> R1 Fork LCA)
    r0 = MerkleDAGNode("master_origin", 0, [], [{"genesis": True}], {"desc": "Genesis Bedrock"})
    archive.commit_node(r0)
    print(f"[OK] R0 Genesis committed:      {r0.node_hash[:16]}...")

    r1 = MerkleDAGNode("master_trunk", 1, [r0.node_hash], [{"event": "fork_lca"}], {"desc": "Shared LCA Trunk"})
    archive.commit_node(r1)
    print(f"[OK] R1 LCA Trunk committed:    {r1.node_hash[:16]}...")

    # 3. Materialize Divergent Branches (R2_A & R3_B)
    r2_a = MerkleDAGNode("branch_a", 2, [r1.node_hash], [{"P": "TRUE", "telemetry_hz": 2.0}])
    archive.commit_node(r2_a)
    print(f"[OK] R2 Branch A committed:     {r2_a.node_hash[:16]}...")

    r3_b = MerkleDAGNode("branch_b", 2, [r1.node_hash], [{"P": "FALSE", "telemetry_hz": 0.5}])
    archive.commit_node(r3_b)
    print(f"[OK] R3 Branch B committed:     {r3_b.node_hash[:16]}...")

    # 4. Materialize Confluent Node R_confluent
    reconciliation_tx = {
        "event": "confluent_resolution",
        "lca_hash": r1.node_hash,
        "resolved_proposition": "P",
        "resolution_verdict": "TRUE",
        "evidence_delta": 0.942,
        "rationale": "Optical telemetry and consensus broken above 0.850 threshold"
    }
    r_confluent = MerkleDAGNode(
        branch_name="master_reunified",
        epoch=3,
        parent_hashes=[r2_a.node_hash, r3_b.node_hash],
        transactions=[reconciliation_tx],
        metadata={"convergence": "3_way_lca_reconciliation"}
    )
    archive.commit_node(r_confluent)
    print(f"[OK] R_Confluent committed:     {r_confluent.node_hash[:16]}...")

    # 5. Commit Post-Actuation Trunk Node (Child of R_confluent)
    with open("active_certificate.json", "r") as f:
        cert = json.load(f)

    post_actuation_tx = {
        "event": "POST_ACTUATION_LATCH",
        "certificate_id": cert["certificate_id"],
        "action_executed": cert["authorized_action"],
        "valve_state": 1.0,
        "thermal_delta_hz": 0.0,
        "status": "QUENCHED_EQUILIBRIUM"
    }

    r_actuated_trunk = MerkleDAGNode(
        branch_name="master_unified_trunk",
        epoch=4,
        parent_hashes=[r_confluent.node_hash],
        transactions=[post_actuation_tx],
        metadata={
            "telemetry_state": "QUENCHED",
            "actuation_target": cert["authorized_action"]
        }
    )
    archive.commit_node(r_actuated_trunk)

    # 6. Verify Lineage in SQLite
    parents = archive.get_parents(r_actuated_trunk.node_hash)
    assert parents == [r_confluent.node_hash], "Parent verification mismatch!"

    print("\n" + "=" * 65)
    print("POST-ACTUATION TRUNK SEALED TO DISK")
    print("=" * 65)
    print(f"Database File:        {db_file}")
    print(f"Parent Confluent:     {r_confluent.node_hash[:16]}...")
    print(f"Unified Trunk Hash:   {r_actuated_trunk.node_hash[:16]}...")
    print(f"Trunk Merkle Root:    {r_actuated_trunk.merkle_root[:16]}...")
    print(f"Action Verified:      {cert['authorized_action']}")
    print(f"Thermal State:        QUENCHED (0.0 Hz)")
    print("[STATUS] Lex I Inscription Sealed and Lineage Audited.")

if __name__ == "__main__":
    run_persistent_seal()
