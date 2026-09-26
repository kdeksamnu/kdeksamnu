
import math
from typing import Optional
from engine.schemas.spectral import LogicState, SpectralConstant

# Symmetric Dissonance Matrix D[i, j]
DISSONANCE_MATRIX: dict[tuple[SpectralConstant, SpectralConstant], float] = {
    # Direct polar antipodes (Maximum Dialetheic Tension)
    (SpectralConstant.GOLD_JOY, SpectralConstant.BLUE_SORROW): 0.95,
    (SpectralConstant.EMERALD_LOVE, SpectralConstant.RED_ANGER): 0.90,
    (SpectralConstant.TEAL_CURIOSITY, SpectralConstant.VIOLET_FEAR): 0.85,
    
    # Secondary tensions
    (SpectralConstant.GOLD_JOY, SpectralConstant.RED_ANGER): 0.60,
    (SpectralConstant.BLUE_SORROW, SpectralConstant.VIOLET_FEAR): 0.40,
    (SpectralConstant.TEAL_CURIOSITY, SpectralConstant.EMERALD_LOVE): 0.20,
}

class SpectralResolver:
    @classmethod
    def get_base_dissonance(cls, c1: SpectralConstant, c2: SpectralConstant) -> float:
        if c1 == c2:
            return 0.0
        return DISSONANCE_MATRIX.get((c1, c2)) or DISSONANCE_MATRIX.get((c2, c1)) or 0.50

    @classmethod
    def resolve_interaction(
        cls, 
        primary: SpectralConstant, 
        secondary: Optional[SpectralConstant], 
        phase: float
    ) -> LogicState:
        if secondary is None:
            return LogicState.TRUE

        if primary == SpectralConstant.BRONZE_OBSIDIAN_NULL or secondary == SpectralConstant.BRONZE_OBSIDIAN_NULL:
            return LogicState.NEITHER

        base_d = cls.get_base_dissonance(primary, secondary)
        
        # Modulate by phase interference
        interference = base_d * abs(math.cos(phase / 2.0))

        if interference >= 0.75:
            return LogicState.BOTH
        elif interference >= 0.25:
            return LogicState.FALSE
        else:
            return LogicState.TRUE
