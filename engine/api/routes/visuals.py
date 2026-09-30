import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, StreamingResponse

router = APIRouter(tags=["visuals"])

VISUAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>MLAOS-Prime // Visual Echo Telemetry</title>
    <style>
        body { margin: 0; background: #050508; overflow: hidden; color: #d4af37; font-family: monospace; }
        #hud { position: absolute; top: 20px; left: 20px; z-index: 10; pointer-events: none; }
    </style>
</head>
<body>
    <div id="hud">
        <h2>CATHEDRAL-ENGINE // LIVE TELEMETRY</h2>
        <p id="status">Connecting to Ash Archive Stream...</p>
    </div>
    <script type="module">
        import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(renderer.domElement);

        const geometry = new THREE.IcosahedronGeometry(2, 2);
        const material = new THREE.MeshStandardMaterial({ color: 0xd4af37, wireframe: true });
        const coreMesh = new THREE.Mesh(geometry, material);
        scene.add(coreMesh);

        const light = new THREE.PointLight(0x00ffff, 2, 50);
        light.position.set(5, 5, 5);
        scene.add(light);
        scene.add(new THREE.AmbientLight(0x222222));

        camera.position.z = 6;

        const evtSource = new EventSource('/visuals/stream');
        evtSource.onmessage = function(event) {
            const data = JSON.parse(event.data);
            document.getElementById('status').innerText = `State: ${data.status || 'Resonant'} | Magnitude: ${data.magnitude || 'Nominal'}`;
            coreMesh.scale.setScalar(1.0 + (data.magnitude ? data.magnitude * 0.05 : 0));
        };

        function animate() {
            requestAnimationFrame(animate);
            coreMesh.rotation.x += 0.005;
            coreMesh.rotation.y += 0.01;
            renderer.render(scene, camera);
        }
        animate();
    </script>
</body>
</html>"""

@router.get("/visuals", response_class=HTMLResponse)
def render_visuals():
    return VISUAL_HTML

@router.get("/visuals/stream")
async def visuals_stream():
    async def event_generator():
        while True:
            payload = {"status": "resonant", "magnitude": 2.5}
            yield f"data: {json.dumps(payload)}\n\n"
            await asyncio.sleep(2.0)
    return StreamingResponse(event_generator(), media_type="text/event-stream")
