#!/usr/bin/env bash

# Script to run and compare serial, shared memory, and MPI tests
# Logs results to timestamped files for easy reference

# Define script name for dynamic usage display
script_name=$(basename "$0")

# Results directory
results_dir="results"
mkdir -p "$results_dir"

# Helper function to print section headers
print_section() {
    echo ""
    echo "#####################"
    echo "    $1"
    echo "#####################"
}

# Log results
log_file="$results_dir/result_$(date +"%Y%m%d_%H%M").txt"
echo "Results will be logged to: $log_file"

# Run tests
{
    print_section "Serial"
    echo "python main_serial.py"
    python main_serial.py
    echo ""

    print_section "Parallel - Shared Memory"
    echo "python main_shared_mem.py"
    python main_shared_mem.py
    echo ""

    print_section "Parallel - MPI"
    for n in 4 3 2 1; do
        echo "mpirun -n $n python main_mpi.py"
        mpirun -n "$n" python main_mpi.py
        echo ""
    done
} | tee "$log_file"
