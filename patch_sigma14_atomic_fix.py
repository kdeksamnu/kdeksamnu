with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_governor = """    def enforce_horizon_governor(self):
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
            sorted_tips = sorted(active_tips, key=lambda x: x[1], reverse=True)
            tip_hash = sorted_tips[0][0]
            cur.execute("UPDATE ash_nodes SET is_stratified = 1 WHERE node_hash = ?", (tip_hash,))
            self.conn.commit()
            active_tips = self.get_active_tips()"""

new_governor = """    def enforce_horizon_governor(self):
        cur = self.conn.cursor()
        # Increment idle counters
        cur.execute(\"\"\"
            UPDATE ash_nodes SET idle_counter = idle_counter + 1
            WHERE node_hash IN (
                SELECT n.node_hash FROM ash_nodes n
                LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
                WHERE e.child_hash IS NULL AND n.is_stratified = 0
            )
        \"\"\")
        self.conn.commit()

        # Enforce K_max strictly by immediately stratifying excess unstratified tips
        while True:
            cur.execute(\"\"\"
                SELECT node_hash FROM ash_nodes n
                LEFT JOIN ash_dag_edges e ON n.node_hash = e.parent_hash
                WHERE e.child_hash IS NULL AND n.is_stratified = 0
                ORDER BY n.idle_counter DESC, n.epoch DESC
            \"\"\")
            tips = cur.fetchall()
            if len(tips) <= self.k_max:
                break
            excess_tip = tips[0][0]
            cur.execute("UPDATE ash_nodes SET is_stratified = 1 WHERE node_hash = ?", (excess_tip,))
            self.conn.commit()"""

if old_governor in code:
    code = code.replace(old_governor, new_governor)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched enforce_horizon_governor with strict cursor-level pruning loop.")
else:
    print("[INFO] Governor pattern already updated or differs.")
