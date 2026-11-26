import * as THREE from 'three';
import { ReactorShader } from '../shaders/reactor';

export class Crucible {
  public mesh: THREE.Mesh;
  public material: THREE.ShaderMaterial;
  public harmonicScarsTotal: number = 0;

  constructor() {
    const geo = new THREE.IcosahedronGeometry(6.5, 36);
    this.material = new THREE.ShaderMaterial({
      uniforms: THREE.UniformsUtils.clone(ReactorShader.uniforms),
      vertexShader: ReactorShader.vertexShader,
      fragmentShader: ReactorShader.fragmentShader,
    });
    this.mesh = new THREE.Mesh(geo, this.material);
  }

  public pulse() {
    this.material.uniforms.uPulseEnergy.value = 1.0;
  }

  public applyHarmonicScar() {
    this.harmonicScarsTotal += 1;
    this.material.uniforms.uScarIntensity.value = 1.0;
  }

  public resetExperiments() {
    this.material.uniforms.uMagicAngle.value = 0.0;
    this.material.uniforms.uCymaticsFreq.value = 0.0;
    this.material.uniforms.uQuarantine.value = 0.0;
  }

  public scram() {
    this.resetExperiments();
    this.material.uniforms.uTemperature.value = 50.0;
    this.material.uniforms.uPhase.value = 0;
    this.material.uniforms.uColorA.value.set('#78350f');
    this.material.uniforms.uColorB.value.set('#0a0a0d');
    this.material.uniforms.uMixRatio.value = 1.0;
  }

  public update(delta: number) {
    this.material.uniforms.uTime.value += delta;
    if (this.material.uniforms.uPulseEnergy.value > 0.0) {
      this.material.uniforms.uPulseEnergy.value = Math.max(0.0, this.material.uniforms.uPulseEnergy.value - delta * 2.0);
    }
  }
}
