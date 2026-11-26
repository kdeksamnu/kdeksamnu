import * as THREE from 'three';
import { DitherShader } from '../shaders/dither';

export class VoxelStrata {
  public mesh: THREE.InstancedMesh;
  public material: THREE.ShaderMaterial;
  private dummy = new THREE.Object3D();
  public size: number = 14;
  public spacing: number = 1.15;
  public rotationSpeed: number = 0.15;
  public sparsity: number = 2;

  constructor() {
    const count = this.size * this.size * this.size;
    const geometry = new THREE.BoxGeometry(0.85, 0.85, 0.85);

    this.material = new THREE.ShaderMaterial({
      uniforms: THREE.UniformsUtils.clone(DitherShader.uniforms),
      vertexShader: DitherShader.vertexShader,
      fragmentShader: DitherShader.fragmentShader,
      defines: {
        USE_INSTANCING: ''
      }
    });

    this.mesh = new THREE.InstancedMesh(geometry, this.material, count);
    this.rebuildGrid();
  }

  public rebuildGrid() {
    let idx = 0;
    const half = (this.size * this.spacing) / 2;
    for (let x = 0; x < this.size; x++) {
      for (let y = 0; y < this.size; y++) {
        for (let z = 0; z < this.size; z++) {
          if ((x + y + z) % this.sparsity === 0) {
            this.dummy.position.set(
              x * this.spacing - half,
              y * this.spacing - half,
              z * this.spacing - half
            );
            this.dummy.updateMatrix();
            this.mesh.setMatrixAt(idx++, this.dummy.matrix);
          }
        }
      }
    }
    this.mesh.count = idx;
    this.mesh.instanceMatrix.needsUpdate = true;
  }

  public setMode(m: number) {
    this.material.uniforms.uMode.value = m;
  }

  public setSpacing(v: number) { this.spacing = v; this.rebuildGrid(); }
  public setWireframe(v: boolean) { this.material.wireframe = v; }

  public update(delta: number) {
    this.material.uniforms.uTime.value += delta;
    if (this.rotationSpeed > 0) {
      this.mesh.rotation.y += delta * this.rotationSpeed;
    }
  }
}
