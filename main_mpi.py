#!/usr/bin/env python3

import requests
import time
import os
from mpi4py import MPI
import chrono_modules.ollama_helper as ollama_helper
import resources.chrono_logging as chrono_logging
import resources.common as cmn

log = chrono_logging.get_logger("main", json=False)

# Constants
MAX_PROMPT_LENGTH = 3000
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE = False

input_file_path = os.path.abspath('data/prompts.txt')

def process_task(task, agree_count, decision_count):
    """Process a single task and update counters locally."""
    model, prompt, layer, role = task

    # Dynamically generate the prompt for Layer 3
    if layer == 3:
        prompt = ollama_helper.generate_prompt(
            prompt, layer=3, role=role, agree_count=agree_count, decision_count=decision_count)

    response = ollama_helper.query_ollama(model, prompt)

    if response:
        result = ollama_helper.process_response(response)
        decision_count += 1
        if result.decision == "TRUE":
            agree_count += 1

    return agree_count, decision_count


def distribute_tasks(prompts, models, roles):
    """Distribute tasks for Layer 2 and Layer 3 among all workers."""
    tasks = []
    for prompt in prompts:
        
        # Layer 2 tasks: Query each model as "Generalist"
        for model in models:
            tasks.append((model, ollama_helper.generate_prompt(prompt, layer=2), 2, DEFAULT_ROLE))

        # Layer 3 tasks: Query each model with role-specific prompts
        for model in models:
            for role in roles:
                tasks.append((model, prompt, 3, role))

    return tasks


def main():
    # MPI Initialization
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Load prompts and define models and roles
    if rank == 0:
        # Read input prompts from a file
        with open(input_file_path) as f:
            prompts = [x.strip() for x in f.read().split('\n') if x.strip()]
        
        # Define models and roles 
        models = cmn.MODELS
        roles = cmn.ROLES

        # Generate all tasks to be executed
        tasks = distribute_tasks(prompts, models, roles)

        # Divide up tasks into subtasks for each process
        subtask_size = len(tasks) // size
        subtasks = [tasks[i * subtask_size:(i + 1) * subtask_size] for i in range(size)]

        # Handle any remaining tasks (in case number of tasks is not divisible by number of processes)
        for i in range(len(tasks) % size):
            subtasks[i].append(tasks[subtask_size * size + i])
    else:
        subtasks = None

    # Scatter tasks among processes
    tasks = comm.scatter(subtasks, root=0)

    # Local counters
    local_agree_counter = 0
    local_decision_count = 0

    # Process assigned tasks
    for task in tasks:
        local_agree_counter, local_decision_count = process_task(
            task, local_agree_counter, local_decision_count)

    # Gather results at the root process
    global_agree_counter = comm.reduce(local_agree_counter, op=MPI.SUM, root=0)
    global_decision_count = comm.reduce(local_decision_count, op=MPI.SUM, root=0)

    # Root process computes and prints results
    if rank == 0:
        score = global_agree_counter / global_decision_count if global_decision_count > 0 else 0
        print("----------------------")
        print(f"Total Agreements: {global_agree_counter}")
        print(f"Total Decisions (# of queries made): {global_decision_count}")
        print(f"Agreement Percentage: {score * 100:.2f}%")
        print("----------------------")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f'Elapsed Time = {elapsed_time:.1f} min.')
