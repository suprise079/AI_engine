#!/usr/bin/env bash
set -e

# echo "[entrypoint] Checking for llama3.1 model..."

# # Ensure model exists (only pulls if not already on volume)
# if ! ollama list 2>/dev/null | grep -q "llama3.1"; then
#   echo "[entrypoint] Pulling llama3.1 model (first run only)..."
#   ollama pull llama3.1
# fi

# echo "[entrypoint] Starting Ollama server..."
# ollama serve &
# OLLAMA_PID=$!

# # Give Ollama a moment to start
# sleep 3

echo "[entrypoint] Starting Node server..."
node dist/server.js &
NODE_PID=$!

# Handle shutdown gracefully
trap "echo '[entrypoint] Stopping services...'; kill $NODE_PID $OLLAMA_PID 2>/dev/null || true; wait; exit 0" SIGTERM SIGINT

wait $NODE_PID


