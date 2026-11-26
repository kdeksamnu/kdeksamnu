import * as THREE from 'three';
import { Crucible } from './Crucible';
import { LabEnvironment } from './LabEnvironment';
import { SPHFluid } from './SPHFluid';
import { DualCoreCollider } from './DualCoreCollider';
import { CymaticsAudio } from '../core/CymaticsAudio';
import { AetherAtelier } from './AetherAtelier';
import { ComputeLoom } from './ComputeLoom';
import { CathedralMaze } from './CathedralMaze';
import { PlayerController } from './PlayerController';
import { RPGEngine } from './RPGEngine';
import { TextToImageCanvas } from './TextToImageCanvas';
import { PaintBrushCursor } from './PaintBrushCursor';
import { Viewport } from '../core/Viewport';
import { GlobalUniforms } from '../shaders/masterShader';
import { ELEMENTS_119, Element119 } from '../data/elements119';

export class ControlDeck {
  private panel: HTMLElement;
  private crucible: Crucible;
  private lab: LabEnvironment;
  private fluid: SPHFluid;
  private collider: DualCoreCollider;
  private audio: CymaticsAudio;
  private atelier: AetherAtelier;
  private loom: ComputeLoom;
  private maze: CathedralMaze;
  private player: PlayerController;
  private rpg: RPGEngine;
  private t2i: TextToImageCanvas;
  private brush: PaintBrushCursor;
  private viewport: Viewport;

  private selectedElement: Element119 = ELEMENTS_119[0];

  constructor(
    crucible: Crucible,
    lab: LabEnvironment,
    fluid: SPHFluid,
    collider: DualCoreCollider,
    audio: CymaticsAudio,
    atelier: AetherAtelier,
    loom: ComputeLoom,
    maze: CathedralMaze,
    player: PlayerController,
    rpg: RPGEngine,
    t2i: TextToImageCanvas,
    brush: PaintBrushCursor,
    viewport: Viewport
  ) {
    this.crucible = crucible;
    this.lab = lab;
    this.fluid = fluid;
    this.collider = collider;
    this.audio = audio;
    this.atelier = atelier;
    this.loom = loom;
    this.maze = maze;
    this.player = player;
    this.rpg = rpg;
    this.t2i = t2i;
    this.brush = brush;
    this.viewport = viewport;

    this.panel = document.createElement('div');
    this.initStyle();
    this.renderUI();
    document.body.appendChild(this.panel);
  }

  private initStyle() {
    this.panel.style.position = 'absolute';
    this.panel.style.top = '10px';
    this.panel.style.right = '10px';
    this.panel.style.width = '350px';
    this.panel.style.background = 'rgba(10, 10, 15, 0.95)';
    this.panel.style.backdropFilter = 'blur(16px)';
    this.panel.style.border = '1px solid #242436';
    this.panel.style.borderRadius = '8px';
    this.panel.style.padding = '12px';
    this.panel.style.color = '#f3f4f6';
    this.panel.style.fontFamily = 'monospace';
    this.panel.style.fontSize = '12px';
    this.panel.style.zIndex = '1000';
    this.panel.style.boxShadow = '0 8px 32px rgba(0,0,0,0.9)';
    this.panel.style.maxHeight = 'calc(100vh - 20px)';
    this.panel.style.overflowY = 'auto';
  }

  private renderUI() {
    this.panel.innerHTML = `
      <div style="font-weight:bold; color:#00e5ff; letter-spacing:0.08em; margin-bottom:8px; border-bottom:1px solid #242436; padding-bottom:4px; display:flex; justify-content:space-between;">
        <span>MLAOS // MASTER ATELIER</span>
        <span style="font-size:10px; color:#ffd700;">PAINT & T2I</span>
      </div>

      <!-- SYSTEM PARADIGMS (4 TABS) -->
      <div style="margin-bottom:8px;">
        <div style="color:#9ca3af; font-size:10px; margin-bottom:3px;">SYSTEM PARADIGM</div>
        <div style="display:grid; grid-template-columns:repeat(4, 1fr); gap:3px;">
          <button id="btn-env-lab" class="active" style="padding:5px 2px; background:#1c1c28; border:1px solid #00e5ff; color:#00e5ff; border-radius:4px; cursor:pointer;">⚗ Lab</button>
          <button id="btn-env-aether" style="padding:5px 2px; background:#171722; border:1px solid #242436; color:#9ca3af; border-radius:4px; cursor:pointer;">🏛️ Atelier</button>
          <button id="btn-env-maze" style="padding:5px 2px; background:#171722; border:1px solid #a855f7; color:#a855f7; border-radius:4px; cursor:pointer;">🏰 Maze</button>
          <button id="btn-env-canvas" style="padding:5px 2px; background:#171722; border:1px solid #ffd700; color:#ffd700; border-radius:4px; cursor:pointer;">🎨 Canvas</button>
        </div>
      </div>

      <!-- PAINT BRUSH PIGMENT PALETTE -->
      <div style="background:#13131e; border:1px solid #242436; border-radius:6px; padding:8px; margin-bottom:8px;">
        <div style="color:#ffd700; font-weight:bold; font-size:11px; margin-bottom:4px;">PAINT BRUSH PIGMENT</div>
        <div id="palette-brush" style="display:grid; grid-template-columns:repeat(7,1fr); gap:3px; margin-bottom:6px;"></div>
        <div style="display:flex; justify-content:space-between; font-size:10px;">
          <span>Brush Size:</span><span id="v-deck-brush">18 px</span>
        </div>
        <input type="range" id="s-deck-brush" min="4" max="48" value="18" style="width:100%;">
      </div>

      <!-- MASTER TEXTURE & LIGHTING CONTROLS -->
      <div style="background:#13131e; border:1px solid #242436; border-radius:6px; padding:8px; margin-bottom:8px;">
        <div style="color:#00e5ff; font-weight:bold; font-size:11px; margin-bottom:4px;">TEXTURE & SHADING CONTROLS</div>

        <div style="display:flex; justify-content:space-between; font-size:10px;"><span>32-bit Bayer Dither:</span><span id="v-bayer">2.0</span></div>
        <input type="range" id="s-bayer" min="1.0" max="8.0" step="0.5" value="2.0" style="width:100%; margin-bottom:4px;">

        <div style="display:flex; justify-content:space-between; font-size:10px;"><span>Chiaroscuro Cut:</span><span id="v-cut">0.35</span></div>
        <input type="range" id="s-cut" min="0.0" max="1.0" step="0.05" value="0.35" style="width:100%; margin-bottom:4px;">

        <div style="display:flex; justify-content:space-between; font-size:10px;"><span>Arterial Vein Glow:</span><span id="v-vglow">1.6</span></div>
        <input type="range" id="s-vglow" min="0.0" max="3.0" step="0.1" value="1.6" style="width:100%;">
      </div>

      <!-- AUDIO & IGNITE -->
      <div style="display:flex; gap:4px;">
        <button id="btn-audio-toggle" style="flex:1; padding:6px; font-size:10px; background:#171722; border:1px solid #fbbf24; color:#fbbf24; border-radius:4px; cursor:pointer;">🔊 AUDIO: OFF</button>
        <button id="btn-pulse" style="padding:6px 12px; background:#1c2d3a; border:1px solid #00e5ff; color:#00e5ff; font-weight:bold; border-radius:4px; cursor:pointer;">⚡ IGNITE</button>
      </div>
    `;

    // 1. Paradigms
    const btnLab = this.panel.querySelector('#btn-env-lab') as HTMLButtonElement;
    const btnAether = this.panel.querySelector('#btn-env-aether') as HTMLButtonElement;
    const btnMaze = this.panel.querySelector('#btn-env-maze') as HTMLButtonElement;
    const btnCanvas = this.panel.querySelector('#btn-env-canvas') as HTMLButtonElement;

    const setMode = (activeBtn: HTMLElement) => {
      [btnLab, btnAether, btnMaze, btnCanvas].forEach(b => {
        b.style.borderColor = '#242436';
        b.style.color = '#9ca3af';
        b.style.background = '#171722';
      });
      activeBtn.style.borderColor = '#00e5ff';
      activeBtn.style.color = '#00e5ff';
      activeBtn.style.background = '#1c1c28';
    };

    btnLab.onclick = () => {
      setMode(btnLab);
      this.crucible.mesh.visible = true;
      this.lab.group.visible = true;
      this.atelier.mesh.visible = false;
      this.loom.mesh.visible = false;
      this.maze.group.visible = false;
      this.rpg.setVisible(false);
      this.t2i.setVisible(false);
      this.viewport.controls.enabled = true;
    };

    btnAether.onclick = () => {
      setMode(btnAether);
      this.atelier.mesh.visible = true;
      this.loom.mesh.visible = true;
      this.crucible.mesh.visible = false;
      this.fluid.mesh.visible = false;
      this.lab.group.visible = false;
      this.collider.group.visible = false;
      this.maze.group.visible = false;
      this.rpg.setVisible(false);
      this.t2i.setVisible(false);
      this.viewport.controls.enabled = true;
    };

    btnMaze.onclick = () => {
      setMode(btnMaze);
      this.maze.group.visible = true;
      this.rpg.setVisible(true);
      this.crucible.mesh.visible = false;
      this.fluid.mesh.visible = false;
      this.lab.group.visible = false;
      this.collider.group.visible = false;
      this.atelier.mesh.visible = false;
      this.loom.mesh.visible = false;
      this.t2i.setVisible(false);
      this.viewport.controls.enabled = false;
    };

    btnCanvas.onclick = () => {
      setMode(btnCanvas);
      this.t2i.setVisible(true);
    };

    // 2. Pigment Palette for Paint Brush Cursor
    const elements = [
      { name: 'Joy (Gold)', hex: '#ffd700' },
      { name: 'Curiosity (Teal)', hex: '#00e5ff' },
      { name: 'Sorrow (Blue)', hex: '#2563eb' },
      { name: 'Anger (Red)', hex: '#ef4444' },
      { name: 'Fear (Violet)', hex: '#8b5cf6' },
      { name: 'Love (Emerald)', hex: '#10b981' },
      { name: 'Obsidian (Null)', hex: '#78350f' }
    ];

    const rack = this.panel.querySelector('#palette-brush')!;
    elements.forEach(e => {
      const b = document.createElement('button');
      b.style.background = e.hex;
      b.style.border = '1px solid #242436';
      b.style.height = '18px';
      b.style.borderRadius = '3px';
      b.style.cursor = 'pointer';
      b.title = e.name;
      b.onclick = () => {
        this.brush.setColor(e.hex);
        GlobalUniforms.uColorPrimary.value.set(e.hex);
      };
      rack.appendChild(b);
    });

    const sBrush = this.panel.querySelector('#s-deck-brush') as HTMLInputElement;
    const vBrush = this.panel.querySelector('#v-deck-brush') as HTMLElement;
    sBrush.oninput = () => {
      const sz = parseInt(sBrush.value);
      vBrush.innerText = `${sz} px`;
      this.brush.setSize(sz);
    };

    // 3. Project Canvas Texture to 3D Models
    document.addEventListener('click', (ev) => {
      const target = ev.target as HTMLElement;
      if (target && target.id === 'btn-project-texture') {
        const tex = this.t2i.texture;
        // Project onto Crucible specimen
        (this.crucible.mesh.material as any).map = tex;
        (this.crucible.mesh.material as any).needsUpdate = true;

        // Project onto Maze walls
        (this.maze.wallMesh.material as any).map = tex;
        (this.maze.wallMesh.material as any).needsUpdate = true;

        target.innerText = '✓ TEXTURE PROJECTED TO 3D';
        setTimeout(() => { target.innerText = '✨ PROJECT AS 3D TEXTURE / SKIN'; }, 2000);
      }
    });

    // 4. Sliders
    const bind = (id: string, lbl: string, fn: (v: number) => void) => {
      const i = this.panel.querySelector(id) as HTMLInputElement;
      const l = this.panel.querySelector(lbl) as HTMLElement;
      i.oninput = () => { l.innerText = i.value; fn(parseFloat(i.value)); };
    };

    bind('#s-bayer', '#v-bayer', (v) => GlobalUniforms.uBayerScale.value = v);
    bind('#s-cut', '#v-cut', (v) => GlobalUniforms.uChiaroscuroCut.value = v);
    bind('#s-vglow', '#v-vglow', (v) => GlobalUniforms.uVeinGlow.value = v);

    // Audio & Pulse
    const btnAudio = this.panel.querySelector('#btn-audio-toggle') as HTMLButtonElement;
    btnAudio.onclick = () => {
      const on = this.audio.toggle();
      btnAudio.innerText = on ? '🔊 AUDIO: ON' : '🔊 AUDIO: OFF';
      btnAudio.style.borderColor = on ? '#10b981' : '#fbbf24';
      btnAudio.style.color = on ? '#10b981' : '#fbbf24';
    };

    (this.panel.querySelector('#btn-pulse') as HTMLElement).onclick = () => {
      this.crucible.pulse();
      this.audio.triggerImpact();
    };
  }
}
