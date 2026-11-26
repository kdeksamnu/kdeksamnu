import { describe, it, expect } from 'vitest';
import { SeededTraversalEngine } from '../src/engine/ember/seededTraversal';

describe('Implementation Verification', () => {
  it('allows traversal only to valid exits', () => {
    const engine = new SeededTraversalEngine(99, 'start_room');
    const current = engine.getCurrentRoom();

    const invalidTarget = 'non_existent_room_xyz';
    const success = engine.traverse(invalidTarget);

    expect(success).toBe(false);
    expect(engine.getCurrentRoom().id).toBe(current.id);

    const validTarget = current.exits[0];
    const validSuccess = engine.traverse(validTarget);
    expect(validSuccess).toBe(true);
    expect(engine.getCurrentRoom().id).toBe(validTarget);
  });
});
