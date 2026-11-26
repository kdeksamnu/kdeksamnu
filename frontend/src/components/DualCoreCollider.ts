import * as THREE from 'three';

export class DualCoreCollider {
  public group: THREE.Group;
  public coreAlpha: THREE.Mesh;
  public coreBeta: THREE.Mesh;
  public railLeft: THREE.Mesh;
  public railRight?: THREE.Mesh;
  public isColliding: boolean = false;
  private animProgress: number = 0;
  private onImpactCallback?: () => void;

  constructor() {
    this.group = new THREE.Group();

    // Accelerator Linear Rails
    const railGeo = new THREE.CylinderGeometry(0.3, 0.3, 34, 16);
    const railMat = new THREE.MeshStandardMaterial({
      color: 0x1f2937,
      metalness: 0.9,
      roughness: 0.3,
      emissive: new THREE.Color(0x3b82f6),
      emissiveIntensity: 0.2
    });

    this.railLeft = new THREE.Mesh(railGeo, railMat);
    this.railLeft.rotation.z = Math.PI / 2;
    this.railLeft.position.set(0, -5, 0);
    this.group.add(this.railLeft);

    // Left Core Alpha (Reagent A)
    const sphereGeo = new THREE.SphereGeometry(2.5, 24, 24);
    const matAlpha = new THREE.MeshStandardMaterial({
      color: 0x00e5ff,
      metalness: 0.8,
      roughness: 0.2,
      emissive: new THREE.Color(0x00e5ff),
      emissiveIntensity: 0.5
    });
    this.coreAlpha = new THREE.Mesh(sphereGeo, matAlpha);
    this.coreAlpha.position.set(-18, 0, 0);
    this.group.add(this.coreAlpha);

    // Right Core Beta (Reagent B)
    const matBeta = new THREE.MeshStandardMaterial({
      color: 0xffd700,
      metalness: 0.8,
      roughness: 0.2,
      emissive: new THREE.Color(0xffd700),
      emissiveIntensity: 0.5
    });
    this.coreBeta = new THREE.Mesh(sphereGeo, matBeta);
    this.coreBeta.position.set(18, 0, 0);
    this.group.add(this.coreBeta);

    this.group.visible = false;
  }

  public setColors(colorA: string, colorB: string) {
    (this.coreAlpha.material as THREE.MeshStandardMaterial).color.set(colorA);
    (this.coreAlpha.material as THREE.MeshStandardMaterial).emissive.set(colorA);
    (this.coreBeta.material as THREE.MeshStandardMaterial).color.set(colorB);
    (this.coreBeta.material as THREE.MeshStandardMaterial).emissive.set(colorB);
  }

  public launchCollision(onImpact: () => void) {
    if (this.isColliding) return;
    this.isColliding = true;
    this.animProgress = 0;
    this.onImpactCallback = onImpact;
    this.group.visible = true;
    this.coreAlpha.position.set(-18, 0, 0);
    this.coreBeta.position.set(18, 0, 0);
  }

  public update(delta: number) {
    if (!this.isColliding) return;

    this.animProgress += delta * 1.5;
    // Exponential acceleration toward center
    const t = Math.min(1.0, this.animProgress);
    const ease = Math.pow(t, 3.0);
    const xDist = (1.0 - ease) * 18.0;

    this.coreAlpha.position.x = -xDist;
    this.coreBeta.position.x = xDist;

    this.coreAlpha.rotation.y += delta * 12.0;
    this.coreBeta.rotation.y -= delta * 12.0;

    if (t >= 1.0) {
      this.isColliding = false;
      this.group.visible = false;
      if (this.onImpactCallback) {
        this.onImpactCallback();
      }
    }
  }
}
