import { describe, it, expect } from 'vitest';
import { EmberVisualRuntime } from '../src/engine/ember';

describe('EmberVisualRuntime', () => {
  it('boots and exposes current frame telemetry', () => {
    const runtime = new EmberVisualRuntime(1337);
    runtime.initialize();
    const frame = runtime.getCurrentFrameData();

    expect(frame.room.id).toBeDefined();
    expect(frame.state.emberCharge).toBe(100);
  });
});
