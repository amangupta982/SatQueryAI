#!/bin/bash
# start-dev.sh — Start both the SatQueryAI main frontend and the 3D View dev servers.
#
# Usage:
#   ./start-dev.sh
#
# This starts:
#   1. 3D View Vite server on port 4173
#   2. Main SatQueryAI frontend on port 5173
#
# Open http://localhost:5173 to use the application.
# Click "3D View" in the navbar to see the existing 3D application.
#
# Press Ctrl+C to stop both servers.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Cleanup: kill background processes on exit
cleanup() {
  echo ""
  echo "Shutting down dev servers..."
  kill $PID_BACKEND 2>/dev/null || true
  kill $PID_3D 2>/dev/null || true
  kill $PID_MAIN 2>/dev/null || true
  wait $PID_BACKEND 2>/dev/null || true
  wait $PID_3D 2>/dev/null || true
  wait $PID_MAIN 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

# Gracefully free ports 5173, 4173, 8000 if occupied by previous runs
for p in 5173 4173 8000; do
  pid=$(lsof -ti :$p 2>/dev/null || true)
  if [ -n "$pid" ]; then
    kill -9 $pid 2>/dev/null || true
  fi
done

echo "Starting SatQuery AI services in the background..."

# 1. Start FastAPI Backend in background
PYTHON_BIN="$SCRIPT_DIR/venv/bin/python3"
if [ ! -f "$PYTHON_BIN" ]; then
  PYTHON_BIN="python3"
fi
$PYTHON_BIN -m uvicorn frontend_backend.backend.main:app --host 0.0.0.0 --port 8000 --reload > "$SCRIPT_DIR/.backend.log" 2>&1 &
PID_BACKEND=$!

# 2. Start 3D View engine quietly in background (logs to .3dview.log)
(cd "$SCRIPT_DIR/3d-view" && npm run dev > /dev/null 2>&1) &
PID_3D=$!

# 3. Start SatQuery AI Main Frontend
(cd "$SCRIPT_DIR/frontend_backend/frontend" && npm run dev > /dev/null 2>&1) &
PID_MAIN=$!

# Wait for frontend port 5173 to be ready
sleep 2

echo ""
echo "=================================================================="
echo "  🚀 ALL ENGINES CONNECTED! ACCESS EVERYTHING AT THIS ONE LINK:"
echo ""
echo "  👉 http://localhost:5173"
echo ""
echo "  (Do not open any other ports — everything is unified here:)"
echo "  • Visual Question Answering (Upload Image & Ask Questions)"
echo "  • Interactive Earth Observation Dashboard"
echo "  • 3D Satellite Globe (embedded under '3D View')"
echo "  • AI-Powered Analysis Studio & Datasets"
echo ""
echo "  Press Ctrl+C to stop all servers."
echo "=================================================================="
echo ""

# Automatically open the one link in the default browser on macOS
if command -v open >/dev/null 2>&1; then
  open http://localhost:5173 2>/dev/null || true
fi

# Wait for processes to exit
wait
