import { describe, it, expect } from 'vitest';
import { EmberRuntimeState } from '../src/engine/ember/emberState';
import { ContradictionIntegrationEngine } from '../src/engine/ember/contradictionIntegration';

describe('State Preserving Contradiction', () => {
  it('resolves conflicting evidence into BOTH (Harmonic Scar)', () => {
    const state = new EmberRuntimeState('room_0_0');
    
    const firstRes = ContradictionIntegrationEngine.integrateEvidence(state, 'axiom_omega', 'TRUE');
    expect(firstRes).toBe('TRUE');

    const secondRes = ContradictionIntegrationEngine.integrateEvidence(state, 'axiom_omega', 'FALSE');
    expect(secondRes).toBe('BOTH');
    expect(state.getState().ambientPressure).toBeGreaterThan(10);
  });
});
