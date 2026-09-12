import numpy as np
from typing import Dict, List

def calculate_psi(expected: List[float], actual: List[float], bins: int = 10) -> float:
    """Calculates Population Stability Index (PSI) to measure training/serving skew per Rule #37."""
    exp_counts, bin_edges = np.histogram(expected, bins=bins)
    act_counts, _ = np.histogram(actual, bins=bin_edges)

    exp_per = exp_counts / max(sum(exp_counts), 1)
    act_per = act_counts / max(sum(act_counts), 1)

    # Avoid division by zero
    exp_per = np.where(exp_per == 0, 0.0001, exp_per)
    act_per = np.where(act_per == 0, 0.0001, act_per)

    psi_value = np.sum((act_per - exp_per) * np.log(act_per / exp_per))
    return float(psi_value)
