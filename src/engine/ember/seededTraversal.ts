import { OfflineRoomGenerator, RoomNode } from './offlineRoomGenerator';
import { EmberRuntimeState } from './emberState';
import { FogPressureEngine } from './fogPressure';

export class SeededTraversalEngine {
  private generator: OfflineRoomGenerator;
  private state: EmberRuntimeState;
  private roomCache: Map<string, RoomNode> = new Map();

  constructor(baseSeed: number, startRoomId: string = 'room_0_0') {
    this.generator = new OfflineRoomGenerator(baseSeed);
    this.state = new EmberRuntimeState(startRoomId);
    
    // Cache starting room
    const startRoom = this.generator.generateRoom(startRoomId, 0);
    this.roomCache.set(startRoomId, startRoom);
  }

  public getCurrentRoom(): RoomNode {
    const currentId = this.state.getState().currentRoomId;
    let room = this.roomCache.get(currentId);
    if (!room) {
      // Derive depth from ID prefix convention room_depth_index
      const parts = currentId.split('_');
      const depth = parseInt(parts[1], 10) || 0;
      room = this.generator.generateRoom(currentId, depth);
      this.roomCache.set(currentId, room);
    }
    return room;
  }

  public traverse(targetRoomId: string): boolean {
    const currentRoom = this.getCurrentRoom();
    if (!currentRoom.exits.includes(targetRoomId)) {
      return false; // Invalid traversal path
    }

    // Generate or fetch target room
    const parts = targetRoomId.split('_');
    const depth = parseInt(parts[1], 10) || (currentRoom.depth + 1);
    let targetRoom = this.roomCache.get(targetRoomId);
    if (!targetRoom) {
      targetRoom = this.generator.generateRoom(targetRoomId, depth);
      this.roomCache.set(targetRoomId, targetRoom);
    }

    // Execute state transition
    this.state.transitionTo(targetRoomId);
    FogPressureEngine.simulateTick(this.state, targetRoom);

    return true;
  }

  public getStateInstance(): EmberRuntimeState {
    return this.state;
  }
}
