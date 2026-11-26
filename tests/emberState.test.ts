import { describe, it, expect } from 'vitest';
import { EmberRuntimeState } from '../src/engine/ember/emberState';

describe('EmberRuntimeState', () => {
  it('initializes with default values and tracking', () => {
    const state = new EmberRuntimeState('room_0_0');
    const data = state.getState();
    expect(data.currentRoomId).toBe('room_0_0');
    expect(data.emberCharge).toBe(100);
    expect(data.ambientPressure).toBe(10);
    expect(data.visitedRooms).toContain('room_0_0');
  });

  it('clamps charges and pressures within bounds', () => {
    const state = new EmberRuntimeState('room_0_0');
    state.updateCharge(50);
    expect(state.getState().emberCharge).toBe(100);

    state.updateCharge(-200);
    expect(state.getState().emberCharge).toBe(0);

    state.updatePressure(200);
    expect(state.getState().ambientPressure).toBe(100);
  });
});
