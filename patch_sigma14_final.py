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
        return cur.fetchall()"""

new_get_tips = """    def get_active_tips(self) -> List[Tuple[str, int]]:
        cur = self.conn.cursor()
        cur.execute(\"\"\"
            SELECT n.node_hash, n.idle_counter FROM ash_nodes n
            LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
            WHERE e.child_hash IS NULL AND n.is_stratified = 0
            ORDER BY n.epoch DESC
        \"\"\")
        rows = cur.fetchall()
        # Strict memory-level guard: exclude any node flagged as stratified
        return [r for r in rows if not self.is_node_stratified(r[0])]

    def is_node_stratified(self, node_hash: str) -> bool:
        cur = self.conn.cursor()
        cur.execute("SELECT is_stratified FROM ash_nodes WHERE node_hash = ?", (node_hash,))
        row = cur.fetchone()
        return row[0] == 1 if row else False"""

if old_get_tips in code:
    code = code.replace(old_get_tips, new_get_tips)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched get_active_tips with strict stratification filter.")
else:
    print("[INFO] get_active_tips pattern already updated or differs.")
