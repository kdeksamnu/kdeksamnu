import { CathedralMaze } from './CathedralMaze';
import { PlayerController } from './PlayerController';
import { CymaticsAudio } from '../core/CymaticsAudio';

export class RPGEngine {
  public somaticIntegrity: number = 100;
  public maxSomatic: number = 100;
  public egoDensity: number = 100;
  public maxEgo: number = 100;
  public rank: string = 'Tier I: Neophyte Weaver';
  public xp: number = 0;
  public harmonicScars: number = 0;
  public shardsCollected: number = 0;
  public totalShards: number = 0;

  private maze: CathedralMaze;
  private player: PlayerController;
  private audio: CymaticsAudio;

  public hudContainer: HTMLElement;
  private mapCanvas: HTMLCanvasElement;
  private mapCtx: CanvasRenderingContext2D;
  private discovered: boolean[][] = [];

  constructor(maze: CathedralMaze, player: PlayerController, audio: CymaticsAudio) {
    this.maze = maze;
    this.player = player;
    this.audio = audio;
    this.totalShards = maze.relics.length;

    this.discovered = Array.from({ length: maze.height }, () => Array(maze.width).fill(false));

    this.hudContainer = document.createElement('div');
    this.mapCanvas = document.createElement('canvas');
    this.mapCtx = this.mapCanvas.getContext('2d')!;

    this.initHUD();
  }

  private initHUD() {
    this.hudContainer.style.position = 'fixed';
    this.hudContainer.style.top = '12px';
    this.hudContainer.style.left = '12px';
    this.hudContainer.style.display = 'none';
    this.hudContainer.style.flexDirection = 'column';
    this.hudContainer.style.gap = '8px';
    this.hudContainer.style.zIndex = '9000';
    this.hudContainer.style.fontFamily = 'monospace';
    this.hudContainer.style.color = '#f3f4f6';

    this.hudContainer.innerHTML = `
      <!-- SOMATIC HEALTH & ENERGY BARS -->
      <div style="background:rgba(10,10,15,0.92); border:1px solid #242436; border-radius:6px; padding:10px 12px; width:260px; box-shadow:0 8px 32px rgba(0,0,0,0.8);">
        <div style="font-size:10px; color:#00e5ff; font-weight:bold; margin-bottom:4px; display:flex; justify-content:space-between;">
          <span id="rpg-rank">Tier I: Neophyte Weaver</span>
          <span id="rpg-shards" style="color:#ffd700;">0 / 12 Shards</span>
        </div>

        <div style="font-size:9px; color:#9ca3af; margin-bottom:2px; display:flex; justify-content:space-between;">
          <span>SOMATIC INTEGRITY (HP)</span>
          <span id="hp-val">100 / 100</span>
        </div>
        <div style="height:6px; background:#1c1c28; border-radius:3px; overflow:hidden; margin-bottom:6px;">
          <div id="hp-bar" style="width:100%; height:100%; background:linear-gradient(90deg, #ef4444, #a855f7); transition:width 0.2s;"></div>
        </div>

        <div style="font-size:9px; color:#9ca3af; margin-bottom:2px; display:flex; justify-content:space-between;">
          <span>EGO DENSITY (MANA)</span>
          <span id="ego-val">100 / 100</span>
        </div>
        <div style="height:6px; background:#1c1c28; border-radius:3px; overflow:hidden; margin-bottom:4px;">
          <div id="ego-bar" style="width:100%; height:100%; background:linear-gradient(90deg, #00e5ff, #3b82f6); transition:width 0.2s;"></div>
        </div>

        <div style="font-size:9px; color:#9ca3af; display:flex; justify-content:space-between; margin-top:4px;">
          <span>CONTROLS: WASD to Move</span>
          <span style="color:#00e5ff;">[V] Camera Mode</span>
        </div>
      </div>
    `;

    // Mini-map Radar Canvas
    this.mapCanvas.width = 140;
    this.mapCanvas.height = 140;
    this.mapCanvas.style.background = 'rgba(7, 7, 12, 0.94)';
    this.mapCanvas.style.border = '1px solid #242436';
    this.mapCanvas.style.borderRadius = '6px';
    this.mapCanvas.style.boxShadow = '0 8px 24px rgba(0,0,0,0.85)';

    this.hudContainer.appendChild(this.mapCanvas);
    document.body.appendChild(this.hudContainer);
  }

  public setVisible(show: boolean) {
    this.hudContainer.style.display = show ? 'flex' : 'none';
  }

  public update(delta: number) {
    if (this.hudContainer.style.display === 'none') return;

    // 1. Check Relic Collision
    const px = this.player.position.x;
    const pz = this.player.position.z;

    this.maze.relics.forEach(r => {
      if (!r.collected) {
        const dx = r.x - px;
        const dz = r.z - pz;
        if (dx * dx + dz * dz < 2.8) {
          r.collected = true;
          r.mesh.visible = false;
          this.shardsCollected++;
          this.xp += 150;
          this.somaticIntegrity = Math.min(this.maxSomatic, this.somaticIntegrity + 20);
          this.egoDensity = Math.min(this.maxEgo, this.egoDensity + 25);
          this.audio.triggerImpact();

          if (this.shardsCollected >= 4 && this.rank.includes('Neophyte')) {
            this.rank = 'Tier II: Adept Weaver';
            this.harmonicScars += 2;
          } else if (this.shardsCollected >= 8 && this.rank.includes('Adept')) {
            this.rank = 'Tier III: Arch-Weaver';
            this.harmonicScars += 3;
          }
          this.updateHUD();
        }
      }
    });

    // 2. Discover Fog-of-War
    const halfW = (this.maze.width * this.maze.cellSize) / 2;
    const halfH = (this.maze.height * this.maze.cellSize) / 2;
    const curCol = Math.floor((px + halfW) / this.maze.cellSize);
    const curRow = Math.floor((pz + halfH) / this.maze.cellSize);

    for (let dy = -2; dy <= 2; dy++) {
      for (let dx = -2; dx <= 2; dx++) {
        const nx = curCol + dx;
        const ny = curRow + dy;
        if (nx >= 0 && nx < this.maze.width && ny >= 0 && ny < this.maze.height) {
          this.discovered[ny][nx] = true;
        }
      }
    }

    // 3. Render Mini-Map
    this.renderMiniMap(curCol, curRow, px, pz);
  }

  private updateHUD() {
    (this.hudContainer.querySelector('#rpg-rank') as HTMLElement).innerText = this.rank;
    (this.hudContainer.querySelector('#rpg-shards') as HTMLElement).innerText = `${this.shardsCollected} / ${this.totalShards} Shards`;
    (this.hudContainer.querySelector('#hp-val') as HTMLElement).innerText = `${this.somaticIntegrity} / ${this.maxSomatic}`;
    (this.hudContainer.querySelector('#hp-bar') as HTMLElement).style.width = `${(this.somaticIntegrity / this.maxSomatic) * 100}%`;
    (this.hudContainer.querySelector('#ego-val') as HTMLElement).innerText = `${this.egoDensity} / ${this.maxEgo}`;
    (this.hudContainer.querySelector('#ego-bar') as HTMLElement).style.width = `${(this.egoDensity / this.maxEgo) * 100}%`;
  }

  private renderMiniMap(curCol: number, curRow: number, px: number, pz: number) {
    const ctx = this.mapCtx;
    const w = this.mapCanvas.width;
    const h = this.mapCanvas.height;
    ctx.clearRect(0, 0, w, h);

    const cellPixel = w / this.maze.width;

    // Draw Discovered Maze Cells
    for (let y = 0; y < this.maze.height; y++) {
      for (let x = 0; x < this.maze.width; x++) {
        if (this.discovered[y][x]) {
          if (this.maze.grid[y][x] === 1) {
            ctx.fillStyle = '#1e2433'; // Walls
            ctx.fillRect(x * cellPixel, y * cellPixel, cellPixel, cellPixel);
          } else {
            ctx.fillStyle = '#0f1118'; // Corridors
            ctx.fillRect(x * cellPixel, y * cellPixel, cellPixel, cellPixel);
          }
        }
      }
    }

    // Draw Uncollected Relics on discovered tiles
    const halfW = (this.maze.width * this.maze.cellSize) / 2;
    const halfH = (this.maze.height * this.maze.cellSize) / 2;
    this.maze.relics.forEach(r => {
      if (!r.collected) {
        const rx = Math.floor((r.x + halfW) / this.maze.cellSize);
        const ry = Math.floor((r.z + halfH) / this.maze.cellSize);
        if (this.discovered[ry][rx]) {
          ctx.fillStyle = r.color;
          ctx.beginPath();
          ctx.arc(rx * cellPixel + cellPixel / 2, ry * cellPixel + cellPixel / 2, 2.5, 0, Math.PI * 2);
          ctx.fill();
        }
      }
    });

    // Draw Player Indicator Dot with Heading
    const playerMapX = (px + halfW) / (this.maze.width * this.maze.cellSize) * w;
    const playerMapY = (pz + halfH) / (this.maze.height * this.maze.cellSize) * h;

    ctx.fillStyle = '#00e5ff';
    ctx.beginPath();
    ctx.arc(playerMapX, playerMapY, 3.5, 0, Math.PI * 2);
    ctx.fill();

    // Direction line
    ctx.strokeStyle = '#00e5ff';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(playerMapX, playerMapY);
    ctx.lineTo(
      playerMapX - Math.sin(this.player.yaw) * 7.0,
      playerMapY - Math.cos(this.player.yaw) * 7.0
    );
    ctx.stroke();
  }
}
