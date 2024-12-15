#!/usr/bin/env bash

# Set environment variables
export OLLAMA_PORT=11431
export OLLAMA_NUM_PARALLEL=10
export OLLAMA_MAX_LOADED_MODELS=6
export OLLAMA_HOST=http://127.0.0.1:$OLLAMA_PORT

# Specify the number of cores
launchctl setenv OMP_NUM_THREADS 4

# Start the Ollama server
ollama serve
