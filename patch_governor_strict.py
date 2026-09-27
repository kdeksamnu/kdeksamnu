with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_func = """    def enforce_horizon_governor(self):
        cur = self.conn.cursor()
        cur.execute(\"\"\"
            UPDATE ash_nodes SET idle_counter = idle_counter + 1
            WHERE node_hash IN (
                SELECT n.node_hash FROM ash_nodes n
                LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
                WHERE e.child_hash IS NULL AND n.is_stratified = 0
            )
        \"\"\")
        self.conn.commit()

        active_tips = self.get_active_tips()
        if len(active_tips) > self.k_max:
            sorted_tips = sorted(active_tips, key=lambda x: x[1], reverse=True)
            excess_tips = sorted_tips[:len(active_tips) - self.k_max]
            
            for tip_hash, _ in excess_tips:
                cur.execute("UPDATE ash_nodes SET is_stratified = 1 WHERE node_hash = ?", (tip_hash,))
            self.conn.commit()"""

new_func = """    def enforce_horizon_governor(self):
        cur = self.conn.cursor()
        cur.execute(\"\"\"
            UPDATE ash_nodes SET idle_counter = idle_counter + 1
            WHERE node_hash IN (
                SELECT n.node_hash FROM ash_nodes n
                LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
                WHERE e.child_hash IS NULL AND n.is_stratified = 0
            )
        \"\"\")
        self.conn.commit()

        active_tips = self.get_active_tips()
        while len(active_tips) > self.k_max:
            # Sort by idle counter descending, stratify the oldest/idlest
            sorted_tips = sorted(active_tips, key=lambda x: x[1], reverse=True)
            tip_hash = sorted_tips[0][0]
            cur.execute("UPDATE ash_nodes SET is_stratified = 1 WHERE node_hash = ?", (tip_hash,))
            self.conn.commit()
            active_tips = self.get_active_tips()"""

if old_func in code:
    code = code.replace(old_func, new_func)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched enforce_horizon_governor with strict while-loop bounding.")
else:
    print("[INFO] Governor pattern already updated or differs.")
