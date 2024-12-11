# chrono-arbitor-py
This program was written as part of Fall 2024 EE 451 course project. The objective of this exercise is to given an existing program, parallelize it to achieve a speedup and acceleration using the parallelization techniques taught in the course.

# System Requirement
- OS: Windows, Mac Lnux 
- RAM: >8GB
- Disk Space: 12GB + space to store language models of your choice
- CPU: 4+ cores, 8+ cores recommended
- GPU: Optional
- Reference: https://www.gpu-mart.com/blog/run-llms-with-ollama

# How to Run the Program
1. Install Ollama server, following the instruction provided at https://ollama.com/
   1. Alternatively run `curl https://ollama.ai/install.sh | sh`
2. Enable concurrent request handling:
    ```
    export OLLAMA_NUM_PARALLEL=10
    export OLLAMA_MAX_LOADED_MODELS=6
    ```
    - Reference: https://github.com/ollama/ollama/issues/358
3. Start Ollama server: `ollama server`
    To start the server on a specific address/port, set this environment variable before starting the server: `export OLLAMA_SERVER=http://[ip address]:[port number]`

