import * as THREE from 'three';
import { DitherShader } from '../shaders/dither';

export class MeshManager {
  public group: THREE.Group;
  public instancedMesh: THREE.InstancedMesh;
  public singleMaterial: THREE.ShaderMaterial;
  public torusMesh: THREE.Mesh;
  public orbMesh: THREE.Mesh;
  public obeliskMesh: THREE.Mesh;
  public currentTarget: string = 'lattice';

  constructor(instancedMesh: THREE.InstancedMesh) {
    this.group = new THREE.Group();
    this.instancedMesh = instancedMesh;
    this.group.add(this.instancedMesh);

    // Shared uniform reference: any slider change affects all meshes simultaneously
    this.singleMaterial = new THREE.ShaderMaterial({
      uniforms: (this.instancedMesh.material as THREE.ShaderMaterial).uniforms,
      vertexShader: DitherShader.vertexShader,
      fragmentShader: DitherShader.fragmentShader,
    });

    // 1. Organic Torus Knot
    const torusGeo = new THREE.TorusKnotGeometry(6.5, 2.2, 160, 32, 2, 3);
    this.torusMesh = new THREE.Mesh(torusGeo, this.singleMaterial);
    this.torusMesh.visible = false;
    this.group.add(this.torusMesh);

    // 2. Prismatic Anomaly Orb
    const orbGeo = new THREE.IcosahedronGeometry(7.5, 32);
    this.orbMesh = new THREE.Mesh(orbGeo, this.singleMaterial);
    this.orbMesh.visible = false;
    this.group.add(this.orbMesh);

    // 3. Gothic Monolith / Obelisk
    const obeliskGeo = new THREE.CylinderGeometry(2.0, 4.5, 17, 6, 12);
    this.obeliskMesh = new THREE.Mesh(obeliskGeo, this.singleMaterial);
    this.obeliskMesh.visible = false;
    this.group.add(this.obeliskMesh);
  }

  public setTarget(target: string) {
    this.currentTarget = target;

    this.instancedMesh.visible = false;
    this.torusMesh.visible = false;
    this.orbMesh.visible = false;
    this.obeliskMesh.visible = false;

    this.torusMesh.position.set(0, 0, 0);
    this.orbMesh.position.set(0, 0, 0);
    this.obeliskMesh.position.set(0, 0, 0);

    if (target === 'lattice') {
      this.instancedMesh.visible = true;
    } else if (target === 'torus') {
      this.torusMesh.visible = true;
    } else if (target === 'orb') {
      this.orbMesh.visible = true;
    } else if (target === 'obelisk') {
      this.obeliskMesh.visible = true;
    } else if (target === 'trio') {
      this.torusMesh.visible = true;
      this.orbMesh.visible = true;
      this.obeliskMesh.visible = true;
      this.torusMesh.position.set(-18, 0, 0);
      this.orbMesh.position.set(0, 0, 0);
      this.obeliskMesh.position.set(18, 0, 0);
    }
  }

  public setWireframe(wire: boolean) {
    (this.instancedMesh.material as THREE.ShaderMaterial).wireframe = wire;
    this.singleMaterial.wireframe = wire;
  }

  public update(delta: number, rotSpeed: number) {
    if (rotSpeed > 0) {
      if (this.instancedMesh.visible) {
        this.instancedMesh.rotation.y += delta * rotSpeed;
      }
      if (this.torusMesh.visible) {
        this.torusMesh.rotation.y += delta * rotSpeed;
        this.torusMesh.rotation.x += delta * rotSpeed * 0.5;
      }
      if (this.orbMesh.visible) {
        this.orbMesh.rotation.y += delta * rotSpeed * 0.6;
      }
      if (this.obeliskMesh.visible) {
        this.obeliskMesh.rotation.y += delta * rotSpeed * 0.4;
      }
    }
  }
}
