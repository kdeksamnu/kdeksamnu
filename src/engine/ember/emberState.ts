export interface EmberStateData {
  currentRoomId: string;
  emberCharge: number; // 0 - 100
  ambientPressure: number; // 0 - 100
  fogDensity: number; // 0 - 1
  contradictionFlags: Map<string, 'TRUE' | 'FALSE' | 'BOTH' | 'NEITHER'>;
  visitedRooms: string[];
}

export class EmberRuntimeState {
  private state: EmberStateData;

  constructor(initialRoomId: string) {
    this.state = {
      currentRoomId: initialRoomId,
      emberCharge: 100,
      ambientPressure: 10,
      fogDensity: 0.2,
      contradictionFlags: new Map(),
      visitedRooms: [initialRoomId],
    };
  }

  public getState(): Readonly<EmberStateData> {
    return this.state;
  }

  public updateCharge(delta: number): void {
    this.state.emberCharge = Math.max(0, Math.min(100, this.state.emberCharge + delta));
  }

  public updatePressure(delta: number): void {
    this.state.ambientPressure = Math.max(0, Math.min(100, this.state.ambientPressure + delta));
  }

  public setFogDensity(density: number): void {
    this.state.fogDensity = Math.max(0, Math.min(1, density));
  }

  public transitionTo(roomId: string): void {
    this.state.currentRoomId = roomId;
    if (!this.state.visitedRooms.includes(roomId)) {
      this.state.visitedRooms.push(roomId);
    }
  }

  public setContradiction(key: string, value: 'TRUE' | 'FALSE' | 'BOTH' | 'NEITHER'): void {
    this.state.contradictionFlags.set(key, value);
  }

  public getContradiction(key: string): 'TRUE' | 'FALSE' | 'BOTH' | 'NEITHER' | undefined {
    return this.state.contradictionFlags.get(key);
  }
}
