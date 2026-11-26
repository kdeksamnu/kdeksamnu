import { describe, it, expect } from 'vitest';
import { OfflineRoomGenerator } from '../src/engine/ember/offlineRoomGenerator';

describe('OfflineRoomGenerator', () => {
  it('generates deterministic rooms given identical seeds and IDs', () => {
    const genA = new OfflineRoomGenerator(42);
    const genB = new OfflineRoomGenerator(42);

    const roomA = genA.generateRoom('chamber_alpha', 1);
    const roomB = genB.generateRoom('chamber_alpha', 1);

    expect(roomA).toEqual(roomB);
    expect(roomA.exits.length).toBeGreaterThan(0);
  });
});
