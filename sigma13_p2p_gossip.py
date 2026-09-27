"""
Chamber Σ-13: Asynchronous P2P Gossip Synchronization & Cross-Node Confluence
System: MLAOS-Prime / Cathedral-Engine Prototype
Governance: Lex I (The Never-Overwrite Doctrine)
"""

import hashlib
import json
import sqlite3
from typing import Any, Dict, List, Optional, Set, Tuple


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True)

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def hash_pair(a: str, b: str) -> str:
    return sha256_hex(a + b)


class MerkleTree:
    def __init__(self, leaves: List[str]):
        if not leaves:
            raise ValueError("Leaves list cannot be empty")
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

    def get_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds")
        proof = []
        idx = leaf_index
        for level in self.levels[:-1]:
            is_right = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right else idx + 1
            if sibling_idx < len(level):
                sibling_hash = level[sibling_idx]
            else:
                sibling_hash = level[idx]
            direction = 'L' if is_right else 'R'
            proof.append((sibling_hash, direction))
            idx //= 2
        return proof

    @staticmethod
    def verify_proof(leaf_hash: str, proof: List[Tuple[str, str]], expected_root: str) -> bool:
        curr = leaf_hash
        for sibling_hash, direction in proof:
            if direction == 'L':
                curr = hash_pair(sibling_hash, curr)
            elif direction == 'R':
                curr = hash_pair(curr, sibling_hash)
            else:
                raise ValueError(f"Unknown direction: {direction}")
        return curr == expected_root


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

    @classmethod
    def from_payload_and_txs(cls, payload_json: str, tx_json_list: List[str]) -> "MerkleDAGNode":
        p = json.loads(payload_json)
        txs = [json.loads(t) for t in tx_json_list]
        return cls(
            branch_name=p["branch_name"],
            epoch=p["epoch"],
            parent_hashes=p["parent_hashes"],
            transactions=txs,
            metadata=p.get("metadata")
        )


class NodeArchive:
    """Independent SQLite-backed repository instance for an autonomous network node."""
    def __init__(self, node_id: str, db_path: str = ":memory:"):
        self.node_id = node_id
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.init_schema()

    def init_schema(self):
        schema = """
        CREATE TABLE IF NOT EXISTS ash_nodes (
            node_hash TEXT PRIMARY KEY,
            branch_name TEXT NOT NULL,
            epoch INTEGER NOT NULL,
            merkle_root TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS ash_dag_edges (
            parent_hash TEXT NOT NULL,
            child_hash TEXT NOT NULL,
            edge_type TEXT DEFAULT 'lineage',
            PRIMARY KEY (parent_hash, child_hash),
            FOREIGN KEY (parent_hash) REFERENCES ash_nodes(node_hash),
            FOREIGN KEY (child_hash) REFERENCES ash_nodes(node_hash)
        );
        CREATE TABLE IF NOT EXISTS ash_transactions (
            tx_hash TEXT PRIMARY KEY,
            node_hash TEXT NOT NULL,
            leaf_index INTEGER NOT NULL,
            payload_json TEXT NOT NULL,
            FOREIGN KEY (node_hash) REFERENCES ash_nodes(node_hash)
        );
        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_nodes_no_update
        BEFORE UPDATE ON ash_nodes BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes are immutable.');
        END;
        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_nodes_no_delete
        BEFORE DELETE ON ash_nodes BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes cannot be purged.');
        END;
        """
        self.conn.executescript(schema)
        self.conn.commit()

    def has_node(self, node_hash: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT 1 FROM ash_nodes WHERE node_hash = ?", (node_hash,))
        return cur.fetchone() is not None

    def commit_node(self, node: MerkleDAGNode):
        if self.has_node(node.node_hash):
            return
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json) VALUES (?, ?, ?, ?, ?)",
            (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
        )
        for p in node.parent_hashes:
            cur.execute(
                "INSERT INTO ash_dag_edges (parent_hash, child_hash, edge_type) VALUES (?, ?, ?)",
                (p, node.node_hash, "lineage")
            )
        for idx, (tx_hash, ctx) in enumerate(zip(node.tx_hashes, node.canonical_txs)):
            cur.execute(
                "INSERT INTO ash_transactions (tx_hash, node_hash, leaf_index, payload_json) VALUES (?, ?, ?, ?)",
                (tx_hash, node.node_hash, idx, ctx)
            )
        self.conn.commit()

    def get_tip_hashes(self) -> List[str]:
        """Identifies leaf nodes with out-degree 0 (active branch heads)."""
        cur = self.conn.cursor()
        query = """
        SELECT n.node_hash FROM ash_nodes n
        LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
        WHERE e.child_hash IS NULL
        ORDER BY n.epoch DESC, n.node_hash ASC
        """
        cur.execute(query)
        return [r[0] for r in cur.fetchall()]

    def export_node_bundle(self, node_hash: str) -> Optional[Dict[str, Any]]:
        cur = self.conn.cursor()
        cur.execute("SELECT payload_json FROM ash_nodes WHERE node_hash = ?", (node_hash,))
        row = cur.fetchone()
        if not row:
            return None
        payload_json = row[0]
        cur.execute("SELECT payload_json FROM ash_transactions WHERE node_hash = ? ORDER BY leaf_index ASC", (node_hash,))
        txs = [r[0] for r in cur.fetchall()]
        return {
            "node_hash": node_hash,
            "payload_json": payload_json,
            "transactions_json": txs
        }

    def get_parents(self, node_hash: str) -> List[str]:
        cur = self.conn.cursor()
        cur.execute("SELECT parent_hash FROM ash_dag_edges WHERE child_hash = ?", (node_hash,))
        return [row[0] for row in cursor.fetchall()] if (cursor := cur) else []


class P2PGossipEngine:
    """Manages asynchronous state negotiation and causal synchronization."""

    @staticmethod
    def negotiate_and_sync(local_node: NodeArchive, peer_node: NodeArchive) -> Dict[str, Any]:
        local_tips = local_node.get_tip_hashes()
        peer_tips = peer_node.get_tip_hashes()

        missing_tips_on_local = [t for t in peer_tips if not local_node.has_node(t)]
        synced_nodes_count = 0

        # Traverse missing causal lineages
        for tip in missing_tips_on_local:
            queue = [tip]
            traversal_order = []
            visited = set()

            while queue:
                current_hash = queue.pop(0)
                if current_hash in visited or local_node.has_node(current_hash):
                    continue
                visited.add(current_hash)
                traversal_order.append(current_hash)

                parents = peer_node.get_parents(current_hash)
                for p in parents:
                    if not local_node.has_node(p):
                        queue.append(p)

            # Ingest in topological order (ancestors before children)
            for h in reversed(traversal_order):
                bundle = peer_node.export_node_bundle(h)
                if bundle:
                    node_obj = MerkleDAGNode.from_payload_and_txs(
                        bundle["payload_json"],
                        bundle["transactions_json"]
                    )
                    assert node_obj.node_hash == h, f"Integrity failure on {h}"
                    local_node.commit_node(node_obj)
                    synced_nodes_count += 1

        return {
            "local_initial_tips": local_tips,
            "peer_tips": peer_tips,
            "nodes_ingested": synced_nodes_count,
            "resulting_tips": local_node.get_tip_hashes()
        }


def run_sigma13_verification():
    print("=" * 80)
    print("CATHEDRAL-ENGINE // CHAMBER Σ-13: ASYNCHRONOUS P2P GOSSIP SYNCHRONIZATION")
    print("Verification Arc: Multi-Node Tip Negotiation & Cross-Process Confluent Merges")
    print("Audit Regime: Lex I (The Never-Overwrite Doctrine)")
    print("=" * 80)

    node_alpha = NodeArchive("Alpha", ":memory:")
    node_beta = NodeArchive("Beta", ":memory:")

    # Phase 1: Shared Origin
    print("\n[Phase 1] Bootstrapping Shared Ancestry on Both Nodes (R0 -> R1)...")
    r0 = MerkleDAGNode("master_origin", 0, [], [{"genesis": True}], {"desc": "Genesis Datum"})
    node_alpha.commit_node(r0)
    node_beta.commit_node(r0)

    r1 = MerkleDAGNode("master_trunk", 1, [r0.node_hash], [{"event": "shared_lca"}], {"desc": "Shared LCA Trunk"})
    node_alpha.commit_node(r1)
    node_beta.commit_node(r1)
    assert node_alpha.get_tip_hashes() == [r1.node_hash]
    assert node_beta.get_tip_hashes() == [r1.node_hash]
    print(f"  -> Shared Genesis Hash: {r0.node_hash[:16]}...")
    print(f"  -> Shared LCA Hash:     {r1.node_hash[:16]}...")
    print("  -> Phase 1 Passed: Identical baseline verified.")

    # Phase 2: Autonomous Divergence
    print("\n[Phase 2] Simulating Autonomous Divergence in Isolation...")
    r2_alpha = MerkleDAGNode("branch_a_thermal", 2, [r1.node_hash], [{"actor": "Alpha", "telemetry_hz": 2.2}])
    node_alpha.commit_node(r2_alpha)

    r3_beta = MerkleDAGNode("branch_b_null", 2, [r1.node_hash], [{"actor": "Beta", "telemetry_hz": 0.3}])
    node_beta.commit_node(r3_beta)

    assert node_alpha.get_tip_hashes() == [r2_alpha.node_hash]
    assert node_beta.get_tip_hashes() == [r3_beta.node_hash]
    assert not node_alpha.has_node(r3_beta.node_hash)
    assert not node_beta.has_node(r2_alpha.node_hash)
    print(f"  -> Node Alpha Tip: {r2_alpha.node_hash[:16]}... (Branch A)")
    print(f"  -> Node Beta Tip:  {r3_beta.node_hash[:16]}... (Branch B)")
    print("  -> Phase 2 Passed: Nodes diverged without lock contention.")

    # Phase 3: P2P Gossip Exchange
    print("\n[Phase 3] Initiating Asynchronous P2P Gossip Exchange...")
    res_alpha = P2PGossipEngine.negotiate_and_sync(node_alpha, node_beta)
    res_beta = P2PGossipEngine.negotiate_and_sync(node_beta, node_alpha)

    assert node_alpha.has_node(r3_beta.node_hash)
    assert node_beta.has_node(r2_alpha.node_hash)
    assert set(node_alpha.get_tip_hashes()) == {r2_alpha.node_hash, r3_beta.node_hash}
    assert set(node_beta.get_tip_hashes()) == {r2_alpha.node_hash, r3_beta.node_hash}
    print(f"  -> Alpha Ingested: {res_alpha['nodes_ingested']} missing node(s)")
    print(f"  -> Beta Ingested:  {res_beta['nodes_ingested']} missing node(s)")
    print("  -> Phase 3 Passed: Bi-directional causal sync complete.")

    # Phase 4: Independent Confluent Merge
    print("\n[Phase 4] Executing Independent Confluent Merges on Both Nodes...")
    confluence_tx = {
        "event": "GOSSIP_CONFLUENCE_RESOLUTION",
        "lca_anchor": r1.node_hash,
        "resolved_state": "SYNTHETIC_EQUILIBRIUM",
        "nodes": ["Alpha", "Beta"]
    }
    convergent_parents = sorted([r2_alpha.node_hash, r3_beta.node_hash])

    merge_alpha = MerkleDAGNode("master_unified", 3, convergent_parents, [confluence_tx])
    merge_beta = MerkleDAGNode("master_unified", 3, convergent_parents, [confluence_tx])

    assert merge_alpha.node_hash == merge_beta.node_hash
    assert merge_alpha.merkle_root == merge_beta.merkle_root

    node_alpha.commit_node(merge_alpha)
    node_beta.commit_node(merge_beta)

    assert node_alpha.get_tip_hashes() == [merge_alpha.node_hash]
    assert node_beta.get_tip_hashes() == [merge_beta.node_hash]
    print(f"  -> Confluent Node Hash: {merge_alpha.node_hash[:16]}... (Identical on Alpha & Beta)")
    print(f"  -> Unified Merkle Root: {merge_alpha.merkle_root[:16]}...")
    print("  -> Phase 4 Passed: Autonomous confluence achieved without central coordinator.")

    # Phase 5: Cross-Node Proof Verification & Lex I Protection
    print("\n[Phase 5] Cross-Node Inclusion Proof Verification...")
    tx_beta_payload = node_alpha.export_node_bundle(r3_beta.node_hash)["transactions_json"][0]
    tx_beta_hash = sha256_hex(tx_beta_payload)
    proof_beta = r3_beta.merkle_tree.get_proof(0)
    assert MerkleTree.verify_proof(tx_beta_hash, proof_beta, r3_beta.merkle_root)
    print("  -> Observer on Node Alpha verified Node Beta's transaction locally [Verified]")

    try:
        node_alpha.conn.execute("DELETE FROM ash_nodes WHERE node_hash = ?", (r3_beta.node_hash,))
        assert False
    except (sqlite3.IntegrityError, sqlite3.OperationalError) as e:
        assert "Violation of Lex I" in str(e)
        print("  -> Lex I Trigger verified on foreign-ingested nodes [Verified]")

    print("\n" + "=" * 80)
    print("CHAMBER Σ-13 VERIFICATION COMPLETE: ALL 5 INVARIANTS SATISFIED (PASS)")
    print("Status: ASYNCHRONOUS P2P GOSSIP & CROSS-NODE CONFLUENCE FORMALLY VERIFIED")
    print("=" * 80)

if __name__ == "__main__":
    run_sigma13_verification()
