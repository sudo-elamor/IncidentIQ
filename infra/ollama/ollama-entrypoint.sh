#!/bin/sh
set -e

echo "Starting Ollama server..."
ollama serve &

# Wait until Ollama API is up
until curl -s http://localhost:11434/api/tags >/dev/null; do
  sleep 1
done

MODEL=${OLLAMA_MODEL:-llama3.2:3b}

echo "Ensuring model $MODEL is available..."
ollama pull "$MODEL"

# Bring Ollama to foreground
wait
