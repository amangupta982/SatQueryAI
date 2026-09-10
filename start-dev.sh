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
  kill $PID_3D 2>/dev/null || true
  kill $PID_MAIN 2>/dev/null || true
  wait $PID_3D 2>/dev/null || true
  wait $PID_MAIN 2>/dev/null || true
  echo "Done."
}
trap cleanup EXIT INT TERM

echo "Starting 3D View dev server (port 4173)..."
cd "$SCRIPT_DIR/3d-view"
npm run dev &
PID_3D=$!

# Give the 3D server a moment to start
sleep 2

echo ""
echo "Starting SatQueryAI main frontend (port 5173)..."
cd "$SCRIPT_DIR/frontend_backend/frontend"
npm run dev &
PID_MAIN=$!

echo ""
echo "============================================"
echo "  Both dev servers are starting."
echo ""
echo "  Main app:  http://localhost:5173"
echo "  3D View:   http://localhost:4173 (standalone)"
echo ""
echo "  Click '3D View' in the navbar to see the"
echo "  3D application embedded in the main app."
echo ""
echo "  Press Ctrl+C to stop both servers."
echo "============================================"
echo ""

# Wait for either process to exit
wait
