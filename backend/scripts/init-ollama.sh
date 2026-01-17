#!/bin/sh
set -e

OLLAMA_URL="http://ollama:11434"

echo "Waiting for Ollama API..."
until curl -sf "$OLLAMA_URL/api/tags" >/dev/null; do
  echo "Ollama not ready yet, sleeping 5s..."
  sleep 5
done

echo "Ollama is ready. Checking models..."

ensure_model() {
  MODEL="$1"
  if ollama list | grep -q "^$MODEL"; then
    echo "Model $MODEL already present, skipping."
  else
    echo "Pulling model $MODEL..."
    ollama pull "$MODEL"
  fi
}

ensure_model "nomic-embed-text"
ensure_model "llama3.2:3b"

echo "Ollama model initialization complete."
