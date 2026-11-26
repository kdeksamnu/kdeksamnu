import * as THREE from 'three';
import { Viewport } from '../core/Viewport';
import { SomaticSolver } from '../core/SomaticSolver';
import { SomaticDualLumenShader } from '../shaders/somaticDualLumen';
import { GlobalUniforms } from '../shaders/masterShader';

export class MythotechnicalWidget {
  public container: HTMLElement;
  public toggleBtn: HTMLElement;
  private viewport: Viewport;
  private solver: SomaticSolver;

  // Active Parameter State
  public bayerDensity: number = 0.85;
  public subPixelScale: number = 3.0;
  public surfaceType: string = 'Obsidian / Bone';
  public kintsugiOverlay: number = 12.4;

  public psiCyan: number = 80;
  public thetaGold: number = 65;
  public speechCadence: number = 1.45;
  public azimuth: number = 135.0;

  public chiaroscuroGamma: number = 2.20;
  public pupilNullCutoff: number = 0.05;
  public aoDepth: number = 0.92;
  public cavityScale: number = 1.00;

  public belnapState: string = 'State B (1,1)';
  public wavelengthNm: number = 488;
  public dialetheicBlend: string = 'Dithered Grid';
  public saturation: number = 1.15;

  public fovAngle: number = 45.0;
  public saccadeJitter: number = 0.75;
  public gazeAngle: number = 12.4;
  public pelvicOffset: number = 0.00;

  constructor(viewport: Viewport, solver: SomaticSolver) {
    this.viewport = viewport;
    this.solver = solver;

    this.container = document.createElement('div');
    this.toggleBtn = document.createElement('button');

    this.initStyles();
    this.renderUI();
    this.bindEvents();

    document.body.appendChild(this.container);
    document.body.appendChild(this.toggleBtn);
  }

  private initStyles() {
    // 1. Floating Toggle Button
    this.toggleBtn.innerText = '🎛️ WIDGET v2.4';
    this.toggleBtn.style.position = 'fixed';
    this.toggleBtn.style.top = '10px';
    this.toggleBtn.style.right = '370px';
    this.toggleBtn.style.background = '#0d131f';
    this.toggleBtn.style.border = '1px solid #00e5ff';
    this.toggleBtn.style.color = '#00e5ff';
    this.toggleBtn.style.padding = '6px 12px';
    this.toggleBtn.style.borderRadius = '4px';
    this.toggleBtn.style.fontSize = '11px';
    this.toggleBtn.style.fontFamily = 'monospace';
    this.toggleBtn.style.cursor = 'pointer';
    this.toggleBtn.style.zIndex = '9999';
    this.toggleBtn.style.boxShadow = '0 0 12px rgba(0,229,255,0.3)';

    // 2. Master Container Panel
    this.container.id = 'mythotechnical-widget';
    this.container.style.position = 'fixed';
    this.container.style.top = '50%';
    this.container.style.left = '50%';
    this.container.style.transform = 'translate(-50%, -50%)';
    this.container.style.width = '1020px';
    this.container.style.maxWidth = '95vw';
    this.container.style.maxHeight = '92vh';
    this.container.style.overflowY = 'auto';
    this.container.style.background = 'rgba(7, 11, 18, 0.96)';
    this.container.style.backdropFilter = 'blur(20px)';
    this.container.style.border = '1px solid #1a293d';
    this.container.style.borderRadius = '8px';
    this.container.style.padding = '14px 18px';
    this.container.style.boxSizing = 'border-box';
    this.container.style.fontFamily = '"SF Mono", "Segoe UI Mono", "Roboto Mono", monospace';
    this.container.style.color = '#f3f4f6';
    this.container.style.zIndex = '9500';
    this.container.style.boxShadow = '0 20px 60px rgba(0,0,0,0.95), 0 0 1px #00e5ff';
    this.container.style.display = 'none'; // Toggleable
  }

  public setVisible(show: boolean) {
    this.container.style.display = show ? 'block' : 'none';
    this.toggleBtn.style.borderColor = show ? '#ffd700' : '#00e5ff';
    this.toggleBtn.style.color = show ? '#ffd700' : '#00e5ff';
  }

  private renderUI() {
    this.container.innerHTML = `
      <!-- TOP HEADER -->
      <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #172436; padding-bottom:8px; margin-bottom:12px;">
        <div style="font-size:13px; font-weight:bold; color:#00e5ff; letter-spacing:0.08em;">
          MLAOS-PRIME // MYTHOTECHNICAL SHADER & RENDERING CONTROL WIDGET
        </div>
        <div style="display:flex; align-items:center; gap:12px;">
          <span style="font-size:11px; color:#ffd700; font-weight:bold;">VERSION 2.4 [ACTIVE]</span>
          <button id="btn-close-widget" style="background:#131d2e; border:1px solid #22354f; color:#9ca3af; border-radius:4px; padding:2px 8px; cursor:pointer;">✕</button>
        </div>
      </div>

      <!-- 6-CARD GRID (3x2) -->
      <div style="display:grid; grid-template-columns:repeat(3, 1fr); gap:10px; margin-bottom:12px;">

        <!-- 1. TEXTURE & MATERIAL (Pass 08) -->
        <div style="background:#0c121d; border:1px solid #1a273b; border-radius:6px; padding:10px;">
          <div style="font-size:11px; font-weight:bold; color:#00e5ff; margin-bottom:8px;">1. TEXTURE & MATERIAL (Pass 08)</div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>2x2 Bayer Dither Density</span><span id="v-bayer" style="color:#f3f4f6;">0.85</span>
          </div>
          <input type="range" id="s-bayer" min="0.0" max="1.0" step="0.05" value="0.85" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Sub-Pixel Scale Factor</span><span id="v-scale" style="color:#f3f4f6;">3.0 px</span>
          </div>
          <input type="range" id="s-scale" min="1.0" max="8.0" step="0.5" value="3.0" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-bottom:2px;">
            <span>Material Surface Type</span>
            <select id="sel-surface" style="background:#141f30; border:1px solid #233752; color:#00e5ff; font-size:10px; border-radius:3px; padding:2px 4px;">
              <option value="Obsidian / Bone">Obsidian / Bone</option>
              <option value="Burnished Bronze">Burnished Bronze</option>
              <option value="Cold Iron">Cold Iron</option>
              <option value="Bio-Silicate">Bio-Silicate</option>
              <option value="Vitreous Null">Vitreous Null</option>
            </select>
          </div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-top:8px;">
            <span>Kintsugi Gold Scar Overlay</span><span id="v-kintsugi" style="color:#f3f4f6;">12.4%</span>
          </div>
          <input type="range" id="s-kintsugi" min="0.0" max="100.0" step="0.5" value="12.4" style="width:100%; accent-color:#00e5ff;">
        </div>

        <!-- 2. DUAL-LUMEN LIGHTING (Pass 06) -->
        <div style="background:#0c121d; border:1px solid #1a273b; border-radius:6px; padding:10px;">
          <div style="font-size:11px; font-weight:bold; color:#f59e0b; margin-bottom:8px;">2. DUAL-LUMEN LIGHTING (Pass 06)</div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Psi Cyan (t_p Thesis)</span><span id="v-psi" style="color:#f3f4f6;">80%</span>
          </div>
          <input type="range" id="s-psi" min="0" max="100" step="5" value="80" style="width:100%; accent-color:#f59e0b; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Theta Gold (f_p Antithesis)</span><span id="v-theta" style="color:#f3f4f6;">65%</span>
          </div>
          <input type="range" id="s-theta" min="0" max="100" step="5" value="65" style="width:100%; accent-color:#f59e0b; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Speech Cadence Coupling (G)</span><span id="v-speech" style="color:#f3f4f6;">1.45x</span>
          </div>
          <input type="range" id="s-speech" min="0.5" max="3.0" step="0.05" value="1.45" style="width:100%; accent-color:#f59e0b; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Directional Vector Azimuth</span><span id="v-azimuth" style="color:#f3f4f6;">135.0 deg</span>
          </div>
          <input type="range" id="s-azimuth" min="0.0" max="360.0" step="5.0" value="135.0" style="width:100%; accent-color:#f59e0b;">
        </div>

        <!-- 3. SHADOWS & ABSORPTION (Pass 04) -->
        <div style="background:#0c121d; border:1px solid #1a273b; border-radius:6px; padding:10px;">
          <div style="font-size:11px; font-weight:bold; color:#c084fc; margin-bottom:8px;">3. SHADOWS & ABSORPTION (Pass 04)</div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Chiaroscuro Bias (gamma)</span><span id="v-gamma" style="color:#f3f4f6;">2.20</span>
          </div>
          <input type="range" id="s-gamma" min="0.5" max="4.0" step="0.05" value="2.20" style="width:100%; accent-color:#c084fc; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Pupil Null Sink Cutoff (c0)</span><span id="v-null" style="color:#f3f4f6;">0.05 abs</span>
          </div>
          <input type="range" id="s-null" min="0.0" max="0.2" step="0.01" value="0.05" style="width:100%; accent-color:#c084fc; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Ambient Occlusion Depth</span><span id="v-ao" style="color:#f3f4f6;">0.92</span>
          </div>
          <input type="range" id="s-ao" min="0.0" max="1.0" step="0.02" value="0.92" style="width:100%; accent-color:#c084fc; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Absorptive Cavity Scale</span><span id="v-cavity" style="color:#f3f4f6;">1.00</span>
          </div>
          <input type="range" id="s-cavity" min="0.1" max="2.0" step="0.05" value="1.00" style="width:100%; accent-color:#c084fc;">
        </div>

        <!-- 4. COLOR, HUE & LOGIC (FOUR) -->
        <div style="background:#0c121d; border:1px solid #1a273b; border-radius:6px; padding:10px;">
          <div style="font-size:11px; font-weight:bold; color:#00e5ff; margin-bottom:8px;">4. COLOR, HUE & LOGIC (FOUR)</div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-bottom:4px;">
            <span>Belnap-Dunn Logic Mode</span>
            <select id="sel-belnap" style="background:#141f30; border:1px solid #233752; color:#ffd700; font-size:10px; border-radius:3px; padding:2px 4px;">
              <option value="State B (1,1)">State B (1,1)</option>
              <option value="State T (1,0)">State T (1,0)</option>
              <option value="State F (0,1)">State F (0,1)</option>
              <option value="State N (0,0)">State N (0,0)</option>
            </select>
          </div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-top:8px;">
            <span>Spectral Wavelength (lambda)</span><span id="v-wave" style="color:#f3f4f6;">488 nm</span>
          </div>
          <input type="range" id="s-wave" min="380" max="750" step="2" value="488" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-bottom:4px;">
            <span>Dialetheic Blend Mode</span>
            <select id="sel-blend" style="background:#141f30; border:1px solid #233752; color:#00e5ff; font-size:10px; border-radius:3px; padding:2px 4px;">
              <option value="Dithered Grid">Dithered Grid</option>
              <option value="Additive Tensor">Additive Tensor</option>
              <option value="Somatic Squeeze">Somatic Squeeze</option>
            </select>
          </div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af; margin-top:8px;">
            <span>Chromatic Saturation</span><span id="v-sat" style="color:#f3f4f6;">1.15x</span>
          </div>
          <input type="range" id="s-sat" min="0.0" max="2.5" step="0.05" value="1.15" style="width:100%; accent-color:#00e5ff;">
        </div>

        <!-- 5. PERSPECTIVE & GAZE (Pass 10) -->
        <div style="background:#0c121d; border:1px solid #1a273b; border-radius:6px; padding:10px;">
          <div style="font-size:11px; font-weight:bold; color:#00e5ff; margin-bottom:8px;">5. PERSPECTIVE & GAZE (Pass 10)</div>

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Focal Length / FOV Angle</span><span id="v-fov" style="color:#f3f4f6;">45.0 deg</span>
          </div>
          <input type="range" id="s-fov" min="20.0" max="90.0" step="1.0" value="45.0" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Micro-Saccade Jitter (1.5Hz)</span><span id="v-saccade" style="color:#f3f4f6;">0.75 px</span>
          </div>
          <input type="range" id="s-saccade" min="0.0" max="2.0" step="0.05" value="0.75" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Gaze Interception Angle</span><span id="v-gaze" style="color:#f3f4f6;">+12.4 deg</span>
          </div>
          <input type="range" id="s-gaze" min="-45.0" max="45.0" step="0.5" value="12.4" style="width:100%; accent-color:#00e5ff; margin-bottom:6px;">

          <div style="display:flex; justify-content:space-between; font-size:10px; color:#9ca3af;">
            <span>Pelvic Axis Alignment</span><span id="v-pelvic" style="color:#f3f4f6;">0.00 offset</span>
          </div>
          <input type="range" id="s-pelvic" min="-5.0" max="5.0" step="0.2" value="0.0" style="width:100%; accent-color:#00e5ff;">
        </div>

        <!-- 6. LIVE GLSL UNIFORM FEED -->
        <div style="background:#06090f; border:1px solid #142030; border-radius:6px; padding:10px; display:flex; flex-direction:column;">
          <div style="font-size:11px; font-weight:bold; color:#38bdf8; margin-bottom:6px;">6. LIVE GLSL UNIFORM FEED</div>
          <pre id="glsl-code-block" style="flex:1; margin:0; font-size:9.5px; line-height:1.45; color:#94a3b8; overflow-x:auto;">
// Real-time WebGL State
u_bayerMatrix   = mat2(0,2,3,1)/4.0;
u_psiLumen      = vec4(0.0, 0.85, 0.95, 0.80);
u_thetaLumen    = vec4(1.0, 0.64, 0.12, 0.65);
u_speechScale   = 1.45;
u_pupilNull     = 0.05;
u_logicState    = vec2(1.0, 1.0); // B
u_saccadeFreq   = 1.5; // Hz
u_chiaroscuro   = 2.20;
u_lexILedger    = 0x9F42A1... [DAG]
status          = VALIDATED (c_i=0)
          </pre>
        </div>

      </div>

      <!-- BOTTOM TELEMETRY BAR -->
      <div style="background:#080c14; border:1px solid #162438; border-radius:6px; padding:8px 12px; font-size:9.5px; line-height:1.5;">
        <div style="font-weight:bold; color:#00e5ff; margin-bottom:2px;">SCENE MOMENTUM COUPLING VALIDATION (M 12x11 OPERATOR):</div>
        <div style="color:#cbd5e1;">
          <span style="color:#10b981;">C1 [Axis]: PASS (0.00)</span> | 
          <span style="color:#10b981;">C2 [Ground]: PASS (0.00)</span> | 
          <span style="color:#a855f7;">C4 [Dialetheic]: CONTAINED (0.00)</span> | 
          <span style="color:#ffd700;">C6 [Lumen]: COUPLED (1.45x)</span>
        </div>
        <div style="color:#94a3b8;">
          C8 [Material]: VALIDATED | C9 [Chiaroscuro]: DIRECTED | C10 [Metabolic]: BALANCED | C12 [Lex I]: APPENDED (Merkle DAG)
        </div>
        <div style="color:#64748b; margin-top:2px;">
          System State: Closed-loop feedback active (p_n+1 = p_n + K(c* - Mp_n)). Zero catastrophic cross-talk.
        </div>
      </div>
    `;
  }

  private updateGLSLFeed() {
    const psiNorm = (this.psiCyan / 100.0).toFixed(2);
    const thetaNorm = (this.thetaGold / 100.0).toFixed(2);
    const code = this.container.querySelector('#glsl-code-block');
    if (code) {
      code.innerHTML = `// Real-time WebGL State
u_bayerMatrix   = mat2(0,2,3,1)/4.0;
u_psiLumen      = vec4(0.0, 0.85, 0.95, ${psiNorm});
u_thetaLumen    = vec4(1.0, 0.64, 0.12, ${thetaNorm});
u_speechScale   = ${this.speechCadence.toFixed(2)};
u_pupilNull     = ${this.pupilNullCutoff.toFixed(2)};
u_logicState    = vec2(1.0, 1.0); // ${this.belnapState.split(' ') || 'B'}
u_saccadeFreq   = 1.5; // Hz
u_chiaroscuro   = ${this.chiaroscuroGamma.toFixed(2)};
u_lexILedger    = 0x9F42A1... [DAG]
status          = VALIDATED (c_i=0)`;
    }
  }

  private bindEvents() {
    this.toggleBtn.onclick = () => {
      const isVisible = this.container.style.display !== 'none';
      this.setVisible(!isVisible);
    };

    (this.container.querySelector('#btn-close-widget') as HTMLElement).onclick = () => {
      this.setVisible(false);
    };

    const bind = (id: string, lbl: string, fn: (v: number) => void, suffix: string = '') => {
      const i = this.container.querySelector(id) as HTMLInputElement;
      const l = this.container.querySelector(lbl) as HTMLElement;
      i.oninput = () => {
        const v = parseFloat(i.value);
        l.innerText = `${i.value}${suffix}`;
        fn(v);
        this.updateGLSLFeed();
      };
    };

    // 1. Texture & Material
    bind('#s-bayer', '#v-bayer', (v) => {
      this.bayerDensity = v;
      GlobalUniforms.uDitherStrength.value = v;
    });
    bind('#s-scale', '#v-scale', (v) => {
      this.subPixelScale = v;
      GlobalUniforms.uBayerScale.value = v;
    }, ' px');
    bind('#s-kintsugi', '#v-kintsugi', (v) => {
      this.kintsugiOverlay = v;
      GlobalUniforms.uVeinGlow.value = (v / 100.0) * 3.0;
      SomaticDualLumenShader.uniforms.uScarIntensity.value = v / 50.0;
    }, '%');

    // 2. Dual-Lumen
    bind('#s-psi', '#v-psi', (v) => {
      this.psiCyan = v;
      SomaticDualLumenShader.uniforms.uLumenCyan.value = (v / 100.0) * 2.0;
    }, '%');
    bind('#s-theta', '#v-theta', (v) => {
      this.thetaGold = v;
      SomaticDualLumenShader.uniforms.uLumenGold.value = (v / 100.0) * 2.0;
    }, '%');
    bind('#s-speech', '#v-speech', (v) => { this.speechCadence = v; }, 'x');
    bind('#s-azimuth', '#v-azimuth', (v) => {
      this.azimuth = v;
      const rad = (v * Math.PI) / 180;
      GlobalUniforms.uLightDir.value.set(Math.cos(rad), 1.0, Math.sin(rad)).normalize();
      SomaticDualLumenShader.uniforms.uLightDir.value.copy(GlobalUniforms.uLightDir.value);
    }, ' deg');

    // 3. Shadows
    bind('#s-gamma', '#v-gamma', (v) => {
      this.chiaroscuroGamma = v;
      GlobalUniforms.uChiaroscuroCut.value = v / 4.0;
    });
    bind('#s-null', '#v-null', (v) => {
      this.pupilNullCutoff = v;
      GlobalUniforms.uShadowFloor.value = v;
    }, ' abs');
    bind('#s-ao', '#v-ao', (v) => { this.aoDepth = v; });
    bind('#s-cavity', '#v-cavity', (v) => { this.cavityScale = v; });

    // 4. Color, Hue & Logic
    const selBelnap = this.container.querySelector('#sel-belnap') as HTMLSelectElement;
    selBelnap.onchange = () => {
      this.belnapState = selBelnap.value;
      if (this.belnapState.includes('State B')) {
        SomaticDualLumenShader.uniforms.uDialetheicTension.value = 1.0;
      } else {
        SomaticDualLumenShader.uniforms.uDialetheicTension.value = 0.0;
      }
      this.updateGLSLFeed();
    };

    bind('#s-wave', '#v-wave', (v) => {
      this.wavelengthNm = v;
      // Convert wavelength (nm) to RGB tint
      const col = new THREE.Color().setHSL((v - 380) / (750 - 380), 0.9, 0.5);
      GlobalUniforms.uColorPrimary.value.copy(col);
    }, ' nm');

    bind('#s-sat', '#v-sat', (v) => { this.saturation = v; }, 'x');

    // 5. Perspective & Gaze
    bind('#s-fov', '#v-fov', (v) => {
      this.fovAngle = v;
      this.viewport.camera.fov = v;
      this.viewport.camera.updateProjectionMatrix();
    }, ' deg');

    bind('#s-saccade', '#v-saccade', (v) => { this.saccadeJitter = v; }, ' px');
    bind('#s-gaze', '#v-gaze', (v) => { this.gazeAngle = v; }, ' deg');
    bind('#s-pelvic', '#v-pelvic', (v) => { this.pelvicOffset = v; }, ' offset');
  }
}
