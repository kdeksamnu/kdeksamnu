import * as THREE from 'three';
import { CathedralMaze } from './CathedralMaze';

export class PlayerController {
  public position: THREE.Vector3 = new THREE.Vector3();
  public velocity: THREE.Vector3 = new THREE.Vector3();
  public avatarMesh: THREE.Mesh;
  public maze: CathedralMaze;
  public camera: THREE.PerspectiveCamera;
  public isFirstPerson: boolean = false;
  public yaw: number = 0;
  public pitch: number = 0;
  private keys: Record<string, boolean> = {};
  public radius: number = 0.85; // Player collision radius

  constructor(maze: CathedralMaze, camera: THREE.PerspectiveCamera) {
    this.maze = maze;
    this.camera = camera;
    this.position.copy(maze.spawnPos);

    // Player Avatar Mesh (Glowing Somatic Silhouette)
    const geo = new THREE.CapsuleGeometry(0.7, 1.2, 8, 16);
    const mat = new THREE.MeshStandardMaterial({
      color: 0x00e5ff,
      emissive: new THREE.Color(0x00e5ff),
      emissiveIntensity: 0.6,
      roughness: 0.2
    });
    this.avatarMesh = new THREE.Mesh(geo, mat);
    this.avatarMesh.position.copy(this.position);
    this.avatarMesh.position.y = 1.3;
    maze.group.add(this.avatarMesh);

    this.bindInputs();
  }

  private bindInputs() {
    window.addEventListener('keydown', (e) => {
      this.keys[e.key.toLowerCase()] = true;
      if (e.key.toLowerCase() === 'v') {
        this.toggleCameraMode();
      }
    });

    window.addEventListener('keyup', (e) => {
      this.keys[e.key.toLowerCase()] = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (this.isFirstPerson && this.maze.group.visible) {
        this.yaw -= e.movementX * 0.0025;
        this.pitch = Math.max(-1.4, Math.min(1.4, this.pitch - e.movementY * 0.0025));
      }
    });
  }

  public toggleCameraMode(): boolean {
    this.isFirstPerson = !this.isFirstPerson;
    this.avatarMesh.visible = !this.isFirstPerson;
    return this.isFirstPerson;
  }

  public update(delta: number) {
    if (!this.maze.group.visible) return;

    const speed = (this.keys['shift'] ? 12.0 : 7.0) * delta;
    const move = new THREE.Vector3();

    // Calculate forward & right movement vectors
    const forward = this.isFirstPerson
      ? new THREE.Vector3(-Math.sin(this.yaw), 0, -Math.cos(this.yaw))
      : new THREE.Vector3(0, 0, -1);

    const right = this.isFirstPerson
      ? new THREE.Vector3(Math.cos(this.yaw), 0, -Math.sin(this.yaw))
      : new THREE.Vector3(1, 0, 0);

    if (this.keys['w'] || this.keys['arrowup']) move.add(forward);
    if (this.keys['s'] || this.keys['arrowdown']) move.sub(forward);
    if (this.keys['d'] || this.keys['arrowright']) move.add(right);
    if (this.keys['a'] || this.keys['arrowleft']) move.sub(right);

    if (move.lengthSq() > 0) {
      move.normalize().multiplyScalar(speed);

      // Continuous Sliding Collision Detection (Independent Axis Resolution)
      const nextX = this.position.x + move.x;
      if (!this.checkWallCollision(nextX, this.position.z)) {
        this.position.x = nextX;
      }

      const nextZ = this.position.z + move.z;
      if (!this.checkWallCollision(this.position.x, nextZ)) {
        this.position.z = nextZ;
      }
    }

    this.avatarMesh.position.set(this.position.x, 1.3, this.position.z);

    // Update Camera
    if (this.isFirstPerson) {
      this.camera.position.set(this.position.x, 2.2, this.position.z);
      const target = new THREE.Vector3(
        this.position.x - Math.sin(this.yaw) * Math.cos(this.pitch),
        this.position.y + 2.2 + Math.sin(this.pitch),
        this.position.z - Math.cos(this.yaw) * Math.cos(this.pitch)
      );
      this.camera.lookAt(target);
    } else {
      // Isometric Follow Cam
      this.camera.position.set(this.position.x, 24.0, this.position.z + 18.0);
      this.camera.lookAt(this.position.x, 0, this.position.z);
    }
  }

  // Circle to Box AABB Wall Collision Test
  private checkWallCollision(px: number, pz: number): boolean {
    const halfW = (this.maze.width * this.maze.cellSize) / 2;
    const halfH = (this.maze.height * this.maze.cellSize) / 2;
    const S = this.maze.cellSize;
    const r = this.radius;

    const minCol = Math.max(0, Math.floor((px - r + halfW) / S));
    const maxCol = Math.min(this.maze.width - 1, Math.floor((px + r + halfW) / S));
    const minRow = Math.max(0, Math.floor((pz - r + halfH) / S));
    const maxRow = Math.min(this.maze.height - 1, Math.floor((pz + r + halfH) / S));

    for (let y = minRow; y <= maxRow; y++) {
      for (let x = minCol; x <= maxCol; x++) {
        if (this.maze.grid[y][x] === 1) {
          const bMinX = x * S - halfW;
          const bMaxX = bMinX + S;
          const bMinZ = y * S - halfH;
          const bMaxZ = bMinZ + S;

          const closestX = Math.max(bMinX, Math.min(px, bMaxX));
          const closestZ = Math.max(bMinZ, Math.min(pz, bMaxZ));
          const dx = px - closestX;
          const dz = pz - closestZ;

          if (dx * dx + dz * dz < r * r) {
            return true;
          }
        }
      }
    }
    return false;
  }
}
