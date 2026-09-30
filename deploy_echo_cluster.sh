#!/usr/bin/env bash
set -e

echo "[CATHEDRAL-ENGINE] Initializing Visual Echo Fork Cluster..."

# 1. Start the FastAPI Fork Backend on port 8001
echo "[+] Spinning up Observer Fork API (Port 8001)..."
python3 duplicate_observer_core.py &
BACKEND_PID=$!

sleep 2

# 2. Start the Static Viewport Client Server on port 8090 (avoiding port 8000 collision)
echo "[+] Spawning Viewport Mirror Client (Port 8090)..."
python3 -m http.server 8090 &
FRONTEND_PID=$!

# 3. Initialize the Ash Archive Sync Daemon
echo "[+] Activating Merkle DAG Sync Daemon..."
python3 ash_archive_sync_daemon.py &
DAEMON_PID=$!

echo "------------------------------------------------------------------"
echo "[STATUS] Cluster operational."
echo "         - Backend API:       http://localhost:8001/docs"
echo "         - Viewport Mirror:   http://localhost:8090/observer_client.html"
echo "         - Vault Ledger:      ash_archive_vault.db"
echo "------------------------------------------------------------------"
echo "Press [CTRL+C] to terminate all cluster nodes."

trap "kill $BACKEND_PID $FRONTEND_PID $DAEMON_PID; echo '[SHUTDOWN] Cluster disengaged.'; exit 0" SIGINT SIGTERM

wait
