import { SomaticSolver } from '../core/SomaticSolver';
import { SomaticKinematicFigure } from './SomaticKinematicFigure';

export class SomaticHUD {
  public container: HTMLElement;
  private solver: SomaticSolver;
  private figure: SomaticKinematicFigure;

  private topLedger!: HTMLElement;
  private panelA!: HTMLElement;
  private panelC!: HTMLElement;
  private panelD!: HTMLElement;
  private bottomControls!: HTMLElement;

  private canvasPhase: HTMLCanvasElement;
  private ctxPhase: CanvasRenderingContext2D;
  private canvasTesseract: HTMLCanvasElement;
  private ctxTesseract: CanvasRenderingContext2D;

  private selectedConstraint: number | null = null;
  private blockHeight: number = 84092;

  constructor(solver: SomaticSolver, figure: SomaticKinematicFigure) {
    this.solver = solver;
    this.figure = figure;

    this.container = document.createElement('div');
    this.initLayout();

    this.canvasPhase = this.panelD.querySelector('#canvas-phase') as HTMLCanvasElement;
    this.ctxPhase = this.canvasPhase.getContext('2d')!;

    this.canvasTesseract = this.panelD.querySelector('#canvas-tesseract') as HTMLCanvasElement;
    this.ctxTesseract = this.canvasTesseract.getContext('2d')!;

    document.body.appendChild(this.container);
    this.bindEvents();
  }

  private initLayout() {
    this.container.id = 'somatic-hud';
    this.container.style.position = 'fixed';
    this.container.style.top = '0';
    this.container.style.left = '0';
    this.container.style.width = '100vw';
    this.container.style.height = '100vh';
    this.container.style.pointerEvents = 'none';
    this.container.style.zIndex = '5000';
    this.container.style.display = 'grid';
    this.container.style.gridTemplateRows = '42px 1fr 1fr 48px';
    this.container.style.gridTemplateColumns = '340px 1fr 360px';
    this.container.style.padding = '8px';
    this.container.style.gap = '8px';
    this.container.style.boxSizing = 'border-box';
    this.container.style.fontFamily = 'monospace';
    this.container.style.color = '#f3f4f6';

    // 1. TOP HUD: Lex I Merkle DAG Ledger Stream
    this.topLedger = document.createElement('div');
    this.topLedger.style.gridColumn = '1 / -1';
    this.topLedger.style.background = 'rgba(10, 10, 15, 0.92)';
    this.topLedger.style.border = '1px solid #242436';
    this.topLedger.style.borderRadius = '6px';
    this.topLedger.style.padding = '0 16px';
    this.topLedger.style.display = 'flex';
    this.topLedger.style.alignItems = 'center';
    this.topLedger.style.justifyContent = 'space-between';
    this.topLedger.style.fontSize = '11px';
    this.topLedger.style.pointerEvents = 'auto';
    this.topLedger.innerHTML = `
      <div style="display:flex; align-items:center; gap:12px;">
        <span style="color:#00e5ff; font-weight:bold;">LEX I // MERKLE DAG LEDGER</span>
        <span style="display:inline-flex; align-items:center; gap:6px;">
          <span style="width:7px; height:7px; border-radius:50%; background:#10b981; box-shadow:0 0 8px #10b981;" id="pulse-15hz"></span>
          <span>1.5 Hz PULSE</span>
        </span>
        <span style="color:#9ca3af;" id="ledger-hash">HASH: ad012a7d664681367b...8ffce</span>
      </div>
      <div style="display:flex; gap:16px;">
        <span style="color:#fbbf24;">STRATUM: ASH ARCHIVE</span>
        <span style="color:#a855f7;">BLOCK: #<span id="ledger-block">84092</span></span>
      </div>
    `;

    // 2. PANEL A: Orbital Validation Ring (C1 - C12)
    this.panelA = document.createElement('div');
    this.panelA.style.gridRow = '2';
    this.panelA.style.gridColumn = '1';
    this.panelA.style.background = 'rgba(10, 10, 15, 0.90)';
    this.panelA.style.border = '1px solid #242436';
    this.panelA.style.borderRadius = '6px';
    this.panelA.style.padding = '10px';
    this.panelA.style.pointerEvents = 'auto';
    this.panelA.style.overflowY = 'auto';
    this.panelA.innerHTML = `
      <div style="font-weight:bold; color:#00e5ff; font-size:11px; margin-bottom:6px; border-bottom:1px solid #1f1f2e; padding-bottom:4px; display:flex; justify-content:space-between;">
        <span>PANEL A: ORBITAL VALIDATION RING</span>
        <span style="color:#fbbf24;">12 NODES</span>
      </div>
      <div id="nodes-ring" style="display:grid; grid-template-columns:repeat(3, 1fr); gap:4px; margin-bottom:8px;"></div>
      <div id="node-detail" style="font-size:10px; background:#14141f; border:1px solid #242436; padding:6px; border-radius:4px; line-height:1.4;">
        Click any constraint node to isolate row in Matrix Grid.
      </div>
    `;

    // 3. PANEL C: Matrix Diagnostic Grid (12x11 Heatmap)
    this.panelC = document.createElement('div');
    this.panelC.style.gridRow = '3';
    this.panelC.style.gridColumn = '1';
    this.panelC.style.background = 'rgba(10, 10, 15, 0.90)';
    this.panelC.style.border = '1px solid #242436';
    this.panelC.style.borderRadius = '6px';
    this.panelC.style.padding = '10px';
    this.panelC.style.pointerEvents = 'auto';
    this.panelC.style.overflow = 'hidden';
    this.panelC.innerHTML = `
      <div style="font-weight:bold; color:#00e5ff; font-size:11px; margin-bottom:6px; border-bottom:1px solid #1f1f2e; padding-bottom:4px; display:flex; justify-content:space-between;">
        <span>PANEL C: MOMENTUM COUPLING (M 12x11)</span>
        <span style="color:#9ca3af;">132 CHANNELS</span>
      </div>
      <div id="heatmap-grid" style="display:grid; grid-template-columns:repeat(11, 1fr); gap:2px; height:120px;"></div>
      <div id="channel-readout" style="font-size:10px; color:#9ca3af; margin-top:6px; height:18px;">
        Hover cell to trace energy conduit to kinetic pass.
      </div>
    `;

    // 4. PANEL D: Superposition Phase Space & 4D Tesseract
    this.panelD = document.createElement('div');
    this.panelD.style.gridRow = '2 / 4';
    this.panelD.style.gridColumn = '3';
    this.panelD.style.background = 'rgba(10, 10, 15, 0.90)';
    this.panelD.style.border = '1px solid #242436';
    this.panelD.style.borderRadius = '6px';
    this.panelD.style.padding = '10px';
    this.panelD.style.pointerEvents = 'auto';
    this.panelD.style.display = 'flex';
    this.panelD.style.flexDirection = 'column';
    this.panelD.style.gap = '8px';
    this.panelD.innerHTML = `
      <div style="font-weight:bold; color:#ffd700; font-size:11px; border-bottom:1px solid #1f1f2e; padding-bottom:4px;">
        PANEL D: SUPERPOSITION & TESSERACT
      </div>

      <!-- 2D Loss Phase Diagram -->
      <div style="font-size:10px; color:#9ca3af;">2D LOSS PHASE LANDSCAPE (p vs I)</div>
      <canvas id="canvas-phase" width="330" height="130" style="background:#09090e; border:1px solid #1f1f2e; border-radius:4px;"></canvas>
      <div style="font-size:10px; display:flex; justify-content:space-between;">
        <span>REGIME: <b id="regime-name" style="color:#00e5ff;">Orthogonal</b></span>
        <span>p_c = 0.25</span>
      </div>

      <!-- 4D Hypercube / Tesseract -->
      <div style="font-size:10px; color:#9ca3af; margin-top:4px;">4D TESSERACT VECTOR FRAME (16 BOOLEAN VERTICES)</div>
      <canvas id="canvas-tesseract" width="330" height="140" style="background:#09090e; border:1px solid #1f1f2e; border-radius:4px;"></canvas>
      <div style="font-size:10px; line-height:1.4; background:#14141f; padding:6px; border-radius:4px; border:1px solid #242436;">
        <div>ACTIVE: <span id="w-active" style="color:#00e5ff;">W3</span></div>
        <div>ANTIPODAL: <span id="w-anti" style="color:#ef4444;">W12</span></div>
        <div style="color:#10b981;">ReLU CROSS-TALK: 0.0000 (Canceled)</div>
      </div>
    `;

    // 5. BOTTOM CONTROLS: Sparsity (p) | Importance (I) | Scrubber
    this.bottomControls = document.createElement('div');
    this.bottomControls.style.gridColumn = '1 / -1';
    this.bottomControls.style.background = 'rgba(10, 10, 15, 0.95)';
    this.bottomControls.style.border = '1px solid #242436';
    this.bottomControls.style.borderRadius = '6px';
    this.bottomControls.style.padding = '0 16px';
    this.bottomControls.style.display = 'flex';
    this.bottomControls.style.alignItems = 'center';
    this.bottomControls.style.gap = '20px';
    this.bottomControls.style.pointerEvents = 'auto';
    this.bottomControls.innerHTML = `
      <div style="display:flex; align-items:center; gap:8px; width:220px;">
        <span style="font-size:10px; color:#9ca3af;">SPARSITY (p):</span>
        <input type="range" id="s-p" min="0.0" max="1.0" step="0.02" value="0.15" style="flex:1;">
        <span id="v-p" style="font-size:10px; color:#00e5ff; width:30px;">0.15</span>
      </div>

      <div style="display:flex; align-items:center; gap:8px; width:220px;">
        <span style="font-size:10px; color:#9ca3af;">IMPORTANCE (I):</span>
        <input type="range" id="s-i" min="0.0" max="2.0" step="0.05" value="1.2" style="flex:1;">
        <span id="v-i" style="font-size:10px; color:#ffd700; width:30px;">1.20</span>
      </div>

      <div style="flex:1; display:flex; align-items:center; gap:8px;">
        <span style="font-size:10px; color:#a855f7;">TIMELINE SCRUBBER:</span>
        <input type="range" id="s-scrubber" min="84000" max="84092" value="84092" style="flex:1;">
        <span style="font-size:10px; color:#9ca3af;">LEX I STRATIFIED</span>
      </div>
    `;

    this.container.appendChild(this.topLedger);
    this.container.appendChild(this.panelA);
    this.container.appendChild(this.panelC);
    this.container.appendChild(this.panelD);
    this.container.appendChild(this.bottomControls);
  }

  private bindEvents() {
    // Populate Panel A (Validation Nodes)
    const ring = this.panelA.querySelector('#nodes-ring')!;
    this.solver.constraints.forEach(c => {
      const b = document.createElement('button');
      b.id = `btn-node-${c.id}`;
      b.style.padding = '6px 2px';
      b.style.background = '#171722';
      b.style.border = c.dialetheic ? '1px solid #ef4444' : '1px solid #242436';
      b.style.color = '#f3f4f6';
      b.style.fontSize = '10px';
      b.style.borderRadius = '4px';
      b.style.cursor = 'pointer';
      b.innerText = c.label;
      b.onclick = () => this.selectConstraint(c.id);
      ring.appendChild(b);
    });

    // Populate Panel C (Heatmap)
    const grid = this.panelC.querySelector('#heatmap-grid')!;
    const readout = this.panelC.querySelector('#channel-readout') as HTMLElement;
    for (let i = 0; i < 12; i++) {
      for (let j = 0; j < 11; j++) {
        const cell = document.createElement('div');
        cell.id = `cell-${i}-${j}`;
        cell.style.background = '#1c2233';
        cell.style.borderRadius = '1px';
        cell.style.cursor = 'pointer';
        cell.onmouseenter = () => {
          readout.innerHTML = `<span style="color:#00e5ff;">Channel [${this.solver.constraints[i].label} ⨂ ${this.solver.passes[j].label}]</span> Val: ${this.solver.M[i][j]}`;
          this.figure.drawEnergyConduit(j, true);
        };
        cell.onmouseleave = () => {
          this.figure.drawEnergyConduit(j, false);
        };
        grid.appendChild(cell);
      }
    }

    // Bottom Sliders
    const sP = this.bottomControls.querySelector('#s-p') as HTMLInputElement;
    const vP = this.bottomControls.querySelector('#v-p') as HTMLElement;
    sP.oninput = () => {
      this.solver.sparsity_p = parseFloat(sP.value);
      vP.innerText = sP.value;
    };

    const sI = this.bottomControls.querySelector('#s-i') as HTMLInputElement;
    const vI = this.bottomControls.querySelector('#v-i') as HTMLElement;
    sI.oninput = () => {
      this.solver.importance_I = parseFloat(sI.value);
      vI.innerText = parseFloat(sI.value).toFixed(2);
    };

    const sScrub = this.bottomControls.querySelector('#s-scrubber') as HTMLInputElement;
    sScrub.oninput = () => {
      const b = sScrub.value;
      (this.topLedger.querySelector('#ledger-block') as HTMLElement).innerText = b;
      (this.topLedger.querySelector('#ledger-hash') as HTMLElement).innerText = `REPLAY #${b}: e8a72b...09c`;
    };
  }

  private selectConstraint(id: number) {
    this.selectedConstraint = id;
    const c = this.solver.constraints[id];
    const detail = this.panelA.querySelector('#node-detail') as HTMLElement;
    detail.innerHTML = `
      <div style="font-weight:bold; color:${c.dialetheic ? '#ef4444' : '#00e5ff'};">${c.name}</div>
      <div>Residual r: <span style="color:#ffd700;">${c.error}</span> | Target: ${c.target}</div>
      <div>Row ${c.label} isolated in Matrix C.</div>
    `;

    // Highlight row in Panel C
    for (let i = 0; i < 12; i++) {
      for (let j = 0; j < 11; j++) {
        const cell = document.getElementById(`cell-${i}-${j}`);
        if (cell) {
          cell.style.outline = (i === id) ? '1px solid #00e5ff' : 'none';
        }
      }
    }
  }

  public setVisible(show: boolean) {
    this.container.style.display = show ? 'grid' : 'none';
  }

  public update(time: number) {
    if (this.container.style.display === 'none') return;

    // 1. Update 1.5 Hz pulse indicator
    const pulse15 = (Math.sin(time * 9.42477) * 0.5 + 0.5);
    (this.topLedger.querySelector('#pulse-15hz') as HTMLElement).style.opacity = `${0.3 + pulse15 * 0.7}`;

    // 2. Update Panel A Node Residual Colors
    this.solver.constraints.forEach(c => {
      const b = document.getElementById(`btn-node-${c.id}`);
      if (b) {
        if (c.dialetheic) {
          b.style.borderColor = (Math.abs(c.error) > 0.4) ? '#ef4444' : '#a855f7';
          b.style.boxShadow = (Math.abs(c.error) > 0.4) ? '0 0 8px #ef4444' : 'none';
        } else {
          b.style.borderColor = Math.abs(c.error) < 0.2 ? '#10b981' : '#ffd700';
        }
      }
    });

    // 3. Update Panel C Heatmap intensities
    for (let i = 0; i < 12; i++) {
      for (let j = 0; j < 11; j++) {
        const cell = document.getElementById(`cell-${i}-${j}`);
        if (cell) {
          const val = this.solver.M[i][j];
          const r = Math.round(val * 40);
          const g = Math.round(val * 160);
          const b = Math.round(val * 220);
          cell.style.background = `rgb(${r}, ${g}, ${b})`;
        }
      }
    }

    // 4. Update Panel D: 2D Loss Phase Diagram
    (this.panelD.querySelector('#regime-name') as HTMLElement).innerText = this.solver.phaseRegime;
    this.renderPhaseDiagram();

    // 5. Update Panel D: 4D Tesseract
    this.renderTesseract(time);
  }

  private renderPhaseDiagram() {
    const ctx = this.ctxPhase;
    const w = this.canvasPhase.width;
    const h = this.canvasPhase.height;
    ctx.clearRect(0, 0, w, h);

    // Draw Phase Boundaries (p in, I in [0, 2])
    const pcX = 0.25 * w;
    const pSimplexX = 0.65 * w;

    // Regimes
    ctx.fillStyle = 'rgba(0, 229, 255, 0.08)';
    ctx.fillRect(0, 0, pcX, h);
    ctx.fillStyle = 'rgba(251, 191, 36, 0.08)';
    ctx.fillRect(pcX, 0, pSimplexX - pcX, h);
    ctx.fillStyle = 'rgba(168, 85, 247, 0.08)';
    ctx.fillRect(pSimplexX, 0, w - pSimplexX, h);

    // Critical line pc = 0.25
    ctx.strokeStyle = '#00e5ff';
    ctx.setLineDash([3, 3]);
    ctx.beginPath();
    ctx.moveTo(pcX, 0);
    ctx.lineTo(pcX, h);
    ctx.stroke();
    ctx.setLineDash([]);

    // Live Operating Point Cursor
    const curX = this.solver.sparsity_p * w;
    const curY = h - (this.solver.importance_I / 2.0) * h;

    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(curX, curY, 4.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = '#fff';
    ctx.lineWidth = 1.5;
    ctx.stroke();
  }

  private renderTesseract(time: number) {
    const ctx = this.ctxTesseract;
    const w = this.canvasTesseract.width;
    const h = this.canvasTesseract.height;
    ctx.clearRect(0, 0, w, h);

    const cx = w / 2;
    const cy = h / 2;

    // 4D Rotation Angles
    const a = time * 0.6;
    const b = time * 0.4;

    const projected: [number, number][] = [];

    // Project 16 vertices from 4D -> 3D -> 2D
    for (let i = 0; i < 16; i++) {
      let [x, y, z, w4] = this.solver.hypercubeVertices[i];

      // Rotate in XW and YZ planes
      const cosA = Math.cos(a), sinA = Math.sin(a);
      const x1 = x * cosA - w4 * sinA;
      const w1 = x * sinA + w4 * cosA;

      const cosB = Math.cos(b), sinB = Math.sin(b);
      const y1 = y * cosB - z * sinB;
      const z1 = y * sinB + z * cosB;

      // 4D perspective projection
      const d = 3.0;
      const f = 1.0 / (d - w1);
      const px = cx + x1 * f * 120.0;
      const py = cy + y1 * f * 120.0;
      projected.push([px, py]);
    }

    // Draw Edges (Vertices differing by 1 bit in 4D)
    ctx.strokeStyle = 'rgba(59, 130, 246, 0.4)';
    ctx.lineWidth = 1.0;
    for (let i = 0; i < 16; i++) {
      for (let bit = 0; bit < 4; bit++) {
        const j = i ^ (1 << bit);
        if (j > i) {
          ctx.beginPath();
          ctx.moveTo(projected[i][0], projected[i][1]);
          ctx.lineTo(projected[j][0], projected[j][1]);
          ctx.stroke();
        }
      }
    }

    // Highlight Vector W_k and its Antipodal Pair W_{15-k}
    const k = this.solver.selectedVector;
    const antiK = this.solver.getAntipodalVector(k);

    // Vector W_k (Cyan)
    ctx.fillStyle = '#00e5ff';
    ctx.beginPath();
    ctx.arc(projected[k][0], projected[k][1], 5, 0, Math.PI * 2);
    ctx.fill();

    // Antipodal Vector -W_k (Red)
    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(projected[antiK][0], projected[antiK][1], 5, 0, Math.PI * 2);
    ctx.fill();
  }
}
