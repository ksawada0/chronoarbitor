#!/usr/bin/env bash

# Get the current date and time
TZ="America/Los_Angeles" date

# Default port for the Ollama server
DEFAULT_PORT=11434
OLLAMA_PORT=$DEFAULT_PORT

# Check if the default port is in use
if lsof -Pi :$OLLAMA_PORT -sTCP:LISTEN -t > /dev/null; then
    echo "Port $OLLAMA_PORT is already in use. Trying an alternative port..."
    OLLAMA_PORT=11435  # Fallback port
fi

# Start the Ollama server if not already running
if ! curl -sSf http://127.0.0.1:$OLLAMA_PORT/health > /dev/null; then
    echo "Starting Ollama server on port $OLLAMA_PORT..."
    OLLAMA_HOST=0.0.0.0:$OLLAMA_PORT ollama serve &
    sleep 5  # Allow server to initialize
else
    echo "Ollama server already running on port $OLLAMA_PORT."
fi

# Export the OLLAMA_HOST environment variable
export OLLAMA_HOST=http://127.0.0.1:$OLLAMA_PORT

# Run serial and parallel tests
echo "#####################"
echo "    Serial"
echo "#####################"
python3 main_serial.py
echo ""

echo "#####################"
echo "    Parallel"
echo "#####################"
for i in {1..16}; do
    echo "Number of cores: $i"
    mpirun -n $i python3 main_mpi.py
    echo ""
done
