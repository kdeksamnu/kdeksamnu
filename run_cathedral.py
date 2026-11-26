#!/usr/bin/env python3
"""
Cathedral-Engine // MLAOS-Prime Unified Runtime Deck Launcher
Unifies the FastAPI substrate with all 3D WebGL / Three.js visualizers.
"""

import os
import sys
import webbrowser
import threading
import time
from pathlib import Path
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import existing application substrate
from engine.main import app

# 1. Enable Universal CORS for WebGL/Three.js clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount nebula directory for nested 3D simulations
# Mount compiled Vite + TypeScript Three.js bundle
dist_path = Path("engine/static/dist")
if dist_path.exists():
    app.mount("/studio", StaticFiles(directory=str(dist_path), html=True), name="studio")

if Path("nebula").exists():
    app.mount("/nebula", StaticFiles(directory="nebula", html=True), name="nebula")

# 3. Serve root HTML visualizers dynamically
@app.get("/{filename}.html")
def serve_root_html(filename: str):
    file_path = Path(f"{filename}.html")
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail=f"Visualizer {filename}.html not found.")

# 4. Master Portal UI
PORTAL_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Cathedral-Engine // Unified Runtime Deck</title>
    <style>
        :root {
            --bg-void: #07070a;
            --bg-panel: #0f0f15;
            --bg-surface: #171722;
            --border-subtle: #242436;
            --accent-cyan: #00e5ff;
            --accent-violet: #a855f7;
            --accent-gold: #fbbf24;
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            background-color: var(--bg-void);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", monospace;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* Top HUD Telemetry Bar */
        header {
            background-color: var(--bg-panel);
            border-bottom: 1px solid var(--border-subtle);
            padding: 8px 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            height: 48px;
            flex-shrink: 0;
        }

        .brand-cluster {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .brand-title {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.08em;
            color: var(--text-primary);
            text-transform: uppercase;
        }

        .badge {
            font-size: 11px;
            padding: 2px 8px;
            border-radius: 4px;
            background: var(--bg-surface);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            font-family: monospace;
        }

        .telemetry-strip {
            display: flex;
            align-items: center;
            gap: 14px;
            font-size: 12px;
            font-family: monospace;
        }

        .status-indicator {
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: #10b981;
            box-shadow: 0 0 8px #10b981;
        }

        /* Navigation Deck Bar */
        nav {
            background-color: var(--bg-surface);
            border-bottom: 1px solid var(--border-subtle);
            padding: 0 12px;
            display: flex;
            align-items: center;
            gap: 4px;
            height: 38px;
            flex-shrink: 0;
            overflow-x: auto;
        }

        .nav-tab {
            background: transparent;
            border: none;
            color: var(--text-secondary);
            padding: 6px 12px;
            font-size: 12px;
            font-weight: 500;
            border-radius: 4px;
            cursor: pointer;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            transition: all 0.15s ease;
            white-space: nowrap;
        }

        .nav-tab:hover {
            color: var(--text-primary);
            background-color: rgba(255, 255, 255, 0.05);
        }

        .nav-tab.active {
            color: var(--accent-cyan);
            background-color: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            box-shadow: inset 0 1px 0 rgba(0, 229, 255, 0.3);
        }

        .nav-actions {
            margin-left: auto;
            display: flex;
            gap: 6px;
        }

        .action-btn {
            background: var(--bg-panel);
            border: 1px solid var(--border-subtle);
            color: var(--text-secondary);
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            cursor: pointer;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 4px;
        }

        .action-btn:hover {
            color: var(--text-primary);
            border-color: var(--accent-cyan);
        }

        /* Main Viewport Container */
        main {
            flex: 1;
            position: relative;
            background-color: #000;
        }

        iframe {
            width: 100%;
            height: 100%;
            border: none;
            display: block;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand-cluster">
            <span class="brand-title">Cathedral-Engine // MLAOS-Prime</span>
            <span class="badge">v1.0.0</span>
            <span class="badge" style="color: var(--accent-violet);">Lattice: FOUR {T, F, B, N}</span>
        </div>
        <div class="telemetry-strip">
            <div class="status-indicator">
                <span class="status-dot" id="status-dot"></span>
                <span id="substrate-status" style="color: #10b981;">RESONANT</span>
            </div>
            <span class="badge" id="ping-badge">LATENCY: -- ms</span>
            <span class="badge" style="color: var(--accent-gold);">Lex I: Append-Only</span>
        </div>
    </header>

    <nav>
        <button class="nav-tab active" onclick="loadFrame('/studio', this)">
            ⚡ Modular 3D Studio (Vite)
        </button>
        <button class="nav-tab" onclick="loadFrame('/nebula/New/cathedral_3d_studio_runtime_deck.html', this)">
            🏛️ 3D Studio Runtime Deck
        </button>
        <button class="nav-tab" onclick="loadFrame('/nebula/New/cathedral_world_simulator.html', this)">
            🌌 World Simulator
        </button>
        <button class="nav-tab" onclick="loadFrame('/cathedral_mesh.html', this)">
            🕸️ Spectral Mesh Router
        </button>
        <button class="nav-tab" onclick="loadFrame('/visualizer.html', this)">
            💎 Ash Archive 3D
        </button>
        <button class="nav-tab" onclick="loadFrame('/observer_client.html', this)">
            👁️ Observer Telemetry
        </button>
        <button class="nav-tab" onclick="loadFrame('/nebula/planet_neuro_simulator.html', this)">
            🪐 Neuro Simulator
        </button>
        <button class="nav-tab" onclick="loadFrame('/spatial/extract?resolution=64', this)">
            📐 Spatial Voxel Stratum
        </button>
        <button class="nav-tab" onclick="loadFrame('/docs', this)">
            ⚡ API Swagger Docs
        </button>

        <div class="nav-actions">
            <a id="popout-link" href="/nebula/New/cathedral_3d_studio_runtime_deck.html" target="_blank" class="action-btn" title="Open in separate tab">
                Popout ↗
            </a>
            <button onclick="reloadFrame()" class="action-btn" title="Reload viewport">
                Reload ↻
            </button>
        </div>
    </nav>

    <main>
        <iframe id="viewport-frame" src="/studio" allow="accelerometer; camera; gyroscope; microphone; xr-spatial-tracking"></iframe>
    </main>

    <script>
        const frame = document.getElementById('viewport-frame');
        const popout = document.getElementById('popout-link');
        const statusEl = document.getElementById('substrate-status');
        const pingEl = document.getElementById('ping-badge');

        function loadFrame(url, btn) {
            frame.src = url;
            popout.href = url;
            document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
            if (btn) btn.classList.add('active');
        }

        function reloadFrame() {
            frame.src = frame.src;
        }

        async function pollTelemetry() {
            const start = performance.now();
            try {
                const res = await fetch('/health');
                const data = await res.json();
                const latency = Math.round(performance.now() - start);
                statusEl.innerText = (data.status || 'ONLINE').toUpperCase();
                pingEl.innerText = `LATENCY: ${latency} ms`;
            } catch (err) {
                statusEl.innerText = 'DISCONNECTED';
                statusEl.style.color = '#ef4444';
                pingEl.innerText = 'LATENCY: ERR';
            }
        }

        setInterval(pollTelemetry, 3000);
        pollTelemetry();
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def index_portal():
    return PORTAL_HTML

def open_browser():
    time.sleep(1.2)
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == "__main__":
    print("=" * 66)
    print(" CATHEDRAL-ENGINE // UNIFIED RUNTIME CONSOLE")
    print(" Launching FastAPI Substrate + WebGL/Three.js Visualizers...")
    print(" Console URL: http://127.0.0.1:8000/")
    print("=" * 66)
    
    threading.Thread(target=open_browser, daemon=True).start()
    uvicorn.run("run_cathedral:app", host="127.0.0.1", port=8000, reload=False)
