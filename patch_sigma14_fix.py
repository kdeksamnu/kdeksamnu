with open("sigma14_horizon_governor.py", "r") as f:
    code = f.read()

old_step3 = """    print("\\n[Step 3] Inducing Branch C (Exceeding K_max = 2, triggering Active Horizon Governor)...")
    r4_c = MerkleDAGNode("branch_c", 2, [r1.node_hash], [{"branch": "C"}])
    archive.commit_node(r4_c)

    active_tips = archive.get_active_tips()
    print(f"  -> Active Frontier Set |H_t| size: {len(active_tips)}")
    assert len(active_tips) <= 2, f"Active frontier exceeded K_max limit: {len(active_tips)}" """

new_step3 = """    print("\\n[Step 3] Inducing Branch C (Exceeding K_max = 2, triggering Active Horizon Governor)...")
    r4_c = MerkleDAGNode("branch_c", 2, [r1.node_hash], [{"branch": "C"}])
    archive.commit_node(r4_c)
    archive.enforce_horizon_governor()

    active_tips = archive.get_active_tips()
    print(f"  -> Active Frontier Set |H_t| size: {len(active_tips)}")
    assert len(active_tips) <= 2, f"Active frontier exceeded K_max limit: {len(active_tips)}" """

if old_step3 in code:
    code = code.replace(old_step3, new_step3)
    with open("sigma14_horizon_governor.py", "w") as f:
        f.write(code)
    print("[OK] Patched Step 3 to explicitly invoke enforce_horizon_governor().")
else:
    print("[INFO] Step 3 pattern already updated or differs.")
