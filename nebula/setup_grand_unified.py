#!/usr/bin/env python3
import os

html_source = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cathedral Chroma Ω // Grand Unified World Engine</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #030306;
            color: #d0d4dc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }
        #canvas-container { width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 1; }
        .hud {
            position: absolute;
            z-index: 100;
            background: rgba(8, 12, 20, 0.88);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(218, 165, 32, 0.35);
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 11px;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.85);
        }
        #header-hud { top: 16px; left: 16px; width: 440px; border-left: 3px solid #daa520; }
        #header-hud h1 { font-size: 13px; font-weight: 700; color: #f5d77f; text-transform: uppercase; margin-bottom: 4px; }
        .subtitle { font-size: 9.5px; color: #8892b0; margin-bottom: 8px; }
        .row { display: flex; justify-content: space-between; margin: 3px 0; border-bottom: 1px solid rgba(255,255,255,0.06); padding-bottom: 2px; }
        .lbl { color: #8892b0; }
        .val { color: #e6f1ff; font-weight: 600; font-family: monospace; }
        .gold { color: #ffd700; }
        .cyan { color: #00f0ff; }
        .emerald { color: #00ff88; }
        .crimson { color: #ff3366; }

        #neural-hud {
            top: 16px;
            right: 16px;
            width: 320px;
            border-right: 3px solid #ffd700;
        }
        #neural-hud h2 { font-size: 11px; color: #ffd700; text-transform: uppercase; margin-bottom: 6px; display: flex; justify-content: space-between; }
        #neural-canvas {
            width: 100%;
            height: 160px;
            background: rgba(4, 6, 10, 0.95);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 4px;
            margin-bottom: 6px;
        }

        #ledger-hud {
            top: 310px;
            right: 16px;
            width: 320px;
            max-height: 280px;
            overflow-y: hidden;
            border-right: 3px solid #00f0ff;
        }
        #ledger-hud h2 { font-size: 11px; color: #00f0ff; text-transform: uppercase; margin-bottom: 6px; display: flex; justify-content: space-between; }
        .block-card {
            background: rgba(12, 18, 28, 0.75);
            border: 1px solid rgba(0, 240, 255, 0.2);
            border-radius: 4px;
            padding: 6px 8px;
            margin-bottom: 5px;
            font-family: monospace;
            font-size: 9px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-4px); } to { opacity: 1; transform: translateY(0); } }

        #action-hud {
            position: absolute;
            bottom: 20px;
            left: 20px;
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
            max-width: 880px;
            z-index: 1000;
        }
        button.btn-action {
            background: rgba(14, 20, 32, 0.95);
            padding: 10px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 10.5px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            transition: all 0.2s ease;
            box-shadow: 0 4px 16px rgba(0,0,0,0.6);
        }
        .btn-gold { border: 2px solid #ffd700; color: #ffd700; }
        .btn-gold:hover { background: rgba(255, 215, 0, 0.25); box-shadow: 0 0 16px rgba(255, 215, 0, 0.4); }
        .btn-cyan { border: 2px solid #00f0ff; color: #00f0ff; }
        .btn-cyan:hover { background: rgba(0, 240, 255, 0.25); box-shadow: 0 0 16px rgba(0, 240, 255, 0.4); }
        .btn-mint { border: 2px solid #00ff88; color: #00ff88; }
        .btn-mint:hover { background: rgba(0, 255, 136, 0.25); box-shadow: 0 0 16px rgba(0, 255, 136, 0.4); }
        .btn-crimson { border: 2px solid #ff3366; color: #ff3366; }
        .btn-crimson:hover { background: rgba(255, 51, 102, 0.25); box-shadow: 0 0 16px rgba(255, 51, 102, 0.4); }
        .btn-neutral { border: 1px solid rgba(218, 165, 32, 0.4); color: #c5cdd9; }
        .btn-neutral:hover { border-color: #ffd700; color: #ffd700; }

        #status-ticker { bottom: 20px; right: 20px; width: 340px; font-size: 10px; font-family: monospace; border-left: 3px solid #00ff88; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="header-hud" class="hud">
        <h1>Cathedral Chroma Ω // Grand Unified Engine</h1>
        <div class="subtitle">Fused Architecture: Volumetric 18.4K Manifold x Neural Inhabitants x Merkle DAG</div>
        <div class="row"><span class="lbl">Permineralized Merkle Root</span><span id="tel-merkle" class="val cyan">0x79935386C053F1A8</span></div>
        <div class="row"><span class="lbl">Tenfold Architecture Sequence</span><span class="val gold">P→O→L→D→E→N→C→A→I→X→P</span></div>
        <div class="row"><span class="lbl">Carbon-Silicon Noether Flux (J_CS)</span><span class="val">1.4730 × 10⁻²² J/s</span></div>
        <div class="row"><span class="lbl">Impedance Coupling Index (Γ)</span><span class="val emerald">1.0248 (Valid)</span></div>
        <div class="row"><span class="lbl">Gaussian Population / Strata</span><span id="tel-count" class="val gold">18,400 Splats / 36 Strata</span></div>
        <div class="row"><span class="lbl">Autonomous Neuro-Entities</span><span id="tel-pop" class="val emerald">140 Agents (Active)</span></div>
        <div class="row"><span class="lbl">Ensemble Torsion &lang;T&rang;</span><span class="val emerald">+0.4119 × 10⁻³⁵ m⁻¹</span></div>
        <div class="row"><span class="lbl">PoE Gas Credit Pool</span><span id="tel-gas" class="val gold">125 Credits</span></div>
        <div class="row"><span class="lbl">Cadence / Adiabatic Headroom</span><span class="val cyan">1.50 Hz / 6.33 × 10¹⁴</span></div>
    </div>

    <div id="neural-hud" class="hud">
        <h2>
            <span>Mind Neuro-Map</span>
            <span id="entity-id-tag" class="gold">Entity #042</span>
        </h2>
        <canvas id="neural-canvas" width="280" height="160"></canvas>
        <div class="row"><span class="lbl">Somatic Energy</span><span id="neu-energy" class="val emerald">92.4 %</span></div>
        <div class="row"><span class="lbl">Epistemic Debt</span><span id="neu-debt" class="val">0.12</span></div>
        <div class="row"><span class="lbl">Active Drive</span><span id="neu-drive" class="val cyan">FORAGING</span></div>
        <div class="row"><span class="lbl">Belnap Valuation</span><span id="neu-belnap" class="val gold">TRUE (Consensus)</span></div>
    </div>

    <div id="ledger-hud" class="hud">
        <h2>
            <span>Ash Archive JBP Ledger</span>
            <span id="block-counter" style="color:#ffd700">835 Blocks</span>
        </h2>
        <div id="block-stream"></div>
    </div>

    <div id="status-ticker" class="hud">
        <div style="color:#00ff88; font-weight:bold; margin-bottom:4px;">UNIFIED RUNTIME TELEMETRY</div>
        <div id="ticker-msg">Circuit state: CLOSED. Somatic and autoregressive fluxes synchronized.</div>
    </div>

    <div id="action-hud">
        <button class="btn-action btn-gold" id="btn-scale-gaussians" onclick="scaleGaussianPopulation(18400)">[GAUSSIANS: 18.4K]</button>
        <button class="btn-action btn-cyan" id="btn-add-layer" onclick="injectMonadLayer()">[INJECT MONAD STRATUM +1]</button>
        <button class="btn-action btn-mint" id="btn-asset-gen" onclick="triggerAssetMintingPrompt()">[PROMPT ASSET MINT]</button>
        <button class="btn-action btn-crimson" id="btn-contradiction" onclick="injectParaconsistentContradiction()">[INJECT CONTRADICTION]</button>
        <button class="btn-action btn-neutral" onclick="toggleTorsionField()">Toggle Torsion</button>
        <button class="btn-action btn-neutral" onclick="resetCamera()">Recenter</button>
    </div>

    <script>
        const TARGET_GAUSSIAN_COUNT = 18400;
        const MONAD_LAYER_COUNT = 36;
        const STRATUM_Z_OFFSET = 1.618;
        const MAX_ALLOCATION = 32768;

        let scene, camera, renderer, controls;
        let pointsMesh, geometry, planetMesh;
        let showTorsion = false;
        let currentSplatCount = TARGET_GAUSSIAN_COUNT;
        let currentStrataCount = MONAD_LAYER_COUNT;

        let positions = new Float32Array(MAX_ALLOCATION * 3);
        let colors = new Float32Array(MAX_ALLOCATION * 3);
        let alphas = new Float32Array(MAX_ALLOCATION);

        let merkleRoot = "0x79935386C053F1A8";
        let blockHeight = 835;
        let gasPool = 125;

        const INPUT_LABELS = ["Slope", "Biomass", "Hazard", "Energy", "Torsion", "Memory"];
        const OUTPUT_LABELS = ["Thrust", "Yaw", "Harvest"];

        class NeuralBrain {
            constructor() {
                this.w1 = Array.from({length: 4}, () => Array.from({length: 6}, () => (Math.random() * 2 - 1)));
                this.w2 = Array.from({length: 3}, () => Array.from({length: 4}, () => (Math.random() * 2 - 1)));
                this.inputs = new Array(6).fill(0);
                this.hidden = new Array(4).fill(0);
                this.outputs = new Array(3).fill(0);
                this.plasticity = 0.05;
            }

            forward(inputs) {
                this.inputs = inputs;
                for (let j = 0; j < 4; j++) {
                    let sum = 0;
                    for (let i = 0; i < 6; i++) sum += this.inputs[i] * this.w1[j][i];
                    this.hidden[j] = Math.tanh(sum);
                }
                for (let k = 0; k < 3; k++) {
                    let sum = 0;
                    for (let j = 0; j < 4; j++) sum += this.hidden[j] * this.w2[k][j];
                    this.outputs[k] = Math.tanh(sum);
                }
                return this.outputs;
            }

            adapt(reward) {
                for (let j = 0; j < 4; j++) {
                    for (let i = 0; i < 6; i++) {
                        this.w1[j][i] += this.plasticity * reward * this.inputs[i] * this.hidden[j];
                        this.w1[j][i] = Math.max(-2, Math.min(2, this.w1[j][i]));
                    }
                }
                for (let k = 0; k < 3; k++) {
                    for (let j = 0; j < 4; j++) {
                        this.w2[k][j] += this.plasticity * reward * this.hidden[j] * this.outputs[k];
                        this.w2[k][j] = Math.max(-2, Math.min(2, this.w2[k][j]));
                    }
                }
            }
        }

        class Inhabitant {
            constructor(id) {
                this.id = id;
                this.pos = new THREE.Vector3(
                    (Math.random() - 0.5) * 12.0,
                    (Math.random() - 0.5) * 8.0,
                    (Math.random() - 0.5) * 12.0
                );
                this.vel = new THREE.Vector3(
                    (Math.random() - 0.5) * 0.4,
                    (Math.random() - 0.5) * 0.2,
                    (Math.random() - 0.5) * 0.4
                );
                this.energy = 85 + Math.random() * 15;
                this.debt = Math.random() * 0.15;
                this.belnap = "TRUE";
                this.brain = new NeuralBrain();

                this.mesh = new THREE.Mesh(
                    new THREE.BoxGeometry(0.24, 0.24, 0.24),
                    new THREE.MeshBasicMaterial({ color: 0x00ff88 })
                );
                this.mesh.position.copy(this.pos);
                scene.add(this.mesh);
            }

            step(dt) {
                let distToCenter = this.pos.length();
                let slope = Math.sin(distToCenter * 0.5);
                let distToEmerald = Math.abs(this.pos.y);
                let hazard = Math.abs(this.pos.x) > 7.0 ? 0.8 : 0.1;
                let energySensor = this.energy / 100.0;
                let torsionSensor = 0.412;
                let memorySensor = 1.0 - this.debt;

                let inputs = [slope, distToEmerald, hazard, energySensor, torsionSensor, memorySensor];
                let outputs = this.brain.forward(inputs);

                let thrust = (outputs[0] + 1.0) * 0.5;
                let yaw = outputs[1] * 0.3;
                let harvest = outputs[2] > 0.3;

                this.vel.applyAxisAngle(new THREE.Vector3(0, 1, 0), yaw * dt);
                this.pos.addScaledVector(this.vel, thrust * dt * 4.0);

                if (Math.abs(this.pos.x) > 9.0) this.vel.x *= -1.0;
                if (Math.abs(this.pos.y) > 7.0) this.vel.y *= -1.0;
                if (Math.abs(this.pos.z) > 9.0) this.vel.z *= -1.0;

                this.mesh.position.copy(this.pos);
                this.energy -= (0.05 * thrust + 0.01) * dt;

                let reward = 0;
                if (distToEmerald < 2.0 && harvest) {
                    this.energy = Math.min(100, this.energy + 0.5 * dt);
                    reward = +0.15;
                } else if (hazard > 0.5) {
                    this.energy -= 0.15 * dt;
                    this.debt = Math.min(1.0, this.debt + 0.03 * dt);
                    reward = -0.2;
                }

                if (this.debt > 0.45) {
                    this.belnap = "BOTH";
                    this.mesh.material.color.setHex(0xffd700);
                } else {
                    this.belnap = "TRUE";
                    this.mesh.material.color.setHex(0x00ff88);
                }

                this.brain.adapt(reward);
            }
        }

        let inhabitants = [];
        let selectedEntity = null;

        const C_GOLD = [0.85, 0.68, 0.22];
        const C_TEAL = [0.12, 0.52, 0.54];
        const C_BLUE = [0.08, 0.18, 0.36];
        const C_OBSIDIAN = [0.04, 0.04, 0.06];

        function generateStratifiedSplats(count, strataCount) {
            let pIdx = 0;
            const perStratum = Math.floor(count / strataCount);

            for (let s = 0; s < strataCount; s++) {
                let zOffset = (s - strataCount / 2.0) * STRATUM_Z_OFFSET;
                let col = C_TEAL;
                let alphaBase = 0.82;

                if (s === 0) { col = C_GOLD; alphaBase = 0.98; }
                else if (s >= 1 && s <= 18) { col = C_TEAL; alphaBase = 0.82; }
                else if (s >= 19 && s <= 30) { col = C_BLUE; alphaBase = 0.35; }
                else { col = C_OBSIDIAN; alphaBase = 0.20; }

                for (let i = 0; i < perStratum; i++) {
                    let theta = Math.random() * Math.PI * 2.0;
                    let rad = 1.2 + Math.random() * 8.5;
                    let x = rad * Math.cos(theta);
                    let y = (Math.random() - 0.5) * 11.0 + (s % 3) * 0.4;
                    let z = rad * Math.sin(theta) + zOffset;

                    positions[pIdx * 3] = x;
                    positions[pIdx * 3 + 1] = y;
                    positions[pIdx * 3 + 2] = z;

                    colors[pIdx * 3] = col[0];
                    colors[pIdx * 3 + 1] = col[1];
                    colors[pIdx * 3 + 2] = col[2];

                    alphas[pIdx] = alphaBase;
                    pIdx++;
                }
            }

            while (pIdx < count) {
                positions[pIdx * 3] = 0; positions[pIdx * 3 + 1] = 0; positions[pIdx * 3 + 2] = 0;
                colors[pIdx * 3] = C_TEAL[0]; colors[pIdx * 3 + 1] = C_TEAL[1]; colors[pIdx * 3 + 2] = C_TEAL[2];
                alphas[pIdx] = 0.8;
                pIdx++;
            }
        }

        function init() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x030306, 0.022);

            camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 8, 28);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;

            generateStratifiedSplats(currentSplatCount, currentStrataCount);

            geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3).setUsage(THREE.DynamicDrawUsage));
            geometry.setAttribute('customColor', new THREE.BufferAttribute(colors, 3).setUsage(THREE.DynamicDrawUsage));
            geometry.setAttribute('baseAlpha', new THREE.BufferAttribute(alphas, 1).setUsage(THREE.DynamicDrawUsage));
            geometry.setDrawRange(0, currentSplatCount);

            const mat = new THREE.ShaderMaterial({
                uniforms: {
                    uTime: { value: 0.0 },
                    uContradictionFlash: { value: 0.0 }
                },
                vertexShader: `
                    attribute vec3 customColor;
                    attribute float baseAlpha;
                    varying vec3 vColor;
                    varying float vAlpha;
                    uniform float uTime;
                    uniform float uContradictionFlash;

                    void main() {
                        vColor = customColor;
                        vAlpha = baseAlpha;
                        if (baseAlpha < 0.35) {
                            float pulse = sin(uTime * 6.28318 * 1.5) * 0.5 + 0.5;
                            vColor = mix(customColor, vec3(1.0, 0.35, 0.05), pulse * 0.8 + uContradictionFlash);
                            vAlpha = clamp(baseAlpha + pulse * 0.35 + uContradictionFlash * 0.5, 0.1, 1.0);
                        }
                        vec4 mv = modelViewMatrix * vec4(position, 1.0);
                        gl_PointSize = (115.0 / -mv.z) * (0.8 + 0.4 * vAlpha);
                        gl_Position = projectionMatrix * mv;
                    }
                `,
                fragmentShader: `
                    varying vec3 vColor;
                    varying float vAlpha;
                    void main() {
                        vec2 c = gl_PointCoord - vec2(0.5);
                        float d = length(c);
                        if (d > 0.5) discard;
                        gl_FragColor = vec4(vColor, exp(-d * d * 8.0) * vAlpha);
                    }
                `,
                transparent: true,
                depthWrite: false,
                blending: THREE.AdditiveBlending
            });

            pointsMesh = new THREE.Points(geometry, mat);
            scene.add(pointsMesh);

            const planetGeom = new THREE.SphereGeometry(3.2, 32, 32);
            const planetMat = new THREE.MeshBasicMaterial({ color: 0x051020, wireframe: true });
            planetMesh = new THREE.Mesh(planetGeom, planetMat);
            scene.add(planetMesh);

            for (let i = 0; i < 140; i++) {
                inhabitants.push(new Inhabitant(i + 1));
            }
            selectedEntity = inhabitants[0];

            seedInitialBlocks();
            window.addEventListener('resize', onWindowResize);
            animate();
        }

        function drawNeuralConnectome() {
            const canvas = document.getElementById('neural-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!selectedEntity) return;
            const brain = selectedEntity.brain;

            const layerX = [30, 140, 250];
            const inY = [18, 42, 66, 90, 114, 138];
            const hidY = [30, 65, 100, 135];
            const outY = [35, 75, 115];

            for (let j = 0; j < 4; j++) {
                for (let i = 0; i < 6; i++) {
                    let w = brain.w1[j][i];
                    ctx.beginPath();
                    ctx.moveTo(layerX[0], inY[i]);
                    ctx.lineTo(layerX[1], hidY[j]);
                    ctx.strokeStyle = w > 0 ? `rgba(0, 240, 255, ${Math.abs(w)*0.45})` : `rgba(255, 51, 102, ${Math.abs(w)*0.45})`;
                    ctx.lineWidth = Math.max(0.5, Math.abs(w) * 1.5);
                    ctx.stroke();
                }
            }

            for (let k = 0; k < 3; k++) {
                for (let j = 0; j < 4; j++) {
                    let w = brain.w2[k][j];
                    ctx.beginPath();
                    ctx.moveTo(layerX[1], hidY[j]);
                    ctx.lineTo(layerX[2], outY[k]);
                    ctx.strokeStyle = w > 0 ? `rgba(255, 215, 0, ${Math.abs(w)*0.5})` : `rgba(255, 51, 102, ${Math.abs(w)*0.5})`;
                    ctx.lineWidth = Math.max(0.5, Math.abs(w) * 1.8);
                    ctx.stroke();
                }
            }

            function drawNode(x, y, val, label) {
                ctx.beginPath();
                ctx.arc(x, y, 5, 0, Math.PI * 2);
                let alpha = Math.min(1.0, Math.abs(val) + 0.2);
                ctx.fillStyle = val >= 0 ? `rgba(0, 255, 136, ${alpha})` : `rgba(255, 51, 102, ${alpha})`;
                ctx.fill();
                ctx.strokeStyle = '#e6f1ff';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.fillStyle = '#8892b0';
                ctx.font = '8px monospace';
                ctx.fillText(label, x - 16, y + 13);
            }

            for (let i = 0; i < 6; i++) drawNode(layerX[0], inY[i], brain.inputs[i], INPUT_LABELS[i]);
            for (let j = 0; j < 4; j++) drawNode(layerX[1], hidY[j], brain.hidden[j], `H${j+1}`);
            for (let k = 0; k < 3; k++) drawNode(layerX[2], outY[k], brain.outputs[k], OUTPUT_LABELS[k]);
        }

        function scaleGaussianPopulation(target) {
            currentSplatCount = target;
            generateStratifiedSplats(currentSplatCount, currentStrataCount);
            geometry.attributes.position.needsUpdate = true;
            geometry.attributes.customColor.needsUpdate = true;
            geometry.attributes.baseAlpha.needsUpdate = true;
            geometry.setDrawRange(0, currentSplatCount);
            document.getElementById('tel-count').innerText = `${currentSplatCount.toLocaleString()} Splats / ${currentStrataCount} Strata`;
            document.getElementById('ticker-msg').innerText = `Manifold scaled to ${currentSplatCount.toLocaleString()} splats.`;
        }

        function injectMonadLayer() {
            if (currentStrataCount < 48) {
                currentStrataCount += 1;
                generateStratifiedSplats(currentSplatCount, currentStrataCount);
                geometry.attributes.position.needsUpdate = true;
                geometry.attributes.customColor.needsUpdate = true;
                geometry.attributes.baseAlpha.needsUpdate = true;
                document.getElementById('tel-strata').innerText = `${currentStrataCount} Strata (Δz = 1.618)`;
                document.getElementById('ticker-msg').innerText = `Injected Monad Stratum Layer #${currentStrataCount}.`;
            }
        }

        async function triggerAssetMintingPrompt() {
            let prompt = window.prompt("Enter Cathedral Artifact specification:", "reliquary of unwritten law");
            if (!prompt) return;

            document.getElementById('ticker-msg').innerText = `Synthesizing asset: "${prompt}"...`;
            let result = null;
            try {
                const response = await fetch("http://127.0.0.1:8000/api/v1/assets/synthesize", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        prompt: prompt,
                        spectral_dominant: "Teal/Curiosity",
                        triz_limit_budget: 0.28,
                        splat_count: 512
                    })
                });
                result = await response.json();
            } catch (err) {
                let fallbackHash = "0x" + Math.random().toString(16).substr(2, 16).toUpperCase();
                let localSplats = [];
                for (let i = 0; i < 512; i++) {
                    let u = Math.random() * Math.PI * 2.0;
                    let v = Math.random() * Math.PI;
                    let r = 1.2 + 0.4 * Math.sin(u * 3.0);
                    localSplats.push({
                        pos: [r * Math.sin(v) * Math.cos(u), r * Math.cos(v) + 2.0, r * Math.sin(v) * Math.sin(u)],
                        rgb: [0.12, 0.52, 0.54],
                        alpha: 0.90
                    });
                }
                result = { status: "IN_BROWSER_FALLBACK", block_hash: fallbackHash, nodes_added: 512, splats: localSplats };
            }

            if (result && result.splats && result.splats.length > 0) {
                let start = currentSplatCount;
                let added = Math.min(result.splats.length, MAX_ALLOCATION - start);
                for (let i = 0; i < added; i++) {
                    let s = result.splats[i];
                    positions[(start + i) * 3] = s.pos[0];
                    positions[(start + i) * 3 + 1] = s.pos[1];
                    positions[(start + i) * 3 + 2] = s.pos[2];
                    colors[(start + i) * 3] = s.rgb[0];
                    colors[(start + i) * 3 + 1] = s.rgb[1];
                    colors[(start + i) * 3 + 2] = s.rgb[2];
                    alphas[start + i] = s.alpha;
                }
                currentSplatCount += added;
                geometry.attributes.position.needsUpdate = true;
                geometry.attributes.customColor.needsUpdate = true;
                geometry.attributes.baseAlpha.needsUpdate = true;
                geometry.setDrawRange(0, currentSplatCount);
            }

            merkleRoot = result.block_hash;
            blockHeight++;
            document.getElementById('tel-merkle').innerText = merkleRoot;
            document.getElementById('tel-count').innerText = `${currentSplatCount.toLocaleString()} Splats`;
            document.getElementById('block-counter').innerText = `${blockHeight} Blocks`;

            appendBlockCard(result.block_hash, `Artifact: "${prompt}" | +${result.nodes_added} Splats`);
            document.getElementById('ticker-msg').innerText = `Permineralized "${prompt}" into Block ${result.block_hash}.`;
        }

        function injectParaconsistentContradiction() {
            pointsMesh.material.uniforms.uContradictionFlash.value = 1.0;
            setTimeout(() => { pointsMesh.material.uniforms.uContradictionFlash.value = 0.0; }, 400);

            inhabitants.forEach((e, idx) => {
                if (idx % 4 === 0) {
                    e.belnap = "BOTH";
                    e.debt = 0.65;
                    e.mesh.material.color.setHex(0xffd700);
                }
            });

            blockHeight++;
            let raw = merkleRoot + "CONTRADICTION_RESOLVED" + Date.now();
            let hashNum = 0;
            for (let i = 0; i < raw.length; i++) hashNum = (hashNum << 5) - hashNum + raw.charCodeAt(i);
            let hex = "0x" + Math.abs(hashNum).toString(16).toUpperCase().padStart(16, '0');
            merkleRoot = hex;

            document.getElementById('tel-merkle').innerText = merkleRoot;
            document.getElementById('block-counter').innerText = `${blockHeight} Blocks`;
            appendBlockCard(hex, "Metamorphic Squeeze: Failure Mode D Interlock Locked");
            document.getElementById('ticker-msg').innerText = "Injected Contradiction: Paradox petrified into M11 Kintsugi Pin.";
        }

        function appendBlockCard(hash, meta) {
            const stream = document.getElementById('block-stream');
            const card = document.createElement('div');
            card.className = 'block-card';
            card.innerHTML = `
                <div style="color:#00ff88; font-weight:bold;">Commit: ${hash}</div>
                <div style="color:#8892b0; font-size:8px;">${meta}</div>
            `;
            stream.insertBefore(card, stream.firstChild);
            if (stream.children.length > 5) stream.removeChild(stream.lastChild);
        }

        function seedInitialBlocks() {
            appendBlockCard("0x79935386C053F1A8", "Tenfold Sequence: P->O->L->D->E->N->C->A->I->X->P");
            appendBlockCard("0x5C245EE7DC7319AE", "Carbon-Silicon Flux: 1.4730e-22 J/s | Gamma: 1.0248");
        }

        function toggleTorsionField() {
            showTorsion = !showTorsion;
            pointsMesh.rotation.z += showTorsion ? 0.35 : -0.35;
        }

        function resetCamera() { controls.reset(); }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        let clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            let dt = Math.min(0.08, clock.getDelta());
            let t = clock.getElapsedTime();

            pointsMesh.material.uniforms.uTime.value = t;
            pointsMesh.rotation.y += 0.0006;
            if (planetMesh) planetMesh.rotation.y += 0.002;

            for (let i = 0; i < inhabitants.length; i++) {
                inhabitants[i].step(dt);
            }

            if (selectedEntity) {
                document.getElementById('entity-id-tag').innerText = `Entity #${selectedEntity.id}`;
                document.getElementById('neu-energy').innerText = `${selectedEntity.energy.toFixed(1)} %`;
                document.getElementById('neu-debt').innerText = selectedEntity.debt.toFixed(2);
                document.getElementById('neu-belnap').innerText = selectedEntity.belnap;
                let drive = "FORAGING";
                if (selectedEntity.debt > 0.45) drive = "DIALETHEIC_STABILIZATION";
                else if (selectedEntity.energy < 30) drive = "METABOLIC_CRITICAL";
                document.getElementById('neu-drive').innerText = drive;
            }

            drawNeuralConnectome();
            controls.update();
            renderer.render(scene, camera);
        }

        window.onload = init;
    </script>
</body>
</html>
"""

with open("cathedral_grand_unified_engine.html", "w", encoding="utf-8") as f:
    f.write(html_source)

print("Grand Unified Engine successfully written to cathedral_grand_unified_engine.html")
