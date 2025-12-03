#!/usr/bin/env bash
set -e

echo "[entrypoint] Starting Ollama server..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama server to be ready
echo "[entrypoint] Waiting for Ollama server to start..."
for i in {1..30}; do
  if curl -s http://127.0.0.1:11434/api/tags > /dev/null 2>&1; then
    echo "[entrypoint] Ollama server is ready"
    break
  fi
  if [ $i -eq 30 ]; then
    echo "[entrypoint] ERROR: Ollama server failed to start"
    exit 1
  fi
  sleep 1
done

# Check if model exists, pull if not
echo "[entrypoint] Checking for llama3.1 model..."
if ! ollama list 2>/dev/null | grep -q "llama3.1"; then
  echo "[entrypoint] Pulling llama3.1 model..."
  ollama pull llama3.1
else
  echo "[entrypoint] llama3.1 model already exists"
fi

echo "[entrypoint] Starting Node server..."
node dist/server.js &
NODE_PID=$!

# Handle shutdown gracefully
trap "echo '[entrypoint] Stopping services...'; kill $NODE_PID $OLLAMA_PID 2>/dev/null || true; wait; exit 0" SIGTERM SIGINT

wait $NODE_PID