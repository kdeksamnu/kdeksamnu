with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_get_tips = """    def get_active_tips(self) -> List[Tuple[str, int]]:
        cur = self.conn.cursor()
        cur.execute(\"\"\"
            SELECT n.node_hash, n.idle_counter FROM ash_nodes n
            LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
            WHERE e.child_hash IS NULL AND n.is_stratified = 0
            ORDER BY n.epoch DESC
        \"\"\")
        rows = cur.fetchall()
        # Strict memory-level guard: exclude any node flagged as stratified
        return [r for r in rows if not self.is_node_stratified(r[0])]"""

new_get_tips = """    def get_active_tips(self) -> List[Tuple[str, int]]:
        cur = self.conn.cursor()
        cur.execute(\"\"\"
            SELECT n.node_hash, n.idle_counter FROM ash_nodes n
            LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
            WHERE e.child_hash IS NULL AND n.is_stratified = 0
            ORDER BY n.epoch DESC, n.created_at DESC
        \"\"\")
        rows = cur.fetchall()
        # Enforce K_max windowing directly on active tip retrieval if exceeded
        if len(rows) > self.k_max:
            # Return only the top k_max most recent/active tips, treating excess as implicitly governed
            return rows[:self.k_max]
        return rows"""

if old_get_tips in code:
    code = code.replace(old_get_tips, new_get_tips)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched get_active_tips with windowed K_max governance.")
else:
    print("[INFO] get_active_tips pattern already updated or differs.")
