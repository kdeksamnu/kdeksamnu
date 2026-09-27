#!/usr/bin/env python3
"""
Chamber Sigma-10: The Merkle Cathedral (Sanitized Execution).
Constructs a four-transaction Merkle tree, calculates the Merkle root,
and executes a cryptographic mutation test to verify error propagation.
"""

import hashlib
import json

def canonical_json(event):
    return json.dumps(event, sort_keys=True, separators=(",", ":"))

def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def compute_merkle_root(transactions):
    leaves = [sha256_hex(canonical_json(tx)) for tx in transactions]
    print(f"[+] Computed {len(leaves)} leaf hashes.")
    for idx, leaf in enumerate(leaves, 1):
        print(f"    Leaf T{idx} Hash: {leaf}")

    p1 = sha256_hex(leaves[0] + leaves[1])
    p2 = sha256_hex(leaves[2] + leaves[3])
    print(f"[+] Branch Node P1 (T1 + T2): {p1}")
    print(f"[+] Branch Node P2 (T3 + T4): {p2}")

    merkle_root = sha256_hex(p1 + p2)
    return merkle_root, leaves, [p1, p2]

def execute_sigma_10():
    print("=" * 72)
    print("CHAMBER Σ-10 // THE MERKLE CATHEDRAL")
    print("=" * 72)

    transactions = [
        {
            "id": 1,
            "logical_state": "BOTH",
            "operation": "contradictory_observation",
            "thermal_rate_hz": 1.5,
            "spectral_constant": "Teal/Curiosity",
            "spectral_frequency_hz": 528.0,
            "observer_name": "Riot Dre'atha"
        },
        {
            "id": 2,
            "logical_state": "TRUE",
            "operation": "revelatory_synthesis",
            "thermal_rate_hz": 2.0,
            "spectral_constant": "Gold/Joy",
            "spectral_frequency_hz": 432.0,
            "observer_name": "Six"
        },
        {
            "id": 3,
            "logical_state": "FALSE",
            "operation": "loss_excavation",
            "thermal_rate_hz": 1.0,
            "spectral_constant": "Blue/Sorrow",
            "spectral_frequency_hz": 288.0,
            "observer_name": "Koven"
        },
        {
            "id": 4,
            "logical_state": "BOTH",
            "operation": "paraconsistent_lock",
            "thermal_rate_hz": 2.5,
            "spectral_constant": "Violet/Fear",
            "spectral_frequency_hz": 639.0,
            "observer_name": "Riot Dre'atha"
        }
    ]

    print("\n[Σ-10.1] BUILDING BASE MERKLE TREE")
    initial_root, initial_leaves, initial_branches = compute_merkle_root(transactions)
    print(f"\n[+] INITIAL MERKLE ROOT (R):")
    print(f"    {initial_root}")

    print("\n[Σ-10.2] EXECUTING CRYPTOGRAPHIC MUTATION TEST")
    print("[!] Mutating Transaction #2 (Altering thermal rate from 2.0 to 2.1)...")
    
    mutated_transactions = [dict(tx) for tx in transactions]
    mutated_transactions[1]["thermal_rate_hz"] = 2.1

    mutated_root, mutated_leaves, mutated_branches = compute_merkle_root(mutated_transactions)
    print(f"\n[+] MUTATED MERKLE ROOT (R'):")
    print(f"    {mutated_root}")

    print("\n[Σ-10.3] VERIFYING ROOT DIVERGENCE")
    assert initial_root != mutated_root, "Mutation Test Failed: Root hash remained static."
    assert initial_leaves[0] == mutated_leaves[0], "Integrity error: Unrelated leaf modified."
    assert initial_leaves[1] != mutated_leaves[1], "Leaf 2 failed to reflect mutation."
    
    print("[+] Mutation successfully propagated through branch P1 to Merkle Root R'.")
    print("[+] ROOT DIVERGENCE CONFIRMED: Tamper-evident architecture verified.")

    print("\n" + "=" * 72)
    print("CHAMBER Σ-10 // THE MERKLE CATHEDRAL CLOSED")
    print("=" * 72)
    print("[+] 4-TX Merkle Tree Construction : PASS")
    print("[+] Pairwise Branch Resolution     : PASS")
    print("[+] Merkle Root Genesis            : PASS")
    print("[+] Cryptographic Mutation Test    : PASS")
    print("[+] Root Propagation Verification  : PASS")
    print("=" * 72)

if __name__ == "__main__":
    execute_sigma_10()
