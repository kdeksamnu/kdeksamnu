#!/usr/bin/env python3
import os

html_code = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cathedral-Engine // Planet Sol-Omega (Neural Connectome Simulator)</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            background-color: #030306;
            color: #d8e0ee;
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
        .hud {
            position: absolute;
            z-index: 10;
            background: rgba(10, 14, 22, 0.85);
            backdrop-filter: blur(14px);
            border: 1px solid rgba(218, 165, 32, 0.3);
            border-radius: 6px;
            padding: 14px 18px;
            font-size: 11px;
            letter-spacing: 0.5px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.8);
        }
        #header-hud {
            top: 16px;
            left: 16px;
            width: 380px;
            border-left: 3px solid #00f0ff;
        }
        #header-hud h1 {
            font-size: 13px;
            color: #00f0ff;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            margin-bottom: 4px;
        }
        .subtitle { font-size: 9.5px; color: #8892b0; margin-bottom: 8px; }
        .row { display: flex; justify-content: space-between; margin: 3px 0; padding-bottom: 2px; border-bottom: 1px solid rgba(255,255,255,0.05); }
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
        #neural-hud h2 {
            font-size: 11px;
            color: #ffd700;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
            display: flex;
            justify-content: space-between;
        }
        #neural-canvas {
            width: 100%;
            height: 180px;
            background: rgba(5, 7, 12, 0.9);
            border: 1px solid rgba(255, 215, 0, 0.2);
            border-radius: 4px;
            margin-bottom: 8px;
        }

        #controls-hud {
            bottom: 16px;
            left: 16px;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            max-width: 650px;
        }
        button.btn {
            background: rgba(20, 26, 40, 0.85);
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
        }
        button.btn.active {
            background: #daa520;
            color: #050508;
            font-weight: bold;
        }

        #status-ticker {
            bottom: 16px;
            right: 16px;
            width: 320px;
            font-size: 10px;
            font-family: monospace;
            border-left: 3px solid #00ff88;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="canvas-container"></div>

    <div id="header-hud" class="hud">
        <h1>Cathedral-Engine // Planet Sol-Omega</h1>
        <div class="subtitle">Autonomous Entities via Neural Connectome Mapping</div>
        <div class="row"><span class="lbl">Planetary Radius</span><span class="val">R = 10.0 Units</span></div>
        <div class="row"><span class="lbl">Inhabitant Population</span><span id="tel-pop" class="val emerald">160 Entities</span></div>
        <div class="row"><span class="lbl">Mean Plasticity (η)</span><span class="val cyan">0.050 / tick</span></div>
        <div class="row"><span class="lbl">Metabolic Burn Rate</span><span class="val gold">4.48 × 10⁻¹⁹ J/s</span></div>
        <div class="row"><span class="lbl">Chiral Torsion Field</span><span class="val emerald">+0.412 × 10⁻³⁵ m⁻¹</span></div>
    </div>

    <div id="neural-hud" class="hud">
        <h2>
            <span>Mind Neuro-Map</span>
            <span id="entity-id-tag" class="gold">Entity #001</span>
        </h2>
        <canvas id="neural-canvas" width="280" height="180"></canvas>
        <div class="row"><span class="lbl">Somatic Energy</span><span id="neu-energy" class="val emerald">94.2 %</span></div>
        <div class="row"><span class="lbl">Epistemic Debt</span><span id="neu-debt" class="val">0.08</span></div>
        <div class="row"><span class="lbl">Active Drive</span><span id="neu-drive" class="val cyan">FORAGING</span></div>
        <div class="row"><span class="lbl">Belnap State</span><span id="neu-belnap" class="val gold">TRUE (Consensus)</span></div>
    </div>

    <div id="status-ticker" class="hud">
        <div style="color:#00ff88; font-weight:bold; margin-bottom:4px;">COGNITIVE STATE STREAM</div>
        <div id="ticker-msg">Inhabitants self-organizing along Emerald biomass equator.</div>
    </div>

    <div id="controls-hud">
        <button class="btn active" onclick="setSpeed(1)">Normal Flow</button>
        <button class="btn" onclick="setSpeed(2.5)">Fast Forward (2.5x)</button>
        <button class="btn" onclick="spawnColony()">Spawn Micro-Colony (+20)</button>
        <button class="btn" onclick="triggerBiomassBloom()">Seed Biomass Bloom</button>
        <button class="btn" onclick="inspectRandom()">Track Random Entity</button>
    </div>

    <script>
        let scene, camera, renderer, controls;
        let planetMesh, atmosphereMesh;
        let PLANET_RADIUS = 10.0;
        let simSpeed = 1.0;

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

        class Entity {
            constructor(id, lat, lon) {
                this.id = id;
                this.lat = lat;
                this.lon = lon;
                this.heading = Math.random() * Math.PI * 2;
                this.speed = 0.008 + Math.random() * 0.006;
                this.energy = 80 + Math.random() * 20;
                this.debt = Math.random() * 0.15;
                this.belnap = "TRUE";
                this.brain = new NeuralBrain();

                this.mesh = new THREE.Mesh(
                    new THREE.ConeGeometry(0.18, 0.45, 4),
                    new THREE.MeshBasicMaterial({ color: 0x00ff88 })
                );
                scene.add(this.mesh);
                this.updatePosition();
            }

            updatePosition() {
                let phi = (90 - this.lat) * (Math.PI / 180);
                let theta = (this.lon + 180) * (Math.PI / 180);
                let r = PLANET_RADIUS + 0.14;
                let x = -(r * Math.sin(phi) * Math.cos(theta));
                let z = (r * Math.sin(phi) * Math.sin(theta));
                let y = (r * Math.cos(phi));
                this.mesh.position.set(x, y, z);

                let normal = new THREE.Vector3(x, y, z).normalize();
                this.mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
            }

            step(dt) {
                let slope = Math.sin(this.lat * 0.1) * 0.5;
                let distToEmerald = Math.abs(Math.sin(this.lon * 0.05));
                let hazard = (Math.abs(this.lat) > 60) ? 0.85 : 0.1;
                let energySensor = this.energy / 100.0;
                let torsionSensor = 0.412;
                let memorySensor = 1.0 - this.debt;

                let inputs = [slope, distToEmerald, hazard, energySensor, torsionSensor, memorySensor];
                let outputs = this.brain.forward(inputs);

                let thrust = (outputs[0] + 1.0) * 0.5;
                let yaw = outputs[1] * 0.15;
                let harvestAction = outputs[2] > 0.3;

                this.heading += yaw * dt;
                this.lat += Math.cos(this.heading) * this.speed * thrust * 40.0 * dt;
                this.lon += Math.sin(this.heading) * this.speed * thrust * 40.0 * dt;

                if (this.lat > 85) { this.lat = 85; this.heading += Math.PI; }
                if (this.lat < -85) { this.lat = -85; this.heading += Math.PI; }
                this.lon = (this.lon + 360) % 360;

                this.energy -= (0.04 * thrust + 0.01) * dt;

                let reward = 0;
                if (distToEmerald < 0.35 && harvestAction) {
                    this.energy = Math.min(100, this.energy + 0.4 * dt);
                    reward = +0.12;
                } else if (hazard > 0.5) {
                    this.energy -= 0.12 * dt;
                    reward = -0.15;
                    this.debt = Math.min(1.0, this.debt + 0.02 * dt);
                }

                if (this.debt > 0.45) {
                    this.belnap = "BOTH";
                    this.mesh.material.color.setHex(0xffd700);
                } else {
                    this.belnap = "TRUE";
                    this.mesh.material.color.setHex(0x00ff88);
                }

                this.brain.adapt(reward);
                this.updatePosition();
            }

            destroy() {
                scene.remove(this.mesh);
            }
        }

        let entities = [];
        let selectedEntity = null;

        function init() {
            const container = document.getElementById('canvas-container');
            scene = new THREE.Scene();

            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.set(0, 8, 28);

            renderer = new THREE.WebGLRenderer({ antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            container.appendChild(renderer.domElement);

            controls = new THREE.OrbitControls(camera, renderer.domElement);
            controls.enableDamping = true;
            controls.dampingFactor = 0.05;
            controls.minDistance = 12;
            controls.maxDistance = 60;

            const planetGeom = new THREE.SphereGeometry(PLANET_RADIUS, 64, 64);
            const planetMat = new THREE.ShaderMaterial({
                vertexShader: `
                    varying vec3 vNormal;
                    varying vec3 vPos;
                    void main() {
                        vNormal = normalize(normalMatrix * normal);
                        vPos = position;
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }
                `,
                fragmentShader: `
                    varying vec3 vNormal;
                    varying vec3 vPos;
                    void main() {
                        float lat = vPos.y / 10.0;
                        vec3 col = vec3(0.08, 0.12, 0.18);
                        if (abs(lat) > 0.75) {
                            col = vec3(0.03, 0.03, 0.05);
                        } else if (abs(lat) < 0.25) {
                            col = vec3(0.05, 0.45, 0.25);
                        } else if (lat > 0.25 && lat < 0.55) {
                            col = vec3(0.65, 0.52, 0.18);
                        } else {
                            col = vec3(0.10, 0.38, 0.42);
                        }
                        vec3 lightDir = normalize(vec3(1.0, 1.0, 1.0));
                        float diff = max(dot(vNormal, lightDir), 0.05);
                        gl_FragColor = vec4(col * diff + col * 0.18, 1.0);
                    }
                `
            });
            planetMesh = new THREE.Mesh(planetGeom, planetMat);
            scene.add(planetMesh);

            const atmosGeom = new THREE.SphereGeometry(PLANET_RADIUS * 1.06, 32, 32);
            const atmosMat = new THREE.ShaderMaterial({
                vertexShader: `
                    varying vec3 vNormal;
                    void main() {
                        vNormal = normalize(normalMatrix * normal);
                        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
                    }
                `,
                fragmentShader: `
                    varying vec3 vNormal;
                    void main() {
                        float intensity = pow(0.65 - dot(vNormal, vec3(0, 0, 1.0)), 2.5);
                        gl_FragColor = vec4(0.0, 0.85, 1.0, 1.0) * intensity * 0.65;
                    }
                `,
                blending: THREE.AdditiveBlending,
                side: THREE.BackSide,
                transparent: true
            });
            atmosphereMesh = new THREE.Mesh(atmosGeom, atmosMat);
            scene.add(atmosphereMesh);

            createStarfield();

            for (let i = 0; i < 160; i++) {
                let lat = (Math.random() - 0.5) * 140.0;
                let lon = Math.random() * 360.0;
                entities.push(new Entity(i + 1, lat, lon));
            }
            selectedEntity = entities[0];

            window.addEventListener('resize', onWindowResize);
            animate();
        }

        function createStarfield() {
            const starGeom = new THREE.BufferGeometry();
            const starCount = 1200;
            const starPos = new Float32Array(starCount * 3);
            for (let i = 0; i < starCount * 3; i += 3) {
                let r = 90 + Math.random() * 50;
                let u = Math.random(), v = Math.random();
                let theta = u * 2.0 * Math.PI;
                let phi = Math.acos(2.0 * v - 1.0);
                starPos[i] = r * Math.sin(phi) * Math.cos(theta);
                starPos[i+1] = r * Math.sin(phi) * Math.sin(theta);
                starPos[i+2] = r * Math.cos(phi);
            }
            starGeom.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
            scene.add(new THREE.Points(starGeom, new THREE.PointsMaterial({ color: 0x8892b0, size: 0.8 })));
        }

        function onWindowResize() {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }

        function drawNeuralConnectome() {
            const canvas = document.getElementById('neural-canvas');
            const ctx = canvas.getContext('2d');
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            if (!selectedEntity) return;
            const brain = selectedEntity.brain;

            const layerX = [35, 140, 245];
            const inY = [25, 50, 75, 100, 125, 155];
            const hidY = [40, 75, 110, 145];
            const outY = [50, 90, 130];

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
                ctx.arc(x, y, 6, 0, Math.PI * 2);
                let alpha = Math.min(1.0, Math.abs(val) + 0.2);
                ctx.fillStyle = val >= 0 ? `rgba(0, 255, 136, ${alpha})` : `rgba(255, 51, 102, ${alpha})`;
                ctx.fill();
                ctx.strokeStyle = '#e6f1ff';
                ctx.lineWidth = 1;
                ctx.stroke();

                ctx.fillStyle = '#8892b0';
                ctx.font = '8px monospace';
                ctx.fillText(label, x - 18, y + 15);
            }

            for (let i = 0; i < 6; i++) drawNode(layerX[0], inY[i], brain.inputs[i], INPUT_LABELS[i]);
            for (let j = 0; j < 4; j++) drawNode(layerX[1], hidY[j], brain.hidden[j], `H${j+1}`);
            for (let k = 0; k < 3; k++) drawNode(layerX[2], outY[k], brain.outputs[k], OUTPUT_LABELS[k]);
        }

        let lastTime = performance.now();
        function animate() {
            requestAnimationFrame(animate);
            let now = performance.now();
            let dt = Math.min(0.1, (now - lastTime) / 1000.0) * simSpeed;
            lastTime = now;

            planetMesh.rotation.y += 0.002 * simSpeed;

            for (let i = entities.length - 1; i >= 0; i--) {
                let e = entities[i];
                e.step(dt);
                if (e.energy <= 0) {
                    e.destroy();
                    entities.splice(i, 1);
                    document.getElementById('ticker-msg').innerText = `Entity #${e.id} exhausted. Recycled into Ash.`;
                }
            }

            document.getElementById('tel-pop').innerText = `${entities.length} Entities`;

            if (selectedEntity) {
                document.getElementById('entity-id-tag').innerText = `Entity #${selectedEntity.id}`;
                document.getElementById('neu-energy').innerText = `${selectedEntity.energy.toFixed(1)} %`;
                document.getElementById('neu-debt').innerText = selectedEntity.debt.toFixed(2);
                document.getElementById('neu-belnap').innerText = selectedEntity.belnap;
                let dominant = "FORAGING";
                if (selectedEntity.debt > 0.45) dominant = "DIALETHEIC_STABILIZATION";
                else if (selectedEntity.energy < 30) dominant = "ENERGY_CRITICAL";
                document.getElementById('neu-drive').innerText = dominant;
            }

            drawNeuralConnectome();
            controls.update();
            renderer.render(scene, camera);
        }

        function setSpeed(s) {
            simSpeed = s;
            const btns = document.querySelectorAll('#controls-hud button.btn');
            btns.forEach(b => b.classList.remove('active'));
            event.target.classList.add('active');
        }

        function spawnColony() {
            let baseId = entities.length > 0 ? entities[entities.length - 1].id + 1 : 1;
            for (let i = 0; i < 20; i++) {
                let lat = (Math.random() - 0.5) * 40.0;
                let lon = Math.random() * 360.0;
                entities.push(new Entity(baseId + i, lat, lon));
            }
            document.getElementById('ticker-msg').innerText = `Spawned micro-colony of 20 autonomous entities.`;
        }

        function triggerBiomassBloom() {
            entities.forEach(e => { e.energy = Math.min(100, e.energy + 25); });
            document.getElementById('ticker-msg').innerText = `Equatorial Emerald Biomass bloom triggered.`;
        }

        function inspectRandom() {
            if (entities.length > 0) {
                selectedEntity = entities[Math.floor(Math.random() * entities.length)];
                document.getElementById('ticker-msg').innerText = `Focused tracking on Entity #${selectedEntity.id}.`;
            }
        }

        window.onload = init;
    </script>
</body>
</html>
"""

with open("planet_neuro_simulator.html", "w", encoding="utf-8") as f:
    f.write(html_code)

print("Planet Sol-Omega simulator successfully written to planet_neuro_simulator.html")
