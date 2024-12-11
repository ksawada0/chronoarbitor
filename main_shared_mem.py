from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import requests
import json
import time
import os
import chrono_modules.ollama_helper as ollama_helper
from classes.DecisionResult import DecisionResult
import resources.common as cmn



# Constants
N_WORKERS = 4  # Number of threads
MAX_PROMPT_LENGTH = 3000
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE = False

# Thread-safe counters
agree_counter_lock = Lock()
decision_count_lock = Lock()
global_agree_counter = 0
global_decision_count = 0

input_file_path = os.path.abspath('data/prompts.txt')


def worker_task(task):
    """Thread worker to process a single task."""
    global global_agree_counter, global_decision_count

    model, prompt, layer, role = task
    start_time = time.time()
    
    # Dynamically generate the prompt for Layer 3
    if layer == 3:
        prompt = ollama_helper.generate_prompt(prompt, layer=3, role=role, agree_count=global_agree_counter)

    response = ollama_helper.query_ollama(model, prompt)
    if response:
        result = ollama_helper.process_response(response)
        end_time = time.time()
        if IS_MEASURE_QUERY_RESPONSE:
            print(f"Task: {model}-{role or 'Generalist'} | Layer: {layer} | Time: {end_time - start_time:.2f} seconds")

        with decision_count_lock:
            global_decision_count += 1
        if result.decision == "TRUE":
            with agree_counter_lock:
                global_agree_counter += 1


def main():
    global global_agree_counter, global_decision_count

    # Prompts and models
    with open (input_file_path) as f:
        prompts = [x.strip() for x in f.read().split('\n')]

    # Define models and roles
    models = cmn.MODELS
    roles = cmn.ROLES

    # Create tasks
    tasks = []

    for prompt in prompts:
        print(f'----------------------\nQuestion: {prompt}')
        # Layer 2: Query each model as Generalist
        for model in models:
                tasks.append((model, ollama_helper.generate_prompt(prompt, layer=2), 2, DEFAULT_ROLE))

        # Layer 3: Query each model with role-specific prompts
        for model in models:
            for role in roles:
                tasks.append((
                    model,
                    prompt,  # Pass the raw prompt here
                    3,       # Layer
                    role      # Specific role
                ))

        # Use ThreadPoolExecutor for parallelism
        with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
            executor.map(worker_task, tasks)

        # Log final results
        score = global_agree_counter / global_decision_count if global_decision_count > 0 else 0
        print(f"Total Agreements: {global_agree_counter}")
        print(f"Total Decisions: {global_decision_count}")
        print(f"Agreement Percentage: {score * 100:.2f}%")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time)/60
    print(f'Elapsed Time = {elapsed_time :.1f} min.' )
