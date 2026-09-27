"""
Chamber Σ-12: The Forking Memory — Core Engine
System: MLAOS-Prime / Cathedral-Engine Prototype
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

def hash_pair(left_hash: str, right_hash: str) -> str:
    return sha256_hex(left_hash + right_hash)

class MerkleTree:
    def __init__(self, leaves: List[str]):
        if not leaves:
            raise ValueError("Cannot build Merkle tree with zero leaves")
        self.leaves = leaves
        self.levels: List[List[str]] = [leaves]
        self._build_tree()

    def _build_tree(self):
        current = self.leaves
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else current[i]
                next_level.append(hash_pair(left, right))
            self.levels.append(next_level)
            current = next_level

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
    def __init__(self, db_path: str = "cathedral_engine_sigma12.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.init_schema()

    def init_schema(self):
        schema_sql = """
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
            edge_type TEXT DEFAULT 'branch',
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
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes are strictly immutable.');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_nodes_no_delete
        BEFORE DELETE ON ash_nodes BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive nodes cannot be purged.');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_dag_edges_no_update
        BEFORE UPDATE ON ash_dag_edges BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: DAG lineage edges are strictly immutable.');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_dag_edges_no_delete
        BEFORE DELETE ON ash_dag_edges BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: DAG lineage edges cannot be purged.');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_tx_no_update
        BEFORE UPDATE ON ash_transactions BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive transactions are strictly immutable.');
        END;

        CREATE TRIGGER IF NOT EXISTS trg_lex_i_ash_tx_no_delete
        BEFORE DELETE ON ash_transactions BEGIN
            SELECT RAISE(ABORT, 'Violation of Lex I: Archive transactions cannot be purged.');
        END;
        """
        self.conn.executescript(schema_sql)
        self.conn.commit()

    def get_parents(self, node_hash: str) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT parent_hash FROM ash_dag_edges WHERE child_hash = ?", (node_hash,))
        return [row[0] for row in cursor.fetchall()]

    def commit_node(self, node: MerkleDAGNode):
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR IGNORE INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json)
            VALUES (?, ?, ?, ?, ?)
            """,
            (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
        )

        for p_hash in node.parent_hashes:
            cursor.execute(
                """
                INSERT OR IGNORE INTO ash_dag_edges (parent_hash, child_hash, edge_type)
                VALUES (?, ?, ?)
                """,
                (p_hash, node.node_hash, "lineage")
            )

        for idx, (tx_hash, ctx) in enumerate(zip(node.tx_hashes, node.canonical_txs)):
            cursor.execute(
                """
                INSERT OR IGNORE INTO ash_transactions (tx_hash, node_hash, leaf_index, payload_json)
                VALUES (?, ?, ?, ?)
                """,
                (tx_hash, node.node_hash, idx, ctx)
            )

        self.conn.commit()

    def get_latest_node_hash(self) -> Optional[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT node_hash FROM ash_nodes ORDER BY rowid DESC LIMIT 1;")
        row = cursor.fetchone()
        return row[0] if row else None
