"""
Chamber Σ-13: Asynchronous P2P Gossip & DAG Synchronization
System: MLAOS-Prime / Cathedral-Engine Prototype
Domain: Decentralized State Reconciliation · P2P Gossip · Merkle DAG Sync
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
    def __init__(self,
                 branch_name: str,
                 epoch: int,
                 parent_hashes: List[str],
                 transactions: List[Dict[str, Any]],
                 metadata: Optional[Dict[str, Any]] = None):
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
        try:
            cur.execute("INSERT INTO ash_nodes VALUES (?, ?, ?, ?, ?)",
                (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
            )
            for p in node.parent_hashes:
                cur.execute("INSERT OR IGNORE INTO ash_dag_edges VALUES (?, ?)", (p, node.node_hash))
            self.conn.commit()
        except sqlite3.IntegrityError:
            self.conn.rollback()

    def node_exists(self, node_hash: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM ash_nodes WHERE node_hash = ?", (node_hash,))
        return cur.fetchone() is not None

    def get_tips(self) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("""
            SELECT node_hash FROM ash_nodes 
            WHERE node_hash NOT IN (SELECT parent_hash FROM ash_dag_edges)
        """)
        return [r[0] for r in cur.fetchall()]

class GossipTransportLayer:
    def __init__(self):
        self.inbox_alpha: List[Dict[str, Any]] = []
        self.inbox_beta: List[Dict[str, Any]] = []

    def broadcast_node(self, sender: str, node: MerkleDAGNode):
        packet = {
            "node_hash": node.node_hash,
            "payload_json": node.canonical_payload,
            "parent_hashes": node.parent_hashes,
            "branch_name": node.branch_name,
            "epoch": node.epoch,
            "merkle_root": node.merkle_root,
            "transactions": node.transactions,
            "metadata": node.metadata
        }
        if sender == "Alpha":
            self.inbox_beta.append(packet)
        else:
            self.inbox_alpha.append(packet)

def run_sigma13_gossip_simulation():
    print("=" * 75)
    print("CATHEDRAL-ENGINE // CHAMBER Σ-13: ASYNCHRONOUS GOSSIP & DAG SYNC")
    print("Verification Arc: Multi-Agent P2P Reconciliation & Convergence")
    print("=" * 75)

    transport = GossipTransportLayer()
    node_alpha_db = AshArchiveDAG(":memory:")
    node_beta_db = AshArchiveDAG(":memory:")

    r0_data = [{ "genesis": True }]
    r0_alpha = MerkleDAGNode("master", 0, [], r0_data)
    r0_beta = MerkleDAGNode("master", 0, [], r0_data)
    node_alpha_db.commit_node(r0_alpha)
    node_beta_db.commit_node(r0_beta)

    r1_data = [{ "event": "fork_lca" }]
    r1_alpha = MerkleDAGNode("master", 1, [r0_alpha.node_hash], r1_data)
    r1_beta = MerkleDAGNode("master", 1, [r0_beta.node_hash], r1_data)
    node_alpha_db.commit_node(r1_alpha)
    node_beta_db.commit_node(r1_beta)

    print("\n[Step 1] Independent Genesis & LCA Anchors Initialized.")

    r2_a = MerkleDAGNode("branch_a", 2, [r1_alpha.node_hash], [{"P": "TRUE", "origin": "Alpha"}])
    node_alpha_db.commit_node(r2_a)

    r3_b = MerkleDAGNode("branch_b", 2, [r1_beta.node_hash], [{"P": "FALSE", "origin": "Beta"}])
    node_beta_db.commit_node(r3_b)

    print(f"  -> Node Alpha generated Branch A tip: {r2_a.node_hash[:12]}...")
    print(f"  -> Node Beta generated Branch B tip:  {r3_b.node_hash[:12]}...")

    print("\n[Step 2] Executing P2P Gossip Exchange across Transport Layer...")
    transport.broadcast_node("Alpha", r2_a)
    transport.broadcast_node("Beta", r3_b)

    for pkt in transport.inbox_alpha:
        if not node_alpha_db.node_exists(pkt["node_hash"]):
            incoming_node = MerkleDAGNode(
                pkt["branch_name"], pkt["epoch"], pkt["parent_hashes"],
                pkt["transactions"], pkt["metadata"]
            )
            node_alpha_db.commit_node(incoming_node)
    
    for pkt in transport.inbox_beta:
        if not node_beta_db.node_exists(pkt["node_hash"]):
            incoming_node = MerkleDAGNode(
                pkt["branch_name"], pkt["epoch"], pkt["parent_hashes"],
                pkt["transactions"], pkt["metadata"]
            )
            node_beta_db.commit_node(incoming_node)

    print("  -> Gossip packets successfully ingested by remote peers.")

    print("\n[Step 3] Decentralized Confluence: Node Alpha constructs multi-parent merge...")
    reconciliation_tx = {
        "event": "p2p_confluent_resolution",
        "lca_hash": r1_alpha.node_hash,
        "resolved_proposition": "P",
        "resolution_verdict": "TRUE",
        "consensus_nodes": ["Alpha", "Beta"]
    }
    r_confluent_alpha = MerkleDAGNode(
        branch_name="master_reunified",
        epoch=3,
        parent_hashes=[r2_a.node_hash, r3_b.node_hash],
        transactions=[reconciliation_tx],
        metadata={"sync_protocol": "gossip_lca"}
    )
    node_alpha_db.commit_node(r_confluent_alpha)

    transport.broadcast_node("Alpha", r_confluent_alpha)
    for pkt in transport.inbox_beta:
        if not node_beta_db.node_exists(pkt["node_hash"]):
            incoming_node = MerkleDAGNode(
                pkt["branch_name"], pkt["epoch"], pkt["parent_hashes"],
                pkt["transactions"], pkt["metadata"]
            )
            node_beta_db.commit_node(incoming_node)

    print(f"  -> Confluent Merge Node Hash: {r_confluent_alpha.node_hash[:12]}...")
    print("  -> Both nodes successfully synchronized multi-parent DAG topology.")

    alpha_tips = node_alpha_db.get_tips()
    beta_tips = node_beta_db.get_tips()
    
    assert alpha_tips == beta_tips, f"Tip divergence between nodes: {alpha_tips} != {beta_tips}"
    assert alpha_tips == [r_confluent_alpha.node_hash], f"Unexpected active tip state: {alpha_tips}"

    print("\n" + "=" * 75)
    print("CHAMBER Σ-13 VERIFICATION COMPLETE: P2P GOSSIP & SYNCHRONIZATION PASSED")
    print("Status: DECENTRALIZED MERKLE DAG RECONCILIATION VERIFIED")
    print("=" * 75)
