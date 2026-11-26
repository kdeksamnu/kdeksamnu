import * as THREE from 'three';

export class SPHFluid {
  public mesh: THREE.InstancedMesh;
  public count: number = 700;
  private positions: Float32Array;
  private velocities: Float32Array;
  private dummy: THREE.Object3D = new THREE.Object3D();
  public viscosity: number = 0.96;
  public surfaceTension: number = 1.8;
  public containmentRadius: number = 7.5;
  public activeColor: THREE.Color = new THREE.Color(0x00e5ff);

  constructor() {
    const geo = new THREE.SphereGeometry(0.38, 12, 12);
    const mat = new THREE.MeshStandardMaterial({
      color: this.activeColor,
      roughness: 0.15,
      metalness: 0.85,
      emissive: this.activeColor,
      emissiveIntensity: 0.25
    });

    this.mesh = new THREE.InstancedMesh(geo, mat, this.count);
    this.positions = new Float32Array(this.count * 3);
    this.velocities = new Float32Array(this.count * 3);

    // Initialize fluid droplet sphere
    for (let i = 0; i < this.count; i++) {
      const r = Math.cbrt(Math.random()) * 5.0;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);

      this.positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      this.positions[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      this.positions[i * 3 + 2] = r * Math.cos(phi);

      this.velocities[i * 3 + 0] = (Math.random() - 0.5) * 0.5;
      this.velocities[i * 3 + 1] = (Math.random() - 0.5) * 0.5;
      this.velocities[i * 3 + 2] = (Math.random() - 0.5) * 0.5;
    }
    this.mesh.visible = false;
  }

  public setColor(hex: string) {
    this.activeColor.set(hex);
    (this.mesh.material as THREE.MeshStandardMaterial).color.set(hex);
    (this.mesh.material as THREE.MeshStandardMaterial).emissive.set(hex);
  }

  public triggerSplash(strength: number = 8.0) {
    for (let i = 0; i < this.count; i++) {
      this.velocities[i * 3 + 0] += (Math.random() - 0.5) * strength;
      this.velocities[i * 3 + 1] += (Math.random() - 0.5) * strength;
      this.velocities[i * 3 + 2] += (Math.random() - 0.5) * strength;
    }
  }

  public update(delta: number) {
    if (!this.mesh.visible) return;

    const dt = Math.min(delta, 0.05);
    const R = this.containmentRadius;

    for (let i = 0; i < this.count; i++) {
      let px = this.positions[i * 3 + 0];
      let py = this.positions[i * 3 + 1];
      let pz = this.positions[i * 3 + 2];

      let vx = this.velocities[i * 3 + 0];
      let vy = this.velocities[i * 3 + 1];
      let vz = this.velocities[i * 3 + 2];

      // Inward surface tension pull toward center of mass
      const dist = Math.sqrt(px * px + py * py + pz * pz) + 0.001;
      const pull = this.surfaceTension * (dist - 1.5);
      vx -= (px / dist) * pull * dt;
      vy -= (py / dist) * pull * dt;
      vz -= (pz / dist) * pull * dt;

      // Viscous drag
      vx *= this.viscosity;
      vy *= this.viscosity;
      vz *= this.viscosity;

      // Integrate
      px += vx * dt * 5.0;
      py += vy * dt * 5.0;
      pz += vz * dt * 5.0;

      // Spherical containment boundary bounce
      const curDist = Math.sqrt(px * px + py * py + pz * pz);
      if (curDist > R) {
        const nx = px / curDist;
        const ny = py / curDist;
        const nz = pz / curDist;
        px = nx * R;
        py = ny * R;
        pz = nz * R;
        vx = -vx * 0.7;
        vy = -vy * 0.7;
        vz = -vz * 0.7;
      }

      this.positions[i * 3 + 0] = px;
      this.positions[i * 3 + 1] = py;
      this.positions[i * 3 + 2] = pz;

      this.velocities[i * 3 + 0] = vx;
      this.velocities[i * 3 + 1] = vy;
      this.velocities[i * 3 + 2] = vz;

      this.dummy.position.set(px, py, pz);
      this.dummy.updateMatrix();
      this.mesh.setMatrixAt(i, this.dummy.matrix);
    }
    this.mesh.instanceMatrix.needsUpdate = true;
  }
}
