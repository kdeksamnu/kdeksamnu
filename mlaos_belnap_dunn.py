import json
from enum import Enum
from typing import Dict, Any, Tuple

class FourValuedLogic(Enum):
    NONE = "NEITHER"  # N: (0, 0) - Absence of evidence
    FALSE = "FALSE"    # F: (0, 1) - Monotonic falsehood
    TRUE = "TRUE"      # T: (1, 0) - Monotonic truth
    BOTH = "BOTH"      # B: (1, 1) - Load-bearing dialetheic paradox

class BelnapDunnEvaluator:
    """
    Belnap-Dunn 4-Valued Paraconsistent Logic Evaluator for Chamber Sigma-12.
    Evaluates sensor telemetry against KRP thresholds to compute state vectors
    without triggering classical contradiction faults.
    """
    def __init__(self, upper_threshold: float = 0.850, lower_threshold: float = 0.300):
        self.upper_threshold = upper_threshold
        self.lower_threshold = lower_threshold

    def evaluate_telemetry(self, sensor_val_a: float, sensor_val_b: float) -> Tuple[FourValuedLogic, Dict[str, Any]]:
        """
        Maps two conflicting or complementary telemetry streams to Belnap-Dunn values.
        """
        evidence_true = sensor_val_a >= self.upper_threshold or sensor_val_b >= self.upper_threshold
        evidence_false = sensor_val_a <= self.lower_threshold or sensor_val_b <= self.lower_threshold

        if evidence_true and evidence_false:
            logical_state = FourValuedLogic.BOTH
        elif evidence_true:
            logical_state = FourValuedLogic.TRUE
        elif evidence_false:
            logical_state = FourValuedLogic.FALSE
        else:
            logical_state = FourValuedLogic.NONE

        telemetry_metadata = {
            "sensor_a": sensor_val_a,
            "sensor_b": sensor_val_b,
            "upper_threshold": self.upper_threshold,
            "lower_threshold": self.lower_threshold,
            "logical_state": logical_state.value,
            "requires_thermal_sink": logical_state == FourValuedLogic.BOTH
        }

        return logical_state, telemetry_metadata

if __name__ == "__main__":
    evaluator = BelnapDunnEvaluator(upper_threshold=0.850, lower_threshold=0.300)

    # Simulation cases across Cathedral branches
    scenarios = [
        ("Nominal Ingress", 0.910, 0.450),
        ("Contradictory Telemetry (Epoch 2 Collision)", 0.942, 0.210),
        ("Void / Sensor Loss", 0.420, 0.510),
        ("Explicit Rejection", 0.180, 0.220)
    ]

    print("=================================================================")
    print("      CHAMBER Σ-12 // BELNAP-DUNN PARACONSISTENT EVALUATION      ")
    print("=================================================================")
    for label, val_a, val_b in scenarios:
        state, meta = evaluator.evaluate_telemetry(val_a, val_b)
        print(f"Scenario : {label}")
        print(f"Inputs   : Sensor A = {val_a} | Sensor B = {val_b}")
        print(f"State    : {state.value} (Thermal Sink Required: {meta['requires_thermal_sink']})")
        print("-" * 65)
