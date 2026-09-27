import random
from dataclasses import dataclass
from enum import Enum

class BelnapValue(Enum):
    TRUE = "T"
    FALSE = "F"
    BOTH = "B"
    NEITHER = "N"

class ActionType(Enum):
    STANDARD = "StandardAction"
    REACTION = "Reaction"
    STRAIN_SURGE = "StrainSurge"

@dataclass
class CombatResult:
    roll: int
    total_result: int
    hit: bool
    recoil_strain: int
    message: str

class CombatResolver:
    @staticmethod
    def resolve_attack(
        d20_roll: int,
        attr_mod: int,
        resonance_bonus: int,
        strain_penalty: int,
        target_ac: int,
        target_logic: BelnapValue,
        target_ego_density: float = 8.3,
        action_type: ActionType = ActionType.STANDARD,
        base_damage: int = 10
    ) -> CombatResult:
        
        # Action Type Modifier
        modifier_bonus = 0
        if action_type == ActionType.STRAIN_SURGE:
            surge_roll = random.randint(1, 6)
            modifier_bonus += surge_roll
            print(f"[+] StrainSurge engaged: +{surge_roll} d6 modifier applied.")

        total_result = d20_roll + attr_mod + resonance_bonus - strain_penalty + modifier_bonus
        
        # Logic State Modulation
        if target_logic == BelnapValue.FALSE:
            return CombatResult(
                roll=d20_roll,
                total_result=total_result,
                hit=False,
                recoil_strain=0,
                message="Target is intangible / phase-shifted (F). Requires spiritual/spectral bypass."
            )
        
        elif target_logic == BelnapValue.NEITHER:
            dc = 10 + target_ego_density
            if total_result < dc:
                return CombatResult(
                    roll=d20_roll,
                    total_result=total_result,
                    hit=False,
                    recoil_strain=0,
                    message=f"Target is unanchored (N). Check {total_result} failed DC {dc}. Result: complete null-void dissipation."
                )
            else:
                hit = total_result >= target_ac
                return CombatResult(
                    roll=d20_roll,
                    total_result=total_result,
                    hit=hit,
                    recoil_strain=0,
                    message=f"Target unanchored (N) anchored successfully. Hit: {hit}"
                )
                
        elif target_logic == BelnapValue.BOTH:
            recoil = base_damage // 2
            return CombatResult(
                roll=d20_roll,
                total_result=total_result,
                hit=True,
                recoil_strain=recoil,
                message=f"Dialetheic superposition (B). Hit and miss resolve simultaneously. Attacker deals damage and absorbs recoil strain: {recoil}."
            )
            
        else: # True (T)
            hit = total_result >= target_ac
            return CombatResult(
                roll=d20_roll,
                total_result=total_result,
                hit=hit,
                recoil_strain=0,
                message=f"Standard target resolution (T). Hit: {hit} (Check {total_result} vs AC {target_ac})"
            )

if __name__ == "__main__":
    print("[*] Testing CombatResolver with Dialetheic Target (B)..." )
    res = CombatResolver.resolve_attack(
        d20_roll=14,
        attr_mod=4,
        resonance_bonus=2,
        strain_penalty=1,
        target_ac=15,
        target_logic=BelnapValue.BOTH,
        action_type=ActionType.STANDARD,
        base_damage=12
    )
    print(f"[+] Result: {res.message}")
    print(f"[+] Total: {res.total_result} | Hit: {res.hit} | Recoil Strain: {res.recoil_strain}")
