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
            # Pre-commit horizon check: if active tips == k_max, stratify idlest tip before adding new branch
            active_tips = self.get_active_tips()
            if len(active_tips) >= self.k_max and not any(p in [t[0] for t in active_tips] for p in node.parent_hashes):
                sorted_tips = sorted(active_tips, key=lambda x: x[1], reverse=True)
                idlest_tip = sorted_tips[0][0]
                cur.execute("UPDATE ash_nodes SET is_stratified = 1 WHERE node_hash = ?", (idlest_tip,))
                self.conn.commit()

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

if old_commit in code:
    code = code.replace(old_commit, new_commit)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched commit_node with pre-commit horizon bounding.")
else:
    print("[INFO] Commit pattern already updated or differs.")
