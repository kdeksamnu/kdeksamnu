import { describe, it, expect } from 'vitest';
import { OfflineRoomGenerator } from '../src/engine/ember/offlineRoomGenerator';

describe('Ledger Adjacency', () => {
  it('maintains consistent depth propagation across exits', () => {
    const generator = new OfflineRoomGenerator(777);
    const room = generator.generateRoom('room_0_0', 0);

    room.exits.forEach((exitId) => {
      expect(exitId).toContain('room_1_');
    });
  });
});
