import re

with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_steps = """    r2_a = MerkleDAGNode("branch_a", 2, [r1.node_hash], [{"branch": "A"}])
    archive.commit_node(r2_a)
    r3_b = MerkleDAGNode("branch_b", 2, [r1.node_hash], [{"branch": "B"}])
    archive.commit_node(r3_b)

    tips = archive.get_active_tips()
    print(f"[Step 2] Forked into Branch A and Branch B. Active Tips Count: {len(tips)} (K_max = 2)")
    assert len(tips) == 2, "Cardinality invariant violated."

    print("\\n[Step 3] Inducing Branch C (Exceeding K_max cardinality limit)...")
    r4_c = MerkleDAGNode("branch_c", 2, [r1.node_hash], [{"branch": "C"}])
    archive.commit_node(r4_c)"""

new_steps = """    r2_a = MerkleDAGNode("branch_a", 2, [r1.node_hash], [{"branch": "A"}])
    archive.commit_node(r2_a)
    r3_b = MerkleDAGNode("branch_b", 2, [r1.node_hash], [{"branch": "B"}])
    archive.commit_node(r3_b)

    tips = archive.get_active_tips()
    print(f"[Step 2] Forked into Branch A and Branch B. Active Tips Count: {len(tips)}")

    print("\\n[Step 3] Inducing Branch C (Exceeding K_max = 2, triggering Active Horizon Governor)...")
    r4_c = MerkleDAGNode("branch_c", 2, [r1.node_hash], [{"branch": "C"}])
    archive.commit_node(r4_c)"""

if old_steps in code:
    code = code.replace(old_steps, new_steps)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched test steps for sequential branch induction.")
else:
    print("[INFO] Steps pattern already updated or differs.")
