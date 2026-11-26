import * as THREE from 'three';

export class ComputeLoom {
  public mesh: THREE.Points;
  public count: number = 3200;
  private positions: Float32Array;
  private velocities: Float32Array;
  private targetPositions: Float32Array;
  private geo: THREE.BufferGeometry;
  public mousePos: THREE.Vector3 = new THREE.Vector3(0, 0, 0);
  public gravityStrength: number = 1.4;

  constructor() {
    this.geo = new THREE.BufferGeometry();
    this.positions = new Float32Array(this.count * 3);
    this.velocities = new Float32Array(this.count * 3);
    this.targetPositions = new Float32Array(this.count * 3);

    // Initial chaotic toroidal vortex
    for (let i = 0; i < this.count; i++) {
      const u = Math.random() * Math.PI * 2;
      const v = Math.random() * Math.PI * 2;
      const r = 4.0 + Math.random() * 8.0;

      this.positions[i * 3 + 0] = (r + Math.cos(v)) * Math.cos(u);
      this.positions[i * 3 + 1] = (Math.random() - 0.5) * 14.0;
      this.positions[i * 3 + 2] = (r + Math.cos(v)) * Math.sin(u);

      this.velocities[i * 3 + 0] = (Math.random() - 0.5) * 0.2;
      this.velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.2;
      this.velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.2;
    }

    this.geo.setAttribute('position', new THREE.BufferAttribute(this.positions, 3));

    const mat = new THREE.PointsMaterial({
      color: 0xffd700, // Liquid gold
      size: 0.38,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending
    });

    this.mesh = new THREE.Points(this.geo, mat);
    this.mesh.visible = false;
  }

  public update(delta: number) {
    if (!this.mesh.visible) return;

    const pos = this.geo.attributes.position.array as Float32Array;
    const time = performance.now() * 0.001;

    for (let i = 0; i < this.count; i++) {
      let px = pos[i * 3 + 0];
      let py = pos[i * 3 + 1];
      let pz = pos[i * 3 + 2];

      // Gravitational pull toward cursor anomaly
      const dx = this.mousePos.x - px;
      const dy = this.mousePos.y - py;
      const dz = this.mousePos.z - pz;
      const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) + 0.5;

      this.velocities[i * 3 + 0] += (dx / dist) * this.gravityStrength * delta * 4.0;
      this.velocities[i * 3 + 1] += (dy / dist) * this.gravityStrength * delta * 4.0;
      this.velocities[i * 3 + 2] += (dz / dist) * this.gravityStrength * delta * 4.0;

      // Swirling data vortex
      this.velocities[i * 3 + 0] += Math.sin(py * 0.5 + time) * delta * 1.5;
      this.velocities[i * 3 + 2] += Math.cos(px * 0.5 + time) * delta * 1.5;

      // Damping
      this.velocities[i * 3 + 0] *= 0.94;
      this.velocities[i * 3 + 1] *= 0.94;
      this.velocities[i * 3 + 2] *= 0.94;

      pos[i * 3 + 0] += this.velocities[i * 3 + 0];
      pos[i * 3 + 1] += this.velocities[i * 3 + 1];
      pos[i * 3 + 2] += this.velocities[i * 3 + 2];

      // Reset particles that stray too far
      if (Math.abs(px) > 28 || Math.abs(py) > 20 || Math.abs(pz) > 28) {
        pos[i * 3 + 0] = (Math.random() - 0.5) * 8.0;
        pos[i * 3 + 1] = (Math.random() - 0.5) * 8.0;
        pos[i * 3 + 2] = (Math.random() - 0.5) * 8.0;
      }
    }
    this.geo.attributes.position.needsUpdate = true;
  }
}
