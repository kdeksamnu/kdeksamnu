import * as THREE from 'three';
import { SomaticDualLumenShader } from '../shaders/somaticDualLumen';
import { SomaticSolver } from '../core/SomaticSolver';

export class SomaticKinematicFigure {
  public group: THREE.Group;
  public material: THREE.ShaderMaterial;
  public nodes: THREE.Mesh[] = [];
  public mudraTrailMesh: THREE.Line;
  private trailBuffer: THREE.Vector3[] = [];
  private trailMax: number = 96;
  public forceArrowGround: THREE.ArrowHelper;
  public spineTorqueRing: THREE.Mesh;
  public energyLine: THREE.Line; // Visual conduit from Panel C to 3D node

  constructor() {
    this.group = new THREE.Group();

    this.material = new THREE.ShaderMaterial({
      uniforms: THREE.UniformsUtils.clone(SomaticDualLumenShader.uniforms),
      vertexShader: SomaticDualLumenShader.vertexShader,
      fragmentShader: SomaticDualLumenShader.fragmentShader
    });

    // 1. Create Rigged Pass Nodes P1 -> P11
    const nodeGeo = new THREE.CylinderGeometry(0.5, 0.7, 1.8, 8);
    for (let i = 0; i < 11; i++) {
      const mesh = new THREE.Mesh(nodeGeo, this.material);
      this.nodes.push(mesh);
      this.group.add(mesh);
    }

    // 2. Ground Reaction Force Vector at P1
    this.forceArrowGround = new THREE.ArrowHelper(
      new THREE.Vector3(0, 1, 0),
      new THREE.Vector3(0, 0, 0),
      4.5,
      0x00e5ff,
      1.2,
      0.6
    );
    this.group.add(this.forceArrowGround);

    // 3. Spinal Torsional Shear Ring at P4
    const ringGeo = new THREE.TorusGeometry(1.6, 0.15, 8, 32);
    const ringMat = new THREE.MeshBasicMaterial({ color: 0xffd700 });
    this.spineTorqueRing = new THREE.Mesh(ringGeo, ringMat);
    this.spineTorqueRing.rotation.x = Math.PI / 2;
    this.group.add(this.spineTorqueRing);

    // 4. P11 Mudrā Trajectory Ribbon Ring Buffer
    const lineGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(this.trailMax * 3);
    lineGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const lineMat = new THREE.LineBasicMaterial({
      color: 0xffd700,
      transparent: true,
      opacity: 0.85,
      blending: THREE.AdditiveBlending
    });
    this.mudraTrailMesh = new THREE.Line(lineGeo, lineMat);
    this.group.add(this.mudraTrailMesh);

    // 5. Active Coupling Energy Line
    const eGeo = new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(), new THREE.Vector3()]);
    this.energyLine = new THREE.Line(eGeo, new THREE.LineBasicMaterial({ color: 0x00e5ff, transparent: true, opacity: 0.0 }));
    this.group.add(this.energyLine);

    this.group.position.y = 0.0;
  }

  public drawEnergyConduit(pIdx: number, active: boolean) {
    if (active && pIdx < this.nodes.length) {
      const p = this.nodes[pIdx].position;
      const pts = [new THREE.Vector3(-14, p.y + 4, 0), p];
      this.energyLine.geometry.setFromPoints(pts);
      (this.energyLine.material as THREE.LineBasicMaterial).opacity = 0.9;
    } else {
      (this.energyLine.material as THREE.LineBasicMaterial).opacity = 0.0;
    }
  }

  public update(delta: number, solver: SomaticSolver) {
    const t = performance.now() * 0.0015;
    this.material.uniforms.uTime.value = t;

    // C4 Dialetheic Tension Glow feedback
    const c4Error = Math.abs(solver.constraints[3].error);
    this.material.uniforms.uDialetheicTension.value = Math.min(1.0, c4Error * 1.5);

    // Animate P1 -> P11 Kinematic Hierarchy
    const p1_y = 0.5;
    const p2_y = p1_y + solver.passes[1].momentum * 1.2;
    const p3_y = p2_y + solver.passes[2].momentum * 1.5;
    const p4_y = p3_y + solver.passes[3].momentum * 1.4;
    const p5_y = p4_y + solver.passes[4].momentum * 1.5;
    const p6_y = p5_y + 1.6;

    this.nodes[0].position.set(0, p1_y, 0);
    this.nodes[1].position.set(0, p2_y, Math.sin(t * 2.0) * 0.2);
    this.nodes[2].position.set(0, p3_y, -Math.sin(t * 2.0) * 0.3);
    this.nodes[3].position.set(0, p4_y, 0); // P4 Lumbar
    this.nodes[4].position.set(0, p5_y, 0); // P5 Thoracic
    this.nodes[5].position.set(0, p6_y, 0); // P6 Cervical

    // P7-P11 Arm & Mudrā Claws
    const armAngle = t * 2.5;
    const p8_pos = new THREE.Vector3(2.5, p5_y, Math.sin(armAngle) * 1.2);
    const p9_pos = new THREE.Vector3(4.2, p5_y - 0.5, Math.sin(armAngle + 1.0) * 1.5);
    const p10_pos = new THREE.Vector3(5.6, p5_y - 1.2, Math.cos(armAngle) * 1.8);
    const p11_pos = new THREE.Vector3(
      6.8 + Math.cos(t * 4.0) * 1.2,
      p5_y - 0.5 + Math.sin(t * 3.5) * 1.5,
      Math.sin(t * 4.0) * 2.5
    );

    this.nodes[6].position.set(1.5, p5_y + 0.2, 0);
    this.nodes[7].position.copy(p8_pos);
    this.nodes[8].position.copy(p9_pos);
    this.nodes[9].position.copy(p10_pos);
    this.nodes[10].position.copy(p11_pos); // P11 Mudrā

    // Ground reaction force pulse
    const forceMag = solver.passes[0].momentum * 3.5;
    this.forceArrowGround.setLength(forceMag, 1.0, 0.4);

    // Spine torque oscillation
    this.spineTorqueRing.position.set(0, p4_y, 0);
    this.spineTorqueRing.rotation.z += delta * solver.passes[3].momentum * 3.0;

    // Append-Only Ring Buffer for P11 Trajectory
    this.trailBuffer.unshift(p11_pos.clone());
    if (this.trailBuffer.length > this.trailMax) this.trailBuffer.pop();

    const linePositions = this.mudraTrailMesh.geometry.attributes.position.array as Float32Array;
    for (let i = 0; i < this.trailBuffer.length; i++) {
      linePositions[i * 3 + 0] = this.trailBuffer[i].x;
      linePositions[i * 3 + 1] = this.trailBuffer[i].y;
      linePositions[i * 3 + 2] = this.trailBuffer[i].z;
    }
    this.mudraTrailMesh.geometry.attributes.position.needsUpdate = true;
  }
}
