import re

with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_commit = """    def commit_node(self, node: MerkleDAGNode):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json, is_stratified, idle_counter) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload, node.is_stratified, 0)
            )
            for p in node.parent_hashes:
                cur.execute("INSERT OR IGNORE INTO ash_dag_edges VALUES (?, ?)", (p, node.node_hash))
            for idx, (tx_hash, ctx) in enumerate(zip(node.tx_hashes, node.canonical_txs)):
                cur.execute("INSERT OR IGNORE INTO ash_transactions VALUES (?, ?, ?, ?)", (tx_hash, node.node_hash, idx, ctx))
            self.conn.commit()
            self.enforce_horizon_governor()
        except sqlite3.IntegrityError:
            self.conn.rollback()"""

new_commit = """    def commit_node(self, node: MerkleDAGNode):
        cur = self.conn.cursor()
        try:
            cur.execute(
                "INSERT INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json, is_stratified, idle_counter) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload, node.is_stratified, 0)
            )
            for p in node.parent_hashes:
                cur.execute("INSERT OR IGNORE INTO ash_dag_edges VALUES (?, ?)", (p, node.node_hash))
            for idx, (tx_hash, ctx) in enumerate(zip(node.tx_hashes, node.canonical_txs)):
                cur.execute("INSERT OR IGNORE INTO ash_transactions VALUES (?, ?, ?, ?)", (tx_hash, node.node_hash, idx, ctx))
            self.conn.commit()
            # Enforce horizon governor immediately after commit to prune excess tips
            self.enforce_horizon_governor()
        except sqlite3.IntegrityError:
            self.conn.rollback()"""

if old_commit in code:
    code = code.replace(old_commit, new_commit)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched commit_node order of execution.")
else:
    print("[INFO] Pattern already updated or needs manual check.")
