import * as THREE from 'three';
import { AetherRaymarchShader } from '../shaders/aetherRaymarch';

export class AetherAtelier {
  public mesh: THREE.Mesh;
  public material: THREE.ShaderMaterial;

  constructor() {
    const geo = new THREE.PlaneGeometry(2, 2);
    this.material = new THREE.ShaderMaterial({
      uniforms: THREE.UniformsUtils.clone(AetherRaymarchShader.uniforms),
      vertexShader: AetherRaymarchShader.vertexShader,
      fragmentShader: AetherRaymarchShader.fragmentShader,
      depthWrite: false,
      depthTest: false
    });

    this.mesh = new THREE.Mesh(geo, this.material);
    this.mesh.visible = false;
  }

  public update(delta: number, mouseX: number, mouseY: number) {
    if (!this.mesh.visible) return;
    this.material.uniforms.uTime.value += delta;
    this.material.uniforms.uMouse.value.set(
      mouseX / window.innerWidth,
      1.0 - mouseY / window.innerHeight
    );
  }
}
