#!/usr/bin/env bash

# Usage function to display help message
usage() {
    script_name=$(basename "$0")
    cat <<EOF
Usage: $script_name [OPTIONS]

Options:
  -p, --port PORT              Set the server port (default: 11431)
  -n, --num-parallel NUM       Set the number of parallel tasks (default: 10)
  -m, --max-models NUM         Set the maximum number of loaded models (default: 6)
  -t, --threads NUM            Set the number of threads for OMP (default: 4)
  -h, --help                   Display this help message

Description:
  This script starts the Ollama server with configurable settings, allowing 
  you to set the port, number of parallel tasks, max loaded models, and threads.

Examples:
  $script_name                       # Start with default settings
  $script_name -p 12345 -n 20 -m 8   # Custom settings
EOF
    exit 1
}

# Default values
OLLAMA_PORT=11431
OLLAMA_NUM_PARALLEL=10
OLLAMA_MAX_LOADED_MODELS=6
OMP_NUM_THREADS=4

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--port)
            OLLAMA_PORT="$2"
            shift 2
            ;;
        -n|--num-parallel)
            OLLAMA_NUM_PARALLEL="$2"
            shift 2
            ;;
        -m|--max-models)
            OLLAMA_MAX_LOADED_MODELS="$2"
            shift 2
            ;;
        -t|--threads)
            OMP_NUM_THREADS="$2"
            shift 2
            ;;
        -h|--help)
            usage
            ;;
        *)
            echo "Unknown option: $1"
            usage
            ;;
    esac
done

# Export environment variables
export OLLAMA_PORT
export OLLAMA_NUM_PARALLEL
export OLLAMA_MAX_LOADED_MODELS
export OLLAMA_HOST="http://127.0.0.1:$OLLAMA_PORT"

# Set threads via launchctl
launchctl setenv OMP_NUM_THREADS "$OMP_NUM_THREADS"

# Display configuration
cat <<EOF
Starting Ollama server with the following configuration:
  Port:                 $OLLAMA_PORT
  Number of Parallel:   $OLLAMA_NUM_PARALLEL
  Max Loaded Models:    $OLLAMA_MAX_LOADED_MODELS
  OMP Threads:          $OMP_NUM_THREADS
EOF

# Start the Ollama server
ollama serve
