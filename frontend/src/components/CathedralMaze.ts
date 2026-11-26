import * as THREE from 'three';

export interface RelicItem {
  id: number;
  mesh: THREE.Mesh;
  x: number;
  z: number;
  type: string;
  color: string;
  collected: boolean;
}

export class CathedralMaze {
  public group: THREE.Group;
  public width: number = 17;
  public height: number = 17;
  public cellSize: number = 4.0;
  public grid: number[][] = [];
  public wallMesh: THREE.InstancedMesh;
  public floorMesh: THREE.Mesh;
  public relics: RelicItem[] = [];
  public spawnPos: THREE.Vector3 = new THREE.Vector3(0, 0, 0);

  constructor() {
    this.group = new THREE.Group();
    this.generateGrid();

    // 1. Build Wall InstancedMesh
    let wallCount = 0;
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        if (this.grid[y][x] === 1) wallCount++;
      }
    }

    const wallGeo = new THREE.BoxGeometry(this.cellSize, 6.0, this.cellSize);
    const wallMat = new THREE.MeshStandardMaterial({
      color: 0x0f1118,
      roughness: 0.35,
      metalness: 0.85,
      emissive: new THREE.Color(0x00e5ff),
      emissiveIntensity: 0.04
    });

    this.wallMesh = new THREE.InstancedMesh(wallGeo, wallMat, wallCount);
    const dummy = new THREE.Object3D();
    const halfW = (this.width * this.cellSize) / 2;
    const halfH = (this.height * this.cellSize) / 2;

    let idx = 0;
    for (let y = 0; y < this.height; y++) {
      for (let x = 0; x < this.width; x++) {
        if (this.grid[y][x] === 1) {
          const wx = x * this.cellSize - halfW + this.cellSize / 2;
          const wz = y * this.cellSize - halfH + this.cellSize / 2;
          dummy.position.set(wx, 3.0, wz);
          dummy.updateMatrix();
          this.wallMesh.setMatrixAt(idx++, dummy.matrix);
        }
      }
    }
    this.wallMesh.instanceMatrix.needsUpdate = true;
    this.group.add(this.wallMesh);

    // 2. Floor Plane
    const floorGeo = new THREE.PlaneGeometry(this.width * this.cellSize, this.height * this.cellSize);
    const floorMat = new THREE.MeshStandardMaterial({
      color: 0x07080c,
      roughness: 0.5,
      metalness: 0.5
    });
    this.floorMesh = new THREE.Mesh(floorGeo, floorMat);
    this.floorMesh.rotation.x = -Math.PI / 2;
    this.floorMesh.position.y = 0.0;
    this.group.add(this.floorMesh);

    // 3. Spawn Spectral Relics in dead-ends
    this.spawnRelics();

    // 4. Calculate Player Spawn Position (Entrance)
    this.spawnPos.set(
      1 * this.cellSize - halfW + this.cellSize / 2,
      1.2,
      1 * this.cellSize - halfH + this.cellSize / 2
    );

    this.group.visible = false;
  }

  private generateGrid() {
    this.grid = Array.from({ length: this.height }, () => Array(this.width).fill(1));

    const carve = (cx: number, cy: number) => {
      this.grid[cy][cx] = 0;
      const dirs = [
        [0, -2], [0, 2], [-2, 0], [2, 0]
      ].sort(() => Math.random() - 0.5);

      for (const [dx, dy] of dirs) {
        const nx = cx + dx;
        const ny = cy + dy;
        if (nx > 0 && nx < this.width - 1 && ny > 0 && ny < this.height - 1 && this.grid[ny][nx] === 1) {
          this.grid[cy + dy / 2][cx + dx / 2] = 0;
          carve(nx, ny);
        }
      }
    };

    carve(1, 1);

    // Central Anomaly Vault (3x3 open chamber)
    const midX = Math.floor(this.width / 2);
    const midY = Math.floor(this.height / 2);
    for (let dy = -1; dy <= 1; dy++) {
      for (let dx = -1; dx <= 1; dx++) {
        this.grid[midY + dy][midX + dx] = 0;
      }
    }
  }

  private spawnRelics() {
    const halfW = (this.width * this.cellSize) / 2;
    const halfH = (this.height * this.cellSize) / 2;
    const types = [
      { name: 'Auric Joy Shard', color: '#ffd700' },
      { name: 'Teal Flux Shard', color: '#00e5ff' },
      { name: 'Void Fear Shard', color: '#8b5cf6' },
      { name: 'Emerald Shard', color: '#10b981' }
    ];

    let rId = 0;
    const relicGeo = new THREE.OctahedronGeometry(0.7, 0);

    for (let y = 1; y < this.height - 1; y++) {
      for (let x = 1; x < this.width - 1; x++) {
        if (this.grid[y][x] === 0 && Math.random() < 0.12 && rId < 14) {
          const type = types[rId % types.length];
          const mat = new THREE.MeshStandardMaterial({
            color: type.color,
            emissive: new THREE.Color(type.color),
            emissiveIntensity: 0.8,
            roughness: 0.1
          });
          const mesh = new THREE.Mesh(relicGeo, mat);
          const wx = x * this.cellSize - halfW + this.cellSize / 2;
          const wz = y * this.cellSize - halfH + this.cellSize / 2;
          mesh.position.set(wx, 1.4, wz);
          this.group.add(mesh);

          this.relics.push({
            id: rId++,
            mesh,
            x: wx,
            z: wz,
            type: type.name,
            color: type.color,
            collected: false
          });
        }
      }
    }
  }

  public update(delta: number) {
    if (!this.group.visible) return;
    const t = performance.now() * 0.003;
    this.relics.forEach(r => {
      if (!r.collected) {
        r.mesh.rotation.y += delta * 1.5;
        r.mesh.position.y = 1.4 + Math.sin(t + r.id) * 0.25;
      }
    });
  }
}
