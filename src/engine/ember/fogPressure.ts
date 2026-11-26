import { EmberRuntimeState } from './emberState';
import { RoomNode } from './offlineRoomGenerator';

export class FogPressureEngine {
  public static simulateTick(state: EmberRuntimeState, currentRoom: RoomNode): void {
    const currentState = state.getState();

    // Pressure scales inversely with room stability and directly with depth
    const stabilityFactor = 1.1 - currentRoom.stability;
    const pressureDelta = stabilityFactor * 2.5 + currentRoom.depth * 0.2;
    state.updatePressure(pressureDelta);

    // Fog density increases as pressure rises or stability drops
    const targetFog = Math.min(1.0, currentState.ambientPressure / 100 + (1 - currentRoom.stability) * 0.5);
    const interpolatedFog = currentState.fogDensity + (targetFog - currentState.fogDensity) * 0.3;
    state.setFogDensity(interpolatedFog);

    // High pressure drains Ember charge
    if (currentState.ambientPressure > 70) {
      state.updateCharge(-4.0);
    } else if (currentState.ambientPressure > 40) {
      state.updateCharge(-2.0);
    } else {
      state.updateCharge(-0.5);
    }
  }
}
