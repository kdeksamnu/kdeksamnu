import * as THREE from 'three';

export interface MeshNode {
  id: number;
  position: THREE.Vector3;
  mesh: THREE.Mesh;
  active: boolean;
  degree: number;
}

export class Dimension8Mesh {
  public group: THREE.Group;
  public nodes: MeshNode[] = [];
  public edgeLines: THREE.LineSegments;
  public linePositions: Float32Array;
  public packetMesh: THREE.InstancedMesh;
  private packetCount: number = 24;
  private dummy: THREE.Object3D = new THREE.Object3D();
  public fiedlerValue: number = 0.3242;

  constructor(nodeCount: number = 8, radius: number = 18.0) {
    this.group = new THREE.Group();

    // 1. Generate 8 Octant Nodes (Dimension-8 Projected Centroids)
    const nodeGeo = new THREE.SphereGeometry(0.8, 16, 16);
    for (let i = 0; i < nodeCount; i++) {
      const phi = Math.acos(-1 + (2 * i) / nodeCount);
      const theta = Math.sqrt(nodeCount * Math.PI) * phi;

      const pos = new THREE.Vector3(
        radius * Math.sin(phi) * Math.cos(theta),
        radius * Math.sin(phi) * Math.sin(theta) * 0.6,
        radius * Math.cos(phi)
      );

      const mat = new THREE.MeshStandardMaterial({
        color: 0x00e5ff,
        emissive: new THREE.Color(0x00e5ff),
        emissiveIntensity: 0.4,
        roughness: 0.2
      });

      const mesh = new THREE.Mesh(nodeGeo, mat);
      mesh.position.copy(pos);
      this.group.add(mesh);

      this.nodes.push({ id: i, position: pos, mesh, active: true, degree: 0 });
    }

    // 2. Conduits / Edges
    const maxEdges = (nodeCount * (nodeCount - 1)) / 2;
    this.linePositions = new Float32Array(maxEdges * 6);
    const lineGeo = new THREE.BufferGeometry();
    lineGeo.setAttribute('position', new THREE.BufferAttribute(this.linePositions, 3));

    const lineMat = new THREE.LineBasicMaterial({
      color: 0x3b82f6,
      transparent: true,
      opacity: 0.45,
      blending: THREE.AdditiveBlending
    });
    this.edgeLines = new THREE.LineSegments(lineGeo, lineMat);
    this.group.add(this.edgeLines);

    // 3. Routing Data Packets
    const pGeo = new THREE.SphereGeometry(0.2, 8, 8);
    const pMat = new THREE.MeshBasicMaterial({ color: 0xffd700 });
    this.packetMesh = new THREE.InstancedMesh(pGeo, pMat, this.packetCount);
    this.group.add(this.packetMesh);

    this.rebuildTopology();
  }

  public rebuildTopology() {
    let pIdx = 0;
    const n = this.nodes.length;
    for (let i = 0; i < n; i++) {
      for (let j = i + 1; j < n; j++) {
        if (this.nodes[i].active && this.nodes[j].active) {
          const p1 = this.nodes[i].position;
          const p2 = this.nodes[j].position;
          this.linePositions[pIdx++] = p1.x;
          this.linePositions[pIdx++] = p1.y;
          this.linePositions[pIdx++] = p1.z;
          this.linePositions[pIdx++] = p2.x;
          this.linePositions[pIdx++] = p2.y;
          this.linePositions[pIdx++] = p2.z;
        }
      }
    }
    this.edgeLines.geometry.attributes.position.needsUpdate = true;
  }

  public isolateNode(idx: number) {
    if (idx < this.nodes.length) {
      this.nodes[idx].active = false;
      ((this.nodes[idx].mesh.material) as THREE.MeshStandardMaterial).color.set('#ef4444');
      ((this.nodes[idx].mesh.material) as THREE.MeshStandardMaterial).emissive.set('#ef4444');
      this.fiedlerValue = 0.0000;
      this.rebuildTopology();
    }
  }

  public restoreAllNodes() {
    this.nodes.forEach(n => {
      n.active = true;
      ((n.mesh.material) as THREE.MeshStandardMaterial).color.set('#00e5ff');
      ((n.mesh.material) as THREE.MeshStandardMaterial).emissive.set('#00e5ff');
    });
    this.fiedlerValue = 0.3242;
    this.rebuildTopology();
  }

  public update(delta: number) {
    this.group.rotation.y += delta * 0.15;
    const time = performance.now() * 0.001;
    for (let i = 0; i < this.packetCount; i++) {
      const u = i % this.nodes.length;
      const v = (i + 1) % this.nodes.length;
      if (this.nodes[u].active && this.nodes[v].active) {
        const alpha = (time * 0.8 + i / this.packetCount) % 1.0;
        this.dummy.position.lerpVectors(this.nodes[u].position, this.nodes[v].position, alpha);
        this.dummy.updateMatrix();
        this.packetMesh.setMatrixAt(i, this.dummy.matrix);
      }
    }
    this.packetMesh.instanceMatrix.needsUpdate = true;
  }
}
