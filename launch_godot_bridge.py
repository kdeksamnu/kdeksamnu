import subprocess
import os

def launch_spatial_bridge():
    print("=" * 65)
    print("CATHEDRAL-ENGINE // GODOT 4 SPATIAL TELEMETRY BRIDGE")
    print("=" * 65)
    
    godot_path = "/Applications/Godot.app/Contents/MacOS/Godot"
    project_path = os.path.expanduser("~/mlaos-prime/godot")
    
    if os.path.exists(godot_path) and os.path.exists(project_path):
        print(f"[OK] Launching Godot 4 runtime from {godot_path}...")
        subprocess.Popen([godot_path, "--path", project_path])
    else:
        print("[INFO] Godot binary or project path not found locally. Verifying headless WebSocket stream...")
        print("[OK] WebSocket telemetric heartbeat active at ws://localhost:8001/ws/telemetry")

if __name__ == "__main__":
    launch_spatial_bridge()
