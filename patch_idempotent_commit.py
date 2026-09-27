with open("sigma12_forking_engine.py", "r") as f:
    code = f.read()

# Make commit_node idempotent to handle pre-existing nodes gracefully
old_insert = """        cursor.execute(
            \"\"\"
            INSERT INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json)
            VALUES (?, ?, ?, ?, ?)
            \"\"\",
            (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
        )"""

new_insert = """        cursor.execute(
            \"\"\"
            INSERT OR IGNORE INTO ash_nodes (node_hash, branch_name, epoch, merkle_root, payload_json)
            VALUES (?, ?, ?, ?, ?)
            \"\"\",
            (node.node_hash, node.branch_name, node.epoch, node.merkle_root, node.canonical_payload)
        )"""

old_edge = """            cursor.execute(
                \"\"\"
                INSERT INTO ash_dag_edges (parent_hash, child_hash, edge_type)
                VALUES (?, ?, ?)
                \"\"\",
                (p_hash, node.node_hash, "lineage")
            )"""

new_edge = """            cursor.execute(
                \"\"\"
                INSERT OR IGNORE INTO ash_dag_edges (parent_hash, child_hash, edge_type)
                VALUES (?, ?, ?)
                \"\"\",
                (p_hash, node.node_hash, "lineage")
            )"""

old_tx = """            cursor.execute(
                \"\"\"
                INSERT INTO ash_transactions (tx_hash, node_hash, leaf_index, payload_json)
                VALUES (?, ?, ?, ?)
                \"\"\",
                (tx_hash, node.node_hash, idx, ctx)
            )"""

new_tx = """            cursor.execute(
                \"\"\"
                INSERT OR IGNORE INTO ash_transactions (tx_hash, node_hash, leaf_index, payload_json)
                VALUES (?, ?, ?, ?)
                \"\"\",
                (tx_hash, node.node_hash, idx, ctx)
            )"""

if old_insert in code:
    code = code.replace(old_insert, new_insert)
    code = code.replace(old_edge, new_edge)
    code = code.replace(old_tx, new_tx)
    with open("sigma12_forking_engine.py", "w") as f:
        f.write(code)
    print("[OK] sigma12_forking_engine.py patched for idempotent commits.")
else:
    print("[INFO] Insertion pattern already updated or differs.")
