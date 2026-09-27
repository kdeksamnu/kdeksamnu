from engine.combat.combat import CombatResolver, BelnapValue, ActionType

print("[*] Initializing Phase 03 Combat Core Verification Suite...")

# Test 1: Standard True State Target
res_t = CombatResolver.resolve_attack(
    d20_roll=12, attr_mod=4, resonance_bonus=2, strain_penalty=0,
    target_ac=15, target_logic=BelnapValue.TRUE, action_type=ActionType.STANDARD
)
assert res_t.hit == True, "Test 1 Failed: True target resolution error."
print(f"[+] Test 1 (Standard T): Passed | {res_t.message}")

# Test 2: Dialetheic Superposition Target (B)
res_b = CombatResolver.resolve_attack(
    d20_roll=10, attr_mod=3, resonance_bonus=1, strain_penalty=0,
    target_ac=14, target_logic=BelnapValue.BOTH, action_type=ActionType.STANDARD, base_damage=10
)
assert res_b.hit == True and res_b.recoil_strain == 5, "Test 2 Failed: Dialetheic recoil error."
print(f"[+] Test 2 (Dialetheic B): Passed | {res_b.message} | Recoil: {res_b.recoil_strain}")

print("[+] Phase 03 Combat Core verification suite completed successfully.")
