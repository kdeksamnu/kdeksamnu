from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List

class EntityType(Enum):
    PC = "PC"
    NPC = "NPC"
    RELIC = "RELIC"
    BARRIER = "BARRIER"

class SpectralConstant(Enum):
    GOLD_JOY = "Θ"
    TEAL_CURIOSITY = "Ψ"
    BLUE_SORROW = "Δ"
    CRIMSON_FLAME = "Φ"
    VIOLET_VOID = "Ω"
    EMERALD_LOVE = "E"
    NULL_ABYSS = "∅"

class BelnapValue(Enum):
    TRUE = "T"
    FALSE = "F"
    BOTH = "B"
    NEITHER = "N"

@dataclass
class EntityState:
    id: str
    name: str
    entity_type: EntityType
    vigor: int = 10
    acuity: int = 10
    poise: int = 10
    entropy: int = 10
    hp: int = 100
    strain: int = 0
    paradox: int = 0
    ego_density: float = 8.3
    resonance_spectrum: SpectralConstant = SpectralConstant.GOLD_JOY
    logic_state: BelnapValue = BelnapValue.TRUE

@dataclass
class GameState:
    entities: Dict[str, EntityState] = field(default_factory=dict)
    chamber_id: str = "GENESIS-Ω01"
    epoch: int = 0
    active_scars: List[str] = field(default_factory=list)

    def transition(self, action_payload: dict) -> "GameState":
        next_epoch = self.epoch + 1
        print(f"[*] Compiling state transition for epoch {next_epoch}...")
        return GameState(
            entities=self.entities.copy(),
            chamber_id=self.chamber_id,
            epoch=next_epoch,
            active_scars=self.active_scars.copy()
        )

if __name__ == "__main__":
    state = GameState()
    entity = EntityState(id="pc-01", name="Riot Dre'atha", entity_type=EntityType.PC)
    state.entities[entity.id] = entity
    next_state = state.transition({"action": "initialize"})
    print(f"[+] GameState successfully initialized at epoch: {next_state.epoch} in chamber: {next_state.chamber_id}")
