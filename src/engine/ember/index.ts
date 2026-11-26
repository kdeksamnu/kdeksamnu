import { SeededTraversalEngine } from './seededTraversal';
import { ContradictionIntegrationEngine } from './contradictionIntegration';
import { EmberRuntimeState } from './emberState';
import { RoomNode } from './offlineRoomGenerator';

export class EmberVisualRuntime {
  private traversalEngine: SeededTraversalEngine;
  private canvasContextId: string;

  constructor(seed: number, canvasContextId: string = 'ember-viewport') {
    this.traversalEngine = new SeededTraversalEngine(seed);
    this.canvasContextId = canvasContextId;
  }

  public initialize(): void {
    console.log(`[EmberRuntime] Initialized viewport context: #${this.canvasContextId}`);
  }

  public getCurrentFrameData(): {
    room: RoomNode;
    state: Return<EmberRuntimeState['getState']>;
  } {
    return {
      room: this.traversalEngine.getCurrentRoom(),
      state: this.traversalEngine.getStateInstance().getState(),
    };
  }

  public stepTraversal(nextRoomId: string): boolean {
    return this.traversalEngine.traverse(nextRoomId);
  }

  public submitEvidence(axiomKey: string, evidence: 'TRUE' | 'FALSE'): 'TRUE' | 'FALSE' | 'BOTH' | 'NEITHER' {
    return ContradictionIntegrationEngine.integrateEvidence(
      this.traversalEngine.getStateInstance(),
      axiomKey,
      evidence
    );
  }
}

export default EmberVisualRuntime;
