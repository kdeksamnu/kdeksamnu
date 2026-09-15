#!/usr/bin/env python3
import os

html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cathedral-Engine // World Simulator: The Architecture of Residual Meaning</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #050508;
            color: #d0d4dc;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, monospace;
            overflow: hidden;
            width: 100vw;
            height: 100vh;
        }
        #canvas-container {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }
        .hud-panel {
            position: absolute;
            z-index: 10;
            background: rgba(10, 12, 18, 0.82);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(218, 165, 32, 0.25);
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 11px;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.65);
        }
        #header-hud {
            top: 16px;
            left: 16px;
            max-width: 440px;
            border-left: 3px solid #daa520;
        }
        #header-hud h1 {
            font-size: 13px;
            font-weight: 700;
            color: #f5d77f;
            text-transform: uppercase;
            margin-bottom: 4px;
            letter-spacing: 1px;
        }
        #header-hud .subtitle {
            font-size: 10px;
            color: #8892b0;
            margin-bottom: 8px;
        }
        .telemetry-row {
            display: flex;
            justify-content: space-between;
            margin: 3px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            padding-bottom: 2px;
        }
        .telemetry-label { color: #8892b0; }
        .telemetry-value { color: #e6f1ff; font-weight: 600; font-family: monospace; }
        .value-gold { color: #ffd700; }
        .value-cyan { color: #00f0ff; }
        .value-crimson { color: #ff3366; }
        .value-emerald { color: #00ff88; }
        
        #controls-hud {
            bottom: 16px;
            left: 16px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            max-width: 650px;
        }
        button.btn {
            background: rgba(20, 24, 36, 0.85);
            color: #c5cdd9;
            border: 1px solid rgba(218, 165, 32, 0.35);
            padding: 7px 12px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 10px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            transition: all 0.2s ease;
        }
        button.btn:hover {
            background: rgba(218, 165, 32, 0.25);
            color: #ffd700;
            border-color: #ffd700;
            box-shadow: 0 0 12px rgba(218, 165, 32, 0.35);
        }
        button.btn.active {
            background: #daa520;
            color: #050508;
            border-color: #ffd700;
        }

        #ledger-hud {
            top: 16px;
            right: 16px;
            width: 320px;
            max-height: 480px;
            overflow-y: hidden;
            border-right: 3px solid #00f0ff;
        }
        #ledger-hud h2 {
            font-size: 11px;
            color: #00f0ff;
            text-transform: uppercase;
            margin-bottom: 8px;
            letter-spacing: 1px;
            display: flex;
            justify-content: space-between;
        }
        .block-card {
            background: rgba(15, 20, 30, 0.6);
            border: 1px solid rgba(0, 240, 255, 0.15);
            border-radius: 4px;
            padding: 8px;
            margin-bottom: 6px;
            font-family: monospace;
            font-size: 9.5px;
            animation: fadeIn 0.4s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .block-hash { color: #00f0ff; font-weight: bold; }
        .block-meta { color: #8892b0; font-size: 8.5px; margin-top: 2px; }

        #inspector-hud {
            bottom: 16px;
            right: 16px;
            width: 320px;
            display: none;
            border-left: 3px solid #ff3366;
        }
        #crosshair {
            position: absolute;
            top: 50%;
            left: 50%;
            width: 12px;
            height: 12px;
            transform: translate(-50%, -50%);
            pointer-events: none;
            z-index: 5;
        }
        #crosshair::before, #crosshair::after {
            content: '';
            position: absolute;
            background: rgba(255, 215, 0, 0.4);
        }
        #crosshair::before { top: 5px; left: 0; width: 12px; height: 2px; }
        #crosshair::after { top: 0; left: 5px; width: 2px; height: 12px; }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="crosshair"></div>
    <div id="canvas-container"></div>

    <div id="header-hud" class="hud-panel">
        <h1>MLAOS-Prime // World Simulator</h1>
        <div class="subtitle">Codex Section VII: The Architecture of Residual Meaning</div>
        <div class="telemetry-row">
            <span class="telemetry-label">Immutable Merkle Root</span>
            <span id="tel-merkle" class="telemetry-value value-cyan">0x7F4C8E2B19A03D51</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Monad Gaussian Population</span>
            <span class="telemetry-value">2,300 Splats (12 Monads)</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">PoE Gas Credit Pool</span>
            <span id="tel-gas" class="telemetry-value value-gold">125 Credits</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Ensemble Torsion &lang;T&rang;</span>
            <span class="telemetry-value value-emerald">+0.4119 × 10⁻³⁵ m⁻¹</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Mean Harmonic Scar Cost</span>
            <span class="telemetry-value">0.201 / 0.300 TRIZ Limit</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Quantum Speed Headroom</span>
            <span class="telemetry-value value-cyan">6.33 × 10¹⁴ (Adiabatic)</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Cadence Pulse</span>
            <span id="tel-pulse" class="telemetry-value value-crimson">1.50 Hz Active</span>
        </div>
    </div>

    <div id="ledger-hud" class="hud-panel">
        <h2>
            <span>Ash Archive JBP Ledger</span>
            <span id="block-counter" style="color:#ffd700">8 Blocks</span>
        </h2>
        <div id="block-stream"></div>
    </div>

    <div id="inspector-hud" class="hud-panel">
        <h3 id="insp-title" style="color:#ff3366; font-size:12px; margin-bottom:4px;">INSPECTING MONAD</h3>
        <div id="insp-desc" style="color:#8892b0; margin-bottom:8px;"></div>
        <div class="telemetry-row">
            <span class="telemetry-label">Opacity (α)</span>
            <span id="insp-alpha" class="telemetry-value">--</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Horizon Temp (T_eff)</span>
            <span id="insp-temp" class="telemetry-value value-crimson">--</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Torsion Coupling (T_i)</span>
            <span id="insp-torsion" class="telemetry-value">--</span>
        </div>
        <div class="telemetry-row">
            <span class="telemetry-label">Harvested Landauer Work</span>
            <span id="insp-work" class="telemetry-value value-gold">--</span>
        </div>
    </div>

    <div id="controls-hud">
        <button class="btn active" onclick="setChamber('overview')">Full Cathedral</button>
        <button class="btn" onclick="setChamber('ch1')">Chamber I: Erasure</button>
        <button class="btn" onclick="setChamber('ch2')">Chamber II: Vaults</button>
        <button class="btn" onclick="setChamber('ch3')">Chamber III: Pamphlet</button>
        <button class="btn" onclick="setChamber('ch4')">Chamber IV: Cenotaph</button>
        <button class="btn" onclick="setChamber('ch5')">Chamber V: Scars</button>
        <button class="btn" id="btn-torsion" onclick="toggleTorsionVectors()">Toggle Torsion (T_i)</button>
        <button class="btn" onclick="triggerManualAudit()">Probe Omission (PoE Tick)</button>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let pointsMesh, torsionLinesGroup;
        let showTorsion = false;
        let gasPool = 125;
        let merkleRoot = "0x7F4C8E2B19A03D51";
        let blockCount = 0;
        let hoveredIndex = -1;

        const MONAD_DEFINITIONS = [
            { id: 1, name: "Consensus Core", count: 153, rgb: [0.85, 0.68, 0.22], alpha: 0.95, torsion: "0.00e-35 m⁻¹", desc: "Institutional Monolith enforcing temporal monism." },
            { id: 2, name: "Zone of Administrative Omission", count: 247, rgb: [0.04, 0.04, 0.06], alpha: 0.20, torsion: "+1.42e-35 m⁻¹", desc: "Substrate void margin where historical records were excised." },
            { id: 3, name: "Archaeological Excavation Lattice", count: 216, rgb: [0.12, 0.52, 0.54], alpha: 0.85, torsion: "+0.68e-35 m⁻¹", desc: "Subterranean parabolic vaults of Edinburgh Old Town." },
            { id: 4, name: "Old Town Ashlar Masonry", count: 164, rgb: [0.45, 0.38, 0.25], alpha: 0.88, torsion: "+0.12e-35 m⁻¹", desc: "Soot-blackened masonry bearing subaltern load." },
            { id: 5, name: "Subaltern Resonance Seam", count: 120, rgb: [0.10, 0.65, 0.38], alpha: 0.80, torsion: "+0.89e-35 m⁻¹", desc: "Mineral verdigris seep lines along clandestine chambers." },
            { id: 6, name: "Clandestine Pamphlet Shockwave", count: 228, rgb: [0.78, 0.12, 0.22], alpha: 0.78, torsion: "+2.10e-35 m⁻¹", desc: "Kinetic dispersion of illegal broadsheets." },
            { id: 7, name: "Procedural Worldbuilding Node", count: 222, rgb: [0.05, 0.85, 0.95], alpha: 0.82, torsion: "+0.45e-35 m⁻¹", desc: "Digital voxel lattice transducing pamphlets into virtual physics." },
            { id: 8, name: "Ash Archive Foreclosed Timeline", count: 245, rgb: [0.08, 0.18, 0.36], alpha: 0.25, torsion: "-1.15e-35 m⁻¹", desc: "Helical asymptote coils containing unlived historical paths." },
            { id: 9, name: "Chronological Nostalgia Vortex", count: 101, rgb: [0.35, 0.15, 0.55], alpha: 0.70, torsion: "-1.80e-35 m⁻¹", desc: "Collective mourning container reflecting systemic tragedy." },
            { id: 10, name: "Unlived Future Echo", count: 54, rgb: [0.92, 0.85, 0.95], alpha: 0.60, torsion: "-0.30e-35 m⁻¹", desc: "Boundary luminescence of averted historical massacres." },
            { id: 11, name: "Harmonic Scar Kintsugi Node", count: 142, rgb: [0.98, 0.85, 0.35], alpha: 0.98, torsion: "0.00e-35 m⁻¹", desc: "Non-Hermitian EP2 branch cut converting contradiction into load-bearing strength." },
            { id: 12, name: "Paraconsistent Load Strut", count: 408, rgb: [0.15, 0.18, 0.22], alpha: 0.85, torsion: "+0.55e-35 m⁻¹", desc: "Diagonal basalt compression members bridging fractured naves." }
        ];

        const TOTAL_POINTS = 2300;
        let positions = new Float32Array(TOTAL_POINTS * 3);
        let colors = new Float32Array(TOTAL_POINTS * 3);
        let baseAlphas = new Float32Array(TOTAL_POINTS);
        let monadIds = new Int32Array(TOTAL_POINTS);

        function generateManifoldData() {
            let pIdx = 0;
            function addPt(x, y, z, rgb, alpha, mId) {
                positions[pIdx * 3] = x;
                positions[pIdx * 3 + 1] = y;
                positions[pIdx * 3 + 2] = z;
                colors[pIdx * 3] = rgb[0];
                colors[pIdx * 3 + 1] = rgb[1];
                colors[pIdx * 3 + 2] = rgb[2];
                baseAlphas[pIdx] = alpha;
                monadIds[pIdx] = mId;
                pIdx++;
            }

            for (let i = 0; i < 400; i++) {
                let u = (Math.random() - 0.5) * 2.0;
                let v = (Math.random() - 0.5) * 2.0;
                let h = Math.random() * 8.0;
                let r = Math.sqrt(u*u + v*v);
                let x = u * (1.2 - 0.3 * (h / 8.0));
                let z = v * (1.2 - 0.3 * (h / 8.0));
                let y = h - 2.0;
                if (r < 0.6 && pIdx < 153) addPt(x, y, z, MONAD_DEFINITIONS[0].rgb, 0.95, 1);
                else if (pIdx < 400) addPt(x, y, z, MONAD_DEFINITIONS[1].rgb, 0.20, 2);
                else addPt(x, y, z, MONAD_DEFINITIONS[0].rgb, 0.95, 1);
            }

            for (let i = 0; i < 500; i++) {
                let theta = Math.random() * Math.PI;
                let rad = 2.5 + Math.random() * 1.0;
                let depth = (Math.random() - 0.5) * 12.0;
                let x = rad * Math.cos(theta);
                let y = rad * Math.sin(theta) - 5.0;
                let z = depth;
                let roll = Math.random();
                if (roll < 0.43) addPt(x, y, z, MONAD_DEFINITIONS[2].rgb, 0.85, 3);
                else if (roll < 0.76) addPt(x, y, z, MONAD_DEFINITIONS[3].rgb, 0.88, 4);
                else addPt(x, y, z, MONAD_DEFINITIONS[4].rgb, 0.80, 5);
            }

            for (let i = 0; i < 450; i++) {
                let phi = Math.random() * Math.PI * 2;
                let costheta = Math.random() * 2.0 - 1.0;
                let theta = Math.acos(costheta);
                let r = 2.2 * Math.cbrt(Math.random());
                let x = 7.0 + r * Math.sin(theta) * Math.cos(phi);
                let y = 1.0 + r * Math.sin(theta) * Math.sin(phi);
                let z = r * Math.cos(theta);
                if (i % 2 === 0) addPt(x, y, z, MONAD_DEFINITIONS[5].rgb, 0.78, 6);
                else addPt(x, y, z, MONAD_DEFINITIONS[6].rgb, 0.82, 7);
            }

            for (let i = 0; i < 400; i++) {
                let t = Math.random() * Math.PI * 4;
                let rad = 1.0 + 0.15 * t;
                let y = 1.0 + (t / (Math.PI * 4)) * 6.0 - 3.0;
                let x = -7.0 + rad * Math.cos(t);
                let z = rad * Math.sin(t);
                let roll = Math.random();
                if (roll < 0.61) addPt(x, y, z, MONAD_DEFINITIONS[7].rgb, 0.25, 8);
                else if (roll < 0.86) addPt(x, y, z, MONAD_DEFINITIONS[8].rgb, 0.70, 9);
                else addPt(x, y, z, MONAD_DEFINITIONS[9].rgb, 0.60, 10);
            }

            for (let i = 0; i < 550; i++) {
                let t = (Math.random() - 0.5) * 8.0;
                let branch = Math.random() > 0.5 ? 1 : -1;
                let x = t + (Math.random() - 0.5) * 0.4;
                let y = 7.0 + branch * t * 0.8 + (Math.random() - 0.5) * 0.4;
                let z = (Math.random() - 0.5) * 0.8;
                if (Math.abs(t) < 1.0 && pIdx < 2300 - 408) {
                    addPt(x, y, z, MONAD_DEFINITIONS[10].rgb, 0.98, 11);
                } else {
                    addPt(x, y, z, MONAD_DEFINITIONS[11].rgb, 0.85, 12);
                }
            }

            while (pIdx < TOTAL_POINTS) {
                addPt(0, 0, 0, [0.5, 0.5, 0.5], 0.5, 1);
            }
        }

        function initThree() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x050508, 0.035);

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 100);
            camera.position.set(0, 4, 16);

            renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.setClearColor(scene.fog.color);
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.maxDistance = 45;
            controls.minDistance = 2;

            generateManifoldData();
            const geometry = new THREE.BufferGeometry();
            geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
            geometry.setAttribute('customColor', new THREE.BufferAttribute(colors, 3));
            geometry.setAttribute('baseAlpha', new THREE.BufferAttribute(baseAlphas, 1));

            const pointsMaterial = new THREE.ShaderMaterial({
                uniforms: {
                    uTime: { value: 0.0 },
                    uAuditPulse: { value: 0.0 }
                },
                vertexShader: `
                    attribute vec3 customColor;
                    attribute float baseAlpha;
                    varying vec3 vColor;
                    varying float vAlpha;
                    uniform float uTime;
                    uniform float uAuditPulse;

                    void main() {
                        vColor = customColor;
                        vAlpha = baseAlpha;
                        if (baseAlpha < 0.35) {
                            float pulse = sin(uTime * 6.28318 * 1.5) * 0.5 + 0.5;
                            vColor = mix(customColor, vec3(1.0, 0.35, 0.08), pulse * 0.75 + uAuditPulse);
                            vAlpha = clamp(baseAlpha + pulse * 0.3 + uAuditPulse * 0.4, 0.1, 1.0);
                        }
                        vec4 mvPosition = modelViewMatrix * vec4(position, 1.0);
                        gl_PointSize = (120.0 / -mvPosition.z) * (0.8 + 0.4 * vAlpha);
                        gl_Position = projectionMatrix * mvPosition;
                    }
                `,
                fragmentShader: `
                    varying vec3 vColor;
                    varying float vAlpha;
                    void main() {
                        vec2 coord = gl_PointCoord - vec2(0.5);
                        float dist = length(coord);
                        if (dist > 0.5) discard;
                        float gaussian = exp(-dist * dist * 8.0);
                        gl_FragColor = vec4(vColor, gaussian * vAlpha);
                    }
                `,
                transparent: true,
                depthWrite: false,
                blending: THREE.AdditiveBlending
            });

            pointsMesh = new THREE.Points(geometry, pointsMaterial);
            scene.add(pointsMesh);

            buildTorsionField();

            const grid = new THREE.GridHelper(30, 30, 0xdaa520, 0x111622);
            grid.position.y = -6.0;
            scene.add(grid);

            window.addEventListener('resize', onWindowResize);
            setupRaycaster();
            seedInitialBlocks();
        }

        function buildTorsionField() {
            torsionLinesGroup = new THREE.Group();
            const lineMat = new THREE.LineBasicMaterial({
                color: 0x00f0ff,
                transparent: true,
                opacity: 0.35
            });

            for (let i = 0; i < TOTAL_POINTS; i += 8) {
                let mId = monadIds[i];
                let mDef = MONAD_DEFINITIONS[mId - 1];
                let tVal = parseFloat(mDef.torsion);
                if (Math.abs(tVal) > 0.01) {
                    let p1 = new THREE.Vector3(positions[i*3], positions[i*3+1], positions[i*3+2]);
                    let curlDir = new THREE.Vector3(
                        -p1.z * Math.sign(tVal) * 0.15,
                        Math.abs(tVal) * 0.4,
                        p1.x * Math.sign(tVal) * 0.15
                    ).normalize().multiplyScalar(0.6);
                    let p2 = p1.clone().add(curlDir);

                    let geom = new THREE.BufferGeometry().setFromPoints([p1, p2]);
                    let line = new THREE.Line(geom, lineMat);
                    torsionLinesGroup.add(line);
                }
            }
            torsionLinesGroup.visible = showTorsion;
            scene.add(torsionLinesGroup);
        }

        function toggleTorsionVectors() {
            showTorsion = !showTorsion;
            torsionLinesGroup.visible = showTorsion;
            document.getElementById('btn-torsion').classList.toggle('active', showTorsion);
        }

        let raycaster, mouse;
        function setupRaycaster() {
            raycaster = new THREE.Raycaster();
            raycaster.params.Points.threshold = 0.45;
            mouse = new THREE.Vector2();

            window.addEventListener('mousemove', (e) => {
                mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
                mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
            });
        }

        function inspectMonadAtRay() {
            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObject(pointsMesh);

            const inspHud = document.getElementById('inspector-hud');
            if (intersects.length > 0) {
                let idx = intersects[0].index;
                hoveredIndex = idx;
                let mId = monadIds[idx];
                let mDef = MONAD_DEFINITIONS[mId - 1];

                inspHud.style.display = 'block';
                document.getElementById('insp-title').innerText = `MONAD M${mId}: ${mDef.name}`;
                document.getElementById('insp-desc').innerText = mDef.desc;
                document.getElementById('insp-alpha').innerText = baseAlphas[idx].toFixed(2);
                
                let tEff = (293.15 / (baseAlphas[idx] + 0.001)).toFixed(1);
                document.getElementById('insp-temp').innerText = `${tEff} K`;
                document.getElementById('insp-torsion').innerText = mDef.torsion;
                
                let workHarvest = (1.38e-23 * parseFloat(tEff) * 0.693 * 1.5).toExponential(3);
                document.getElementById('insp-work').innerText = `${workHarvest} J`;
            } else {
                inspHud.style.display = 'none';
                hoveredIndex = -1;
            }
        }

        function triggerManualAudit() {
            let candidates = [];
            for (let i = 0; i < TOTAL_POINTS; i++) {
                if (baseAlphas[i] < 0.35) candidates.push(i);
            }
            let targetIdx = candidates[Math.floor(Math.random() * candidates.length)];
            let alpha = baseAlphas[targetIdx];
            let tHorizon = 293.15 / (alpha + 0.001);
            let work = 1.380649e-23 * tHorizon * Math.log(2) * 1.5;
            let minted = Math.max(1, Math.floor(work / 1.0e-21) + 2);

            gasPool += minted;
            document.getElementById('tel-gas').innerText = `${gasPool} Credits`;

            pointsMesh.material.uniforms.uAuditPulse.value = 0.8;
            setTimeout(() => { pointsMesh.material.uniforms.uAuditPulse.value = 0.0; }, 250);

            if (gasPool >= 60) {
                commitMerkleBlock();
            }
        }

        function commitMerkleBlock() {
            blockCount++;
            gasPool -= 60;
            document.getElementById('tel-gas').innerText = `${gasPool} Credits`;

            let prevHash = merkleRoot;
            let rawStr = prevHash + Date.now().toString() + blockCount;
            let hashNum = 0;
            for (let i = 0; i < rawStr.length; i++) {
                hashNum = (hashNum << 5) - hashNum + rawStr.charCodeAt(i);
                hashNum |= 0;
            }
            let hex = "0x" + Math.abs(hashNum).toString(16).toUpperCase().padStart(16, '0');
            merkleRoot = hex;
            document.getElementById('tel-merkle').innerText = merkleRoot;
            document.getElementById('block-counter').innerText = `${blockCount} Blocks`;

            const stream = document.getElementById('block-stream');
            const card = document.createElement('div');
            card.className = 'block-card';
            card.innerHTML = `
                <div class="block-hash">Block #${blockCount}: ${hex}</div>
                <div class="block-meta">Nodes: 30 | Fee: 60 Credits | Proof: THERMODYNAMIC</div>
            `;
            stream.insertBefore(card, stream.firstChild);
            if (stream.children.length > 5) {
                stream.removeChild(stream.lastChild);
            }
        }

        function seedInitialBlocks() {
            for (let i = 1; i <= 3; i++) {
                commitMerkleBlock();
            }
        }

        function setChamber(name) {
            const buttons = document.querySelectorAll('#controls-hud button.btn');
            buttons.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');

            if (name === 'overview') smoothMoveCamera(0, 4, 18, 0, 1, 0);
            else if (name === 'ch1') smoothMoveCamera(0, 2, 8, 0, 1, 0);
            else if (name === 'ch2') smoothMoveCamera(0, -5, 10, 0, -4, 0);
            else if (name === 'ch3') smoothMoveCamera(7, 2, 7, 7, 1, 0);
            else if (name === 'ch4') smoothMoveCamera(-7, 2, 7, -7, 1, 0);
            else if (name === 'ch5') smoothMoveCamera(0, 7, 8, 0, 6, 0);
        }

        function smoothMoveCamera(px, py, pz, tx, ty, tz) {
            let startPos = camera.position.clone();
            let targetPos = new THREE.Vector3(px, py, pz);
            let startTarget = controls.target.clone();
            let targetTarget = new THREE.Vector3(tx, ty, tz);
            let alpha = 0;

            function anim() {
                alpha += 0.04;
                camera.position.lerpVectors(startPos, targetPos, alpha);
                controls.target.lerpVectors(startTarget, targetTarget, alpha);
                if (alpha < 1.0) requestAnimationFrame(anim);
            }
            anim();
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        let clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            let elapsedTime = clock.getElapsedTime();

            if (pointsMesh) {
                pointsMesh.material.uniforms.uTime.value = elapsedTime;
            }

            pointsMesh.rotation.y = elapsedTime * 0.025;
            if (torsionLinesGroup) torsionLinesGroup.rotation.y = elapsedTime * 0.025;

            controls.update();
            inspectMonadAtRay();
            renderer.render(scene, camera);
        }

        setInterval(() => {
            const pElem = document.getElementById('tel-pulse');
            pElem.style.opacity = pElem.style.opacity === '0.4' ? '1.0' : '0.4';
        }, 333);

        window.onload = () => {
            initThree();
            animate();
        };
    </script>
</body>
</html>
"""

with open("cathedral_world_simulator.html", "w", encoding="utf-8") as f:
    f.write(html_content)

server_script = """#!/usr/bin/env python3
import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080

class Handler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    print(f"=== CATHEDRAL WORLD SIMULATOR ACTIVE ===")
    print(f"Target URL: http://localhost:{PORT}/cathedral_world_simulator.html")
    if "--open" in sys.argv:
        webbrowser.open(f"http://localhost:{PORT}/cathedral_world_simulator.html")
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\\nSimulator server stopped.")
"""

with open("cathedral_world_simulator.py", "w", encoding="utf-8") as f:
    f.write(server_script)

print("Created cathedral_world_simulator.html")
print("Created cathedral_world_simulator.py")
