from mpi4py import MPI
import time
import os
import chrono_modules.ollama_helper as ollama_helper
import resources.chrono_logging as chrono_logging
import resources.common as cmn

log = chrono_logging.get_logger("main", json=False)

# Constants
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE_TIME = True
input_file_path = os.path.abspath('data/prompts.txt')


def process_task(task):
    """Process a single task and return results with prompt_id."""
    prompt_id, model, prompt, layer, role = task
    start_time = time.time()

    # Dynamically generate the prompt for Layer 3
    if layer == 3:
        prompt = ollama_helper.generate_prompt(prompt, layer=3, role=role)

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

    return prompt_id, agree, decision


def distribute_tasks(prompts, models, roles):
    """Generate tasks with prompt_id for distribution."""
    tasks = []
    for prompt_id, prompt in enumerate(prompts):
        # Layer 2 tasks: Query each model as "Generalist"
        for model in models:
            tasks.append((prompt_id, model, ollama_helper.generate_prompt(prompt, layer=2), 2, DEFAULT_ROLE))

        # Layer 3 tasks: Query each model with role-specific prompts
        for model in models:
            for role in roles:
                tasks.append((prompt_id, model, prompt, 3, role))

    return tasks


def main():
    # MPI Initialization
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Load prompts and define models and roles
    if rank == 0:
        with open(input_file_path) as f:
            prompts = [x.strip() for x in f.read().split('\n') if x.strip()]
        models = cmn.MODELS
        roles = cmn.ROLES
        tasks = distribute_tasks(prompts, models, roles)

        # Divide tasks into chunks for processes
        chunk_size = len(tasks) // size
        chunks = [tasks[i * chunk_size:(i + 1) * chunk_size] for i in range(size)]

        # Handle any remaining tasks
        for i in range(len(tasks) % size):
            chunks[i].append(tasks[chunk_size * size + i])
    else:
        prompts = None
        tasks = None
        models = None
        roles = None
        chunks = None

    # Broadcast models and roles
    models = comm.bcast(models, root=0)
    roles = comm.bcast(roles, root=0)

    # Scatter tasks among processes
    local_tasks = comm.scatter(chunks, root=0)

    # Process local tasks
    local_results = []
    for task in local_tasks:
        local_results.append(process_task(task))

    # Gather results at root
    all_results = comm.gather(local_results, root=0)

    # Root process aggregates results
    if rank == 0:
        # Aggregate by prompt_id
        aggregated_results = {}
        for process_results in all_results:
            for prompt_id, agree, decision in process_results:
                if prompt_id not in aggregated_results:
                    aggregated_results[prompt_id] = {"agree": 0, "decision": 0}
                aggregated_results[prompt_id]["agree"] += agree
                aggregated_results[prompt_id]["decision"] += decision

        # Log results per prompt
        for prompt_id, counts in aggregated_results.items():
            agree = counts["agree"]
            decision = counts["decision"]
            score = agree / decision if decision > 0 else 0
            print("----------------------")
            print(f"Prompt ID: {prompt_id}")
            print(f"Total Agreements: {agree}")
            print(f"Total Decisions: {decision}")
            print(f"Agreement Percentage: {score * 100:.2f}%")
            print("----------------------")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f'Elapsed Time = {elapsed_time:.1f} min.')
