import * as THREE from 'three';
import { PaintBrushCursor } from './PaintBrushCursor';

export class TextToImageCanvas {
  public canvas: HTMLCanvasElement;
  public ctx: CanvasRenderingContext2D;
  public texture: THREE.CanvasTexture;
  public container: HTMLElement;
  public brush: PaintBrushCursor;

  private isDrawing: boolean = false;
  private lastX: number = 0;
  private lastY: number = 0;
  public promptText: string = 'Obsidian cathedral with gold veins and cyan plasma eye in void';

  constructor(brush: PaintBrushCursor) {
    this.brush = brush;
    this.canvas = document.createElement('canvas');
    this.canvas.width = 512;
    this.canvas.height = 512;
    this.ctx = this.canvas.getContext('2d')!;

    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.wrapS = THREE.RepeatWrapping;
    this.texture.wrapT = THREE.RepeatWrapping;

    this.container = document.createElement('div');
    this.initUI();
    this.bindDrawing();

    // Initial synthesis
    this.generateFromPrompt(this.promptText);
  }

  private initUI() {
    this.container.id = 't2i-studio';
    this.container.style.position = 'fixed';
    this.container.style.bottom = '14px';
    this.container.style.left = '14px';
    this.container.style.width = '320px';
    this.container.style.background = 'rgba(10, 10, 15, 0.95)';
    this.container.style.backdropFilter = 'blur(16px)';
    this.container.style.border = '1px solid #242436';
    this.container.style.borderRadius = '8px';
    this.container.style.padding = '10px';
    this.container.style.zIndex = '6000';
    this.container.style.display = 'none';
    this.container.style.flexDirection = 'column';
    this.container.style.gap = '8px';
    this.container.style.fontFamily = 'monospace';
    this.container.style.color = '#f3f4f6';
    this.container.style.boxShadow = '0 12px 40px rgba(0,0,0,0.85)';

    this.container.innerHTML = `
      <div style="font-weight:bold; color:#00e5ff; font-size:11px; display:flex; justify-content:space-between; border-bottom:1px solid #1f1f2e; padding-bottom:4px;">
        <span>🎨 TEXT-TO-IMAGE ALCHEMICAL CANVAS</span>
        <span style="color:#ffd700;">CC-Ω ENGINE</span>
      </div>

      <!-- Canvas Display Box -->
      <div style="position:relative; width:100%; height:200px; background:#07080c; border:1px solid #242436; border-radius:4px; overflow:hidden;">
        <canvas id="active-canvas" width="512" height="512" style="width:100%; height:100%; cursor:crosshair;"></canvas>
      </div>

      <!-- Live Prompt Input -->
      <div>
        <div style="font-size:9px; color:#9ca3af; margin-bottom:2px;">SYNTHESIS PROMPT (LITHOGRAPHIC PARSER)</div>
        <input type="text" id="t2i-input" value="${this.promptText}" style="width:100%; background:#161622; border:1px solid #242436; color:#00e5ff; font-size:10px; border-radius:4px; padding:6px; box-sizing:border-box;">
      </div>

      <!-- Brush Controls -->
      <div style="display:flex; justify-content:space-between; align-items:center; font-size:10px;">
        <span>Brush Size:</span>
        <input type="range" id="s-brush-size" min="4" max="48" value="18" style="width:120px;">
        <button id="btn-clear-canvas" style="padding:2px 8px; background:#1c1c28; border:1px solid #242436; color:#9ca3af; border-radius:3px; cursor:pointer;">Clear</button>
      </div>

      <!-- 3D Texture Projector Button -->
      <button id="btn-project-texture" style="width:100%; padding:7px; background:#1c2d3a; border:1px solid #00e5ff; color:#00e5ff; font-weight:bold; border-radius:4px; cursor:pointer; font-size:10px;">
        ✨ PROJECT AS 3D TEXTURE / SKIN
      </button>
    `;

    document.body.appendChild(this.container);

    const activeCanvas = this.container.querySelector('#active-canvas') as HTMLCanvasElement;
    this.canvas = activeCanvas;
    this.ctx = this.canvas.getContext('2d')!;
    this.texture = new THREE.CanvasTexture(this.canvas);
    this.texture.wrapS = THREE.RepeatWrapping;
    this.texture.wrapT = THREE.RepeatWrapping;

    // Prompt Live Input Handler
    const input = this.container.querySelector('#t2i-input') as HTMLInputElement;
    input.oninput = () => {
      this.promptText = input.value;
      this.generateFromPrompt(this.promptText);
    };

    const sSize = this.container.querySelector('#s-brush-size') as HTMLInputElement;
    sSize.oninput = () => {
      this.brush.setSize(parseInt(sSize.value));
    };

    (this.container.querySelector('#btn-clear-canvas') as HTMLButtonElement).onclick = () => {
      this.generateFromPrompt(this.promptText);
    };
  }

  public setVisible(show: boolean) {
    this.container.style.display = show ? 'flex' : 'none';
  }

  /// Procedural Semantic Latent Synthesizer (CC-Ω Prompt Engine)
  public generateFromPrompt(prompt: string) {
    const ctx = this.ctx;
    const w = this.canvas.width;
    const h = this.canvas.height;
    const p = prompt.toLowerCase();

    // 1. Base Obsidian Void Substrate
    ctx.fillStyle = '#06070a';
    ctx.fillRect(0, 0, w, h);

    // 2. Determine Primary & Secondary Colors from prompt
    let colA = '#00e5ff'; // Cyan default
    let colB = '#ffd700'; // Gold default
    if (p.includes('violet') || p.includes('fear')) colA = '#8b5cf6';
    if (p.includes('red') || p.includes('anger') || p.includes('pyre')) colA = '#ef4444';
    if (p.includes('emerald') || p.includes('green') || p.includes('love')) colA = '#10b981';
    if (p.includes('blue') || p.includes('sorrow')) colA = '#2563eb';
    if (p.includes('obsidian') || p.includes('void')) colB = '#3b1d0d';

    // 3. Volumetric Fog / Plasma Nebula
    const grad = ctx.createRadialGradient(w / 2, h / 2, 20, w / 2, h / 2, w / 1.5);
    grad.addColorStop(0, colA);
    grad.addColorStop(0.5, colB);
    grad.addColorStop(1, 'rgba(6, 7, 10, 0)');
    ctx.globalAlpha = 0.45;
    ctx.fillStyle = grad;
    ctx.fillRect(0, 0, w, h);
    ctx.globalAlpha = 1.0;

    // 4. Gothic Colonnade / Monolith Architecture
    if (p.includes('cathedral') || p.includes('monolith') || p.includes('pillar') || p.includes('tower')) {
      ctx.fillStyle = 'rgba(12, 14, 20, 0.9)';
      const pillarCount = 6;
      const pw = w / (pillarCount * 2);
      for (let i = 0; i < pillarCount; i++) {
        const x = i * (pw * 2) + pw / 2;
        ctx.fillRect(x, 40, pw, h - 80);
      }
    }

    // 5. Central Aperture / Plasma Eye / Mandala
    if (p.includes('eye') || p.includes('portal') || p.includes('aperture') || p.includes('mandala')) {
      for (let r = 140; r > 20; r -= 25) {
        ctx.strokeStyle = r % 50 === 0 ? colB : colA;
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(w / 2, h / 2, r, 0, Math.PI * 2);
        ctx.stroke();
      }
    }

    // 6. Arterial Vein Crack Network (Kintsugi Gold / Void)
    if (p.includes('vein') || p.includes('crack') || p.includes('scar') || p.includes('kintsugi') || true) {
      ctx.strokeStyle = colB;
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      for (let i = 0; i < 8; i++) {
        let vx = Math.random() * w;
        let vy = Math.random() * h;
        ctx.moveTo(vx, vy);
        for (let seg = 0; seg < 5; seg++) {
          vx += (Math.random() - 0.5) * 80;
          vy += (Math.random() - 0.5) * 80;
          ctx.lineTo(vx, vy);
        }
      }
      ctx.stroke();
    }

    this.texture.needsUpdate = true;
  }

  private bindDrawing() {
    this.canvas.addEventListener('mousedown', (e) => {
      this.isDrawing = true;
      const rect = this.canvas.getBoundingClientRect();
      this.lastX = ((e.clientX - rect.left) / rect.width) * this.canvas.width;
      this.lastY = ((e.clientY - rect.top) / rect.height) * this.canvas.height;
    });

    window.addEventListener('mouseup', () => {
      this.isDrawing = false;
    });

    this.canvas.addEventListener('mousemove', (e) => {
      if (!this.isDrawing) return;
      const rect = this.canvas.getBoundingClientRect();
      const curX = ((e.clientX - rect.left) / rect.width) * this.canvas.width;
      const curY = ((e.clientY - rect.top) / rect.height) * this.canvas.height;

      const ctx = this.ctx;
      ctx.strokeStyle = this.brush.brushColor;
      ctx.lineWidth = this.brush.brushSize * 1.5;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.shadowColor = this.brush.brushColor;
      ctx.shadowBlur = 10;

      ctx.beginPath();
      ctx.moveTo(this.lastX, this.lastY);
      ctx.lineTo(curX, curY);
      ctx.stroke();

      this.lastX = curX;
      this.lastY = curY;
      this.texture.needsUpdate = true;
    });
  }
}
