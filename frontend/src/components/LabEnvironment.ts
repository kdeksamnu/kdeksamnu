import * as THREE from 'three';

export class LabEnvironment {
  public group: THREE.Group;
  public outerRing: THREE.Mesh;
  public midRing: THREE.Mesh;
  public innerRing: THREE.Mesh;
  public particles: THREE.Points;
  public laserPillars: THREE.Group;
  private particleCount: number = 400;
  private particleGeo: THREE.BufferGeometry;

  constructor() {
    this.group = new THREE.Group();

    // 1. Pedestal Base
    const baseGeo = new THREE.CylinderGeometry(14, 16, 2.5, 32);
    const baseMat = new THREE.MeshStandardMaterial({
      color: 0x0f0f16,
      roughness: 0.4,
      metalness: 0.85
    });
    const base = new THREE.Mesh(baseGeo, baseMat);
    base.position.y = -10.5;
    this.group.add(base);

    // Glowing calibration rim
    const rimGeo = new THREE.TorusGeometry(14.2, 0.25, 16, 64);
    const rimMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff });
    const rim = new THREE.Mesh(rimGeo, rimMat);
    rim.rotation.x = Math.PI / 2;
    rim.position.y = -9.2;
    this.group.add(rim);

    // 2. Gimbal Magnetic Rings
    const ringMat = new THREE.MeshStandardMaterial({
      color: 0x222230,
      metalness: 0.9,
      roughness: 0.2,
      emissive: new THREE.Color(0x00e5ff),
      emissiveIntensity: 0.15
    });

    this.outerRing = new THREE.Mesh(new THREE.TorusGeometry(12.5, 0.35, 16, 64), ringMat);
    this.midRing = new THREE.Mesh(new THREE.TorusGeometry(11.0, 0.3, 16, 64), ringMat);
    this.innerRing = new THREE.Mesh(new THREE.TorusGeometry(9.5, 0.25, 16, 64), ringMat);

    this.group.add(this.outerRing);
    this.group.add(this.midRing);
    this.group.add(this.innerRing);

    // 3. Quarantine Laser Pillars (4 emitter pillars around dais)
    this.laserPillars = new THREE.Group();
    const beamGeo = new THREE.CylinderGeometry(0.08, 0.08, 22, 16);
    const beamMat = new THREE.MeshBasicMaterial({ color: 0xf59e0b, transparent: true, opacity: 0.0 });
    const angles = [0, Math.PI / 2, Math.PI, (Math.PI * 3) / 2];
    angles.forEach(a => {
      const beam = new THREE.Mesh(beamGeo, beamMat);
      beam.position.set(Math.cos(a) * 11, 0, Math.sin(a) * 11);
      this.laserPillars.add(beam);
    });
    this.group.add(this.laserPillars);

    // 4. Particles
    this.particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.particleCount * 3);
    for (let i = 0; i < this.particleCount; i++) {
      positions[i * 3 + 0] = (Math.random() - 0.5) * 16;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 16;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 16;
    }
    this.particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const pMat = new THREE.PointsMaterial({
      color: 0x00e5ff,
      size: 0.35,
      transparent: true,
      opacity: 0.75,
      blending: THREE.AdditiveBlending
    });

    this.particles = new THREE.Points(this.particleGeo, pMat);
    this.group.add(this.particles);
  }

  public setQuarantine(active: boolean) {
    this.laserPillars.children.forEach(child => {
      ((child as THREE.Mesh).material as THREE.MeshBasicMaterial).opacity = active ? 0.85 : 0.0;
    });
  }

  public update(delta: number, containment: number) {
    const speed = (1.1 - containment * 0.5);
    this.outerRing.rotation.x += delta * 0.4 * speed;
    this.outerRing.rotation.y += delta * 0.6 * speed;
    this.midRing.rotation.y -= delta * 0.7 * speed;
    this.innerRing.rotation.z += delta * 0.9 * speed;

    const pos = this.particleGeo.attributes.position.array as Float32Array;
    for (let i = 0; i < this.particleCount; i++) {
      pos[i * 3 + 1] += delta * (2.0 + Math.sin(i) * 1.5);
      if (pos[i * 3 + 1] > 10.0) pos[i * 3 + 1] = -9.0;
    }
    this.particleGeo.attributes.position.needsUpdate = true;
  }
}
