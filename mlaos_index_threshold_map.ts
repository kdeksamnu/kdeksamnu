// ============================================================================
// GENESIS-Ω01: TACTICAL TOPOLOGY BINDING (BRIDGING PYTHON MANIFEST -> TS STATE)
// ============================================================================

export interface GridTile {
  x: number;
  y: number;
  classification: 'Deployment' | 'Scar_Node' | 'Cover' | 'Hazard' | 'Objective' | 'Extraction' | 'Standard';
  acBonus: number;
  hazardEffect?: string;
}

export function initializeIndexThresholdMap(state: any): Map<string, GridTile> {
  const grid = new Map<string, GridTile>();

  // 1. Initialize 16x20 Standard Grid
  for (let x = 0; x < 16; x++) {
    for (let y = 0; y < 20; y++) {
      const key = `${x},${y}`;
      grid.set(key, { x, y, classification: 'Standard', acBonus: 0 });
    }
  }

  // 2. Bind Cover Structures (Basalt Pillars: C1, C2, C3, C4 clusters)
  const basaltPillars = [
    { x: 4, y: 15 }, { x: 5, y: 15 }, { x: 4, y: 16 }, { x: 5, y: 16 }, // C1
    { x: 10, y: 15 }, { x: 11, y: 15 }, { x: 10, y: 16 }, { x: 11, y: 16 }, // C2
    { x: 4, y: 5 }, { x: 5, y: 5 }, { x: 4, y: 6 }, { x: 5, y: 6 },     // C3
    { x: 10, y: 5 }, { x: 11, y: 5 }, { x: 10, y: 6 }, { x: 11, y: 6 }    // C4
  ];
  basaltPillars.forEach(p => {
    grid.set(`${p.x},${p.y}`, { ...p, classification: 'Cover', acBonus: 3 });
  });

  // 3. Bind WAL Conduits (Hazard Corridors)
  const walConduits = [{ x: 1, y: 17 }, { x: 2, y: 17 }, { x: 1, y: 18 }, { x: 2, y: 18 }, { x: 12, y: 17 }, { x: 13, y: 17 }, { x: 12, y: 18 }, { x: 13, y: 18 }];
  walConduits.forEach(p => {
    grid.set(`${p.x},${p.y}`, {
      ...p,
      classification: 'Hazard',
      acBonus: 0,
      hazardEffect: '1d6 Syntax Damage + 1 Strain'
    });
  });

  // 4. Bind Objective Core (Index Threshold Central Altar)
  const altarTiles = [{ x: 8, y: 11 }, { x: 9, y: 11 }, { x: 8, y: 12 }, { x: 9, y: 12 }];
  altarTiles.forEach(p => {
    grid.set(`${p.x},${p.y}`, { ...p, classification: 'Objective', acBonus: 0 });
  });

  // 5. Register Paraconsistent Scar Anchors into Authoritative State
  state.createScarAnchor(4, 9, 'Paraconsistent', 'S1 Initial Anchor Node');
  state.createScarAnchor(11, 9, 'Paraconsistent', 'S2 Initial Anchor Node');
  state.createScarAnchor(7, 18, 'Paraconsistent', 'S3 Initial Anchor Node');

  // 6. Bind Extraction Terminal
  grid.set('0,19', { x: 0, y: 19, classification: 'Extraction', acBonus: 0 });

  return grid;
}
