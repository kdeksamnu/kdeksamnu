import hashlib

def keystone_hash(data):
    """Standard SHA-256 hash for a Truth-State leaf."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def merge_nodes(left_hash, right_hash):
    """Concatenate and hash two sibling nodes."""
    return hashlib.sha256((left_hash + right_hash).encode('utf-8')).hexdigest()

# 1. Define our Ash Archive Truth-States (Leaves)
states = ['State_Alpha', 'State_Beta', 'State_Gamma', 'State_Delta']
leaves = [keystone_hash(s) for s in states]

# 2. Construct the Merkle Tree (Level 1)
node_01 = merge_nodes(leaves[0], leaves[1])
node_23 = merge_nodes(leaves[2], leaves[3])

# 3. Magisterial Kernel Root Hash
root_hash = merge_nodes(node_01, node_23)

# 4. Generate a legitimate proof for 'State_Beta' (leaves[1])
valid_proof = [
    (leaves[0], 'left'),
    (node_23, 'right')
]

# 5. Generate a malformed proof (tampered sibling hash representing a divergent history)
tampered_hash = keystone_hash("Corrupted_State")
malformed_proof = [
    (tampered_hash, 'left'),
    (node_23, 'right')
]

def verify_inclusion(target_hash, proof_path, expected_root):
    """Verifies the Merkle inclusion proof."""
    current_hash = target_hash
    for sibling, direction in proof_path:
        if direction == 'left':
            current_hash = merge_nodes(sibling, current_hash)
        else:
            current_hash = merge_nodes(current_hash, sibling)
    return current_hash == expected_root

# 6. Execute Diagnostics
print(f"--- Chamber Σ-11 Diagnostics ---")
print(f"Root Hash: {root_hash[:12]}...")

print(f"\n[Test 1] Validating State_Beta Inclusion...")
result_valid = verify_inclusion(leaves[1], valid_proof, root_hash)
print(f"Result: {'SUCCESS - PROOF ACCEPTED' if result_valid else 'FAILED'}")

print(f"\n[Test 2] Testing Malformed Proof Rejection...")
result_invalid = verify_inclusion(leaves[1], malformed_proof, root_hash)
print(f"Result: {'SUCCESS - PROOF REJECTED' if not result_invalid else 'FALSE POSITIVE'}")
