export interface RoomNode {
  id: string;
  seed: number;
  depth: number;
  exits: string[];
  stability: number; // 0 to 1
  metadata: {
    resonance: 'gold' | 'blue' | 'teal' | 'obsidian';
    hazards: string[];
  };
}

export class OfflineRoomGenerator {
  private baseSeed: number;

  constructor(baseSeed: number) {
    this.baseSeed = baseSeed;
  }

  // Simple mulberry32 pseudo-random number generator for deterministic results
  private lcg(seed: number): () => number {
    let s = seed;
    return () => {
      s = (s * 1664525 + 1013904223) % 4294967296;
      return s / 4294967296;
    };
  }

  public generateRoom(roomId: string, depth: number): RoomNode {
    // Combine baseSeed, roomId hash, and depth for absolute determinism
    let hash = this.baseSeed + depth * 31;
    for (let i = 0; i < roomId.length; i++) {
      hash = (hash << 5) - hash + roomId.charCodeAt(i);
      hash |= 0;
    }
    const rng = this.lcg(Math.abs(hash));

    const resonances: RoomNode['metadata']['resonance'][] = ['gold', 'blue', 'teal', 'obsidian'];
    const resonance = resonances[Math.floor(rng() * resonances.length)];

    const allHazards = ['Thermal Vent', 'Ember Bloom', 'Pressure Leak', 'Ash Drift', 'Resonance Echo'];
    const hazardCount = Math.floor(rng() * 3);
    const hazards: string[] = [];
    for (let h = 0; h < hazardCount; h++) {
      const hazard = allHazards[Math.floor(rng() * allHazards.length)];
      if (!hazards.includes(hazard)) hazards.push(hazard);
    }

    const exitCount = 1 + Math.floor(rng() * 3);
    const exits: string[] = [];
    for (let e = 0; e < exitCount; e++) {
      exits.push(`room_${depth + 1}_${Math.floor(rng() * 1000)}`);
    }

    return {
      id: roomId,
      seed: Math.abs(hash),
      depth,
      exits,
      stability: parseFloat((0.4 + rng() * 0.6).toFixed(2)),
      metadata: {
        resonance,
        hazards,
      },
    };
  }
}
