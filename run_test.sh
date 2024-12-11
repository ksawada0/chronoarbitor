#!/usr/bin/env bash
# 
# Run this script with 
#       ./run_test_2.sh | tee result_$(date +"%Y%m%d_%H%M").txt 
# 

echo "#####################"
echo "    Serial"
echo "#####################"
echo "python main_serial.py"
python main_serial.py 
echo ""

echo "#####################"
echo "    Parallel - Shared Memory"
echo "#####################"
echo "python main_shared_mem.py"
python main_shared_mem.py
echo ""

echo "#####################"
echo "    Parallel - MPI"
echo "#####################"
echo "mpirun -n 4 python3 main_mpi.py"
mpirun -n 4 python main_mpi.py
echo ""

echo "mpirun -n 3 python3 main_mpi.py"
mpirun -n 3 python main_mpi.py
echo ""

echo "mpirun -n 2 python3 main_mpi.py"
mpirun -n 2 python main_mpi.py
echo ""

echo "mpirun -n 1 python3 main_mpi.py"
mpirun -n 1 python main_mpi.py
echo ""
