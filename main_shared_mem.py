from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import os
import time
import chrono_modules.ollama_helper as ollama_helper
import resources.chrono_logging as chrono_logging
import resources.common as cmn

log = chrono_logging.get_logger("main", json=False)

# Constants
N_WORKERS = 1  # Number of threads
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE_TIME = True
IS_LOG_RESPONSE = False

input_file_path = os.path.abspath('data/prompts.txt')

# Shared data structures
results_lock = Lock()
global_results = {}  # {prompt_id: {"agree": int, "decision": int}}


def worker_task(task, local_results):
    """Thread worker to process a single task."""
    prompt_id, model, prompt, layer, role = task
    start_time = time.time()

    # Dynamically generate the prompt for Layer 3
    if layer == 3:
        prompt = ollama_helper.generate_prompt(prompt, layer=3, role=role)

    try:
        response = ollama_helper.query_ollama(model, prompt)
        end_time = time.time()

        if IS_MEASURE_QUERY_RESPONSE_TIME:
            print(f"Task: {model}-{role or 'Generalist'} | Layer: {layer} | Time: {end_time - start_time:.2f} seconds")

        if response:
            result = ollama_helper.process_response(response)
            agree = 1 if result.decision == "TRUE" else 0
            decision = 1
        else:
            agree = 0
            decision = 0

        # Update local results for this prompt_id
        if prompt_id not in local_results:
            local_results[prompt_id] = {"agree": 0, "decision": 0}
        local_results[prompt_id]["agree"] += agree
        local_results[prompt_id]["decision"] += decision

    except Exception as e:
        print(f"Error processing task {task}: {e}")


def main():
    # Prompts and models
    with open(input_file_path) as f:
        prompts = [x.strip() for x in f.read().split('\n') if x.strip()]

    models = cmn.MODELS
    roles = cmn.ROLES
    print(f'Number of Threads: {N_WORKERS}')
    print(f'Number of Models: {len(models)}')
    print(f'Number of Roles: {len(roles)}')

    # Create tasks
    tasks = []
    for prompt_id, prompt in enumerate(prompts):
        # Layer 2: Query each model as Generalist
        for model in models:
            tasks.append((prompt_id, model, ollama_helper.generate_prompt(prompt, layer=2), 2, DEFAULT_ROLE))

        # Layer 3: Query each model with role-specific prompts
        for model in models:
            for role in roles:
                tasks.append((prompt_id, model, prompt, 3, role))

    # Process tasks in parallel
    def worker_wrapper(local_tasks):
        local_results = {}  # Local storage for results
        for task in local_tasks:
            worker_task(task, local_results)
        return local_results

    with ThreadPoolExecutor(max_workers=N_WORKERS) as executor:
        local_results_list = list(executor.map(worker_wrapper, [tasks[i::N_WORKERS] for i in range(N_WORKERS)]))

    # Merge all local results into the global results
    for local_results in local_results_list:
        for prompt_id, counts in local_results.items():
            with results_lock:
                if prompt_id not in global_results:
                    global_results[prompt_id] = {"agree": 0, "decision": 0}
                global_results[prompt_id]["agree"] += counts["agree"]
                global_results[prompt_id]["decision"] += counts["decision"]

    # Log results per prompt
    for prompt_id, counters in global_results.items():
        agree = counters["agree"]
        decision = counters["decision"]
        score = agree / decision if decision > 0 else 0
        print(f"----------------------")
        print(f"Prompt ID: {prompt_id}")
        print(f"Total Agreements: {agree}")
        print(f"Total Decisions (# of queries made): {decision}")
        print(f"Agreement Percentage: {score * 100:.2f}%")
        print(f"----------------------")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f'Elapsed Time = {elapsed_time:.1f} min.')
