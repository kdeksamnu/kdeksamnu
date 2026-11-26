import { Viewport } from './core/Viewport';
import { Crucible } from './components/Crucible';
import { LabEnvironment } from './components/LabEnvironment';
import { SPHFluid } from './components/SPHFluid';
import { DualCoreCollider } from './components/DualCoreCollider';
import { Dimension8Mesh } from './components/Dimension8Mesh';
import { CymaticsAudio } from './core/CymaticsAudio';
import { AetherAtelier } from './components/AetherAtelier';
import { ComputeLoom } from './components/ComputeLoom';
import { CathedralMaze } from './components/CathedralMaze';
import { PlayerController } from './components/PlayerController';
import { RPGEngine } from './components/RPGEngine';
import { TextToImageCanvas } from './components/TextToImageCanvas';
import { PaintBrushCursor } from './components/PaintBrushCursor';
import { SomaticSolver } from './core/SomaticSolver';
import { SomaticKinematicFigure } from './components/SomaticKinematicFigure';
import { SomaticHUD } from './components/SomaticHUD';
import { MythotechnicalWidget } from './components/MythotechnicalWidget';
import { HUD } from './components/HUD';
import { ControlDeck } from './components/ControlDeck';
import { GlobalUniforms } from './shaders/masterShader';

const viewport = new Viewport('canvas-container');
viewport.camera.position.set(0, 10, 24);
viewport.controls.target.set(0, 5, 0);
viewport.controls.update();

// Classical Subsystems
const lab = new LabEnvironment();
const crucible = new Crucible();
const fluid = new SPHFluid();
const collider = new DualCoreCollider();
const dim8Mesh = new Dimension8Mesh(8, 19.0);
const audio = new CymaticsAudio();

const atelier = new AetherAtelier();
const loom = new ComputeLoom();

const maze = new CathedralMaze();
const player = new PlayerController(maze, viewport.camera);
const rpg = new RPGEngine(maze, player, audio);

// Somatic Engine Subsystems
const somaticSolver = new SomaticSolver();
const somaticFigure = new SomaticKinematicFigure();
const somaticHUD = new SomaticHUD(somaticSolver, somaticFigure);

// Mythotechnical Widget v2.4
const widget = new MythotechnicalWidget(viewport, somaticSolver);

// Paint Brush & Live T2I Studio
const brush = new PaintBrushCursor();
const t2i = new TextToImageCanvas(brush);

viewport.scene.add(somaticFigure.group);
viewport.scene.add(atelier.mesh);
viewport.scene.add(loom.mesh);
viewport.scene.add(lab.group);
viewport.scene.add(crucible.mesh);
viewport.scene.add(fluid.mesh);
viewport.scene.add(collider.group);
viewport.scene.add(dim8Mesh.group);
viewport.scene.add(maze.group);

// Focus on Somatic Manifold initially
lab.group.visible = false;
crucible.mesh.visible = false;

new HUD('hud');
new ControlDeck(crucible, lab, fluid, collider, audio, atelier, loom, maze, player, rpg, t2i, brush, viewport);

viewport.render((delta) => {
  const time = performance.now() * 0.001;
  GlobalUniforms.uTime.value += delta;

  // 60 FPS Closed-Loop Feedback
  somaticSolver.step(time);
  somaticFigure.update(delta, somaticSolver);
  somaticHUD.update(time);

  // Background systems
  atelier.update(delta, brush.mouseX, brush.mouseY);
  loom.update(delta);
  brush.update();
  maze.update(delta);
  player.update(delta);
  rpg.update(delta);
});
