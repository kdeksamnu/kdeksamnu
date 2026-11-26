import { EmberRuntimeState } from './emberState';

export type BelnapValue = 'TRUE' | 'FALSE' | 'BOTH' | 'NEITHER';

export class ContradictionIntegrationEngine {
  /**
   * Integrates new evidence using Belnap-Dunn 4-valued paraconsistent logic matrix.
   * Handles overlapping or contradictory ontological proofs without crashing.
   */
  public static integrateEvidence(
    state: EmberRuntimeState,
    axiomKey: string,
    newEvidence: 'TRUE' | 'FALSE'
  ): BelnapValue {
    const existing = state.getContradiction(axiomKey);

    let resolved: BelnapValue;

    if (!existing) {
      resolved = newEvidence;
    } else if (existing === newEvidence) {
      resolved = existing;
    } else {
      // Contradiction collision -> Both (Harmonic Scar formation)
      resolved = 'BOTH';
    }

    state.setContradiction(axiomKey, resolved);

    // If a contradiction crystallizes as BOTH, it increases ambient pressure as a side-effect
    if (resolved === 'BOTH') {
      state.updatePressure(15.0);
    }

    return resolved;
  }
}
