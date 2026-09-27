with open("sigma12_forking_engine.py", "r") as f:
    code = f.read()

if "def get_parents" not in code:
    # Inject get_parents method into AshArchiveDAG class
    target = "    def commit_node(self, node: MerkleDAGNode):"
    replacement = """    def get_parents(self, node_hash: str) -> List[str]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT parent_hash FROM ash_dag_edges WHERE child_hash = ?", (node_hash,))
        return [row[0] for row in cursor.fetchall()]

    def commit_node(self, node: MerkleDAGNode):"""
    
    code = code.replace(target, replacement)
    with open("sigma12_forking_engine.py", "w") as f:
        f.write(code)
    print("[OK] sigma12_forking_engine.py successfully patched with get_parents.")
else:
    print("[OK] get_parents already present in AshArchiveDAG.")
