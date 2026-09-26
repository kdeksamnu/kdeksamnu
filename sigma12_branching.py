import hashlib

def keystone_hash(data, parent_hash="0"*64):
    """Generates a cryptographic hash incorporating parent lineage."""
    payload = f"{parent_hash}:{data}"
    return hashlib.sha256(payload.encode('utf-8')).hexdigest()

# 1. Establish Genesis Root R_0
r0 = keystone_hash("Genesis_State")

# 2. Fork into divergent branches R_1 and R_2 (Representation of concurrent historical states)
r1 = keystone_hash("Branch_Alpha_Observation", parent_hash=r0)
r2 = keystone_hash("Branch_Beta_Observation", parent_hash=r0)

# 3. Form Confluent State R_3 referencing both parents (Multi-parent DAG merge)
confluent_payload = f"{r1}:{r2}:Confluent_Reconciliation"
r3 = hashlib.sha256(confluent_payload.encode('utf-8')).hexdigest()

print("--- Chamber Σ-12 Forking Memory & Confluence ---")
print(f"Genesis R0: {r0[:12]}...")
print(f"Branch R1:  {r1[:12]}...")
print(f"Branch R2:  {r2[:12]}...")
print(f"Confluent R3 (Parents: R1, R2): {r3[:12]}...")
