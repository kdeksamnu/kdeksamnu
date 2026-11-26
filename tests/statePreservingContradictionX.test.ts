import { describe, it, expect } from 'vitest';
import { EmberRuntimeState } from '../src/engine/ember/emberState';
import { ContradictionIntegrationEngine } from '../src/engine/ember/contradictionIntegration';

describe('State Preserving Contradiction X', () => {
  it('preserves idempotent evidence states without pressure spike', () => {
    const state = new EmberRuntimeState('room_0_0');
    
    ContradictionIntegrationEngine.integrateEvidence(state, 'axiom_sigma', 'TRUE');
    const initialPressure = state.getState().ambientPressure;

    const repeatRes = ContradictionIntegrationEngine.integrateEvidence(state, 'axiom_sigma', 'TRUE');
    expect(repeatRes).toBe('TRUE');
    expect(state.getState().ambientPressure).toBe(initialPressure);
  });
});
