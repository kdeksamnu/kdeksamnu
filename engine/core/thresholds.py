from dataclasses import dataclass

@dataclass
class VesselState:
    strain: int = 0
    paradox: int = 0
    hp: int = 100

class ThresholdMonitor:
    @staticmethod
    def evaluate_transition(state: VesselState) -> str:
        messages = []
        
        # Strain Escalation Rules
        if state.strain >= 5:
            state.strain = 2
            state.paradox += 1
            messages.append("[!] SOMATIC BURNOUT: Strain reached 5. Dropped to 2, permanent Paradox increment applied.")
        elif state.strain >= 3:
            messages.append("[!] MICRO-FRACTURE ACTIVE: Strain >= 3. -2 penalty applied to physical attribute checks.")
            
        # Paradox Escalation Rules
        if state.paradox >= 5:
            messages.append("[!] CRITICAL REALITY RUPTURE: Paradox reached 5/5. Handing execution authority directly to CascadeMgr.")
        elif state.paradox >= 3:
            messages.append("[!] HARMONIC DISTORTION: Paradox >= 3. Entity radiates an unstable A-field; nearby entities must roll poise saves.")
            
        if not messages:
            messages.append("[+] Vessel state nominal within acceptable thresholds.")
            
        return "\n".join(messages)

if __name__ == "__main__":
    vessel = VesselState(strain=3, paradox=3)
    print(f"[*] Initial State -> Strain: {vessel.strain}, Paradox: {vessel.paradox}")
    print(ThresholdMonitor.evaluate_transition(vessel))
