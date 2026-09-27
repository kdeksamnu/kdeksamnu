#!/usr/bin/env python3
"""
Chamber Sigma-11: The Observer's Proof.
Constructs a Merkle inclusion proof for a target transaction,
verifies positive inclusion against a trusted root, and executes
a negative rejection test using a mutated leaf.
"""

import hashlib
import json

def canonical_json(event):
    return json.dumps(event, sort_keys=True, separators=(",", ":"))

def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()

def execute_sigma_11():
    print("=" * 72)
    print("CHAMBER Σ-11 // THE OBSERVER'S PROOF")
    print("=" * 72)

    transactions = [
        {"id": 1, "logical_state": "BOTH", "operation": "contradictory_observation", "thermal_rate_hz": 1.5, "spectral_constant": "Teal/Curiosity", "spectral_frequency_hz": 528.0, "observer_name": "Riot Dre'atha"},
        {"id": 2, "logical_state": "TRUE", "operation": "revelatory_synthesis", "thermal_rate_hz": 2.0, "spectral_constant": "Gold/Joy", "spectral_frequency_hz": 432.0, "observer_name": "Six"},
        {"id": 3, "logical_state": "FALSE", "operation": "loss_excavation", "thermal_rate_hz": 1.0, "spectral_constant": "Blue/Sorrow", "spectral_frequency_hz": 288.0, "observer_name": "Koven"},
        {"id": 4, "logical_state": "BOTH", "operation": "paraconsistent_lock", "thermal_rate_hz": 2.5, "spectral_constant": "Violet/Fear", "spectral_frequency_hz": 639.0, "observer_name": "Riot Dre'atha"}
    ]

    leaves = [sha256_hex(canonical_json(tx)) for tx in transactions]
    p1 = sha256_hex(leaves[0] + leaves[1])
    p2 = sha256_hex(leaves[2] + leaves[3])
    trusted_root = sha256_hex(p1 + p2)
    
    print(f"\n[+] Trusted Merkle Root (R): {trusted_root}")

    target_tx = transactions[1]
    target_leaf = leaves[1]
    sibling_leaf = leaves[0]
    cross_branch_p2 = p2

    print(f"\n[Σ-11.1] ASSEMBLING INCLUSION PROOF FOR TRANSACTION #2")
    print(f"    Target Leaf H(T2)    : {target_leaf}")
    print(f"    Sibling Leaf H(T1)   : {sibling_leaf}")
    print(f"    Cross-Branch Sibling : {cross_branch_p2}")

    print("\n[Σ-11.2] EXECUTING POSITIVE INCLUSION VERIFICATION")
    recomputed_p1 = sha256_hex(sibling_leaf + target_leaf)
    reconstructed_root = sha256_hex(recomputed_p1 + cross_branch_p2)
    
    print(f"    Reconstructed Root   : {reconstructed_root}")
    
    assert reconstructed_root == trusted_root, "Positive Inclusion Failed: Reconstructed root does not match trusted root."
    print("[+] POSITIVE PROOF ACCEPTED: Transaction T2 verified as member of root R.")

    print("\n[Σ-11.3] EXECUTING NEGATIVE REJECTION TEST")
    mutated_tx = dict(target_tx)
    mutated_tx["thermal_rate_hz"] = 2.1
    mutated_leaf = sha256_hex(canonical_json(mutated_tx))
    
    print(f"    Mutated Leaf H(T2')  : {mutated_leaf}")

    recomputed_p1_mutated = sha256_hex(sibling_leaf + mutated_leaf)
    reconstructed_root_mutated = sha256_hex(recomputed_p1_mutated + cross_branch_p2)
    
    print(f"    Mutated Path Root    : {reconstructed_root_mutated}")

    assert reconstructed_root_mutated != trusted_root, "Negative Test Failed: Tampered proof incorrectly validated."
    print("[+] NEGATIVE PROOF REJECTED: Tampered transaction hash failed root validation.")

    print("\n" + "=" * 72)
    print("CHAMBER Σ-11 // THE OBSERVER'S PROOF CLOSED")
    print("=" * 72)
    print("[+] Inclusion Proof Construction : PASS")
    print("[+] Positive Root Reconstruction : PASS")
    print("[+] Negative Proof Rejection     : PASS")
    print("[+] Verifiable Memory Verified   : PASS")
    print("=" * 72)

if __name__ == "__main__":
    execute_sigma_11()
