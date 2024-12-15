#!/usr/bin/env bash

# Usage function to display help message
usage() {
    script_name=$(basename "$0")
    cat <<EOF
Usage: $script_name [NUM_MODELS] [NUM_ROLES]

Arguments:
  NUM_MODELS   Number of models to use (default: 3)
  NUM_ROLES    Number of roles to use (default: 4)

Description:
  This script executes an MPI-based Python script multiple times with varying 
  numbers of MPI processes and stores the results in timestamped log files.

Examples:
  $0            # Uses default values: 2 models and 2 roles
  $0 3 4        # Runs with 3 models and 4 roles
EOF
    exit 1
}

# Check for invalid arguments
if [[ "$#" -gt 2 ]]; then
    echo "Error: Too many arguments."
    usage
fi

# Default values
num_models=3
num_roles=4

# Update values if arguments are provided
if [[ "$#" -ge 1 ]]; then
    num_models="$1"
fi
if [[ "$#" -eq 2 ]]; then
    num_roles="$2"
fi

# Verify results directory exists
results_dir="results/num_cores"
mkdir -p "$results_dir"

# Main loop to run the script with varying number of processes
for i in {1..16}; do
    echo "Running with $i MPI processes, $num_models models, and $num_roles roles..."
    mpiexec -n "$i" python main_mpi.py "-m $num_models" "-r $num_roles" | tee "$results_dir/result_num_cores_$(date +"%Y%m%d_%H%M").txt"
done
