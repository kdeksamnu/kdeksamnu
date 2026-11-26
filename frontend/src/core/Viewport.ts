import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

export class Viewport {
  public scene: THREE.Scene;
  public camera: THREE.PerspectiveCamera;
  public controls: OrbitControls;
  public renderer: THREE.WebGLRenderer;
  private container: HTMLElement;

  constructor(containerId: string) {
    this.container = document.getElementById(containerId) || document.body;
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07070a);

    this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
    this.camera.position.set(20, 24, 28);
    this.camera.lookAt(0, 0, 0);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.container.appendChild(this.renderer.domElement);

    this.controls = new OrbitControls(this.camera, this.renderer.domElement);
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;

    // Ambient scene fill
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.4));

    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  public render(updateFn?: (delta: number) => void) {
    let lastTime = performance.now();
    const animate = (time: number) => {
      requestAnimationFrame(animate);
      const delta = (time - lastTime) * 0.001;
      lastTime = time;
      this.controls.update();
      if (updateFn) updateFn(delta);
      this.renderer.render(this.scene, this.camera);
    };
    requestAnimationFrame(animate);
  }
}
