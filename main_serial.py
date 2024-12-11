#!/usr/bin/env python3

import requests
import json
import time
import os
import chrono_modules.ollama_helper as ollama_helper
import resources.chrono_logging as chrono_logging
import resources.common as cmn
from classes.DecisionResult import DecisionResult


log = chrono_logging.get_logger("main", json=False)

# Constants
MAX_PROMPT_LENGTH = 3000
DEFAULT_ROLE = "Generalist"
IS_MEASURE_QUERY_RESPONSE = False

# Global counters
global_agree_counter = 0
global_decision_count = 0

input_file_path = os.path.abspath('data/prompts.txt')


def process_task(task):
    """Process a single task and measure performance."""
    global global_agree_counter, global_decision_count

    model, prompt, layer, role = task
    start_time = time.time()

    # Dynamically generate the prompt for Layer 3
    if layer == 3:
        prompt = ollama_helper.generate_prompt(prompt, layer=3, role=role, agree_count=global_agree_counter, decision_count=global_decision_count)

    response = ollama_helper.query_ollama(model, prompt)
    end_time = time.time()
    if IS_MEASURE_QUERY_RESPONSE:
        print(f"Task: {model}-{role or 'Generalist'} | Layer: {layer} | Time: {end_time - start_time:.2f} seconds")

    if response:
        result = ollama_helper.process_response(response)
        global_decision_count += 1
        if result.decision == "TRUE":
            global_agree_counter += 1


def main():
    global global_agree_counter, global_decision_count

    # Prompts and models
    with open(input_file_path) as f:
        prompts = [x.strip() for x in f.read().split('\n')]

    # Define models and roles
    models = cmn.MODELS
    roles = cmn.ROLES

    # Process each prompt
    for prompt in prompts:
        print(f'----------------------\nQuestion: {prompt}')

        # Layer 2: Query each model as Generalist
        for model in models:
            process_task((model, ollama_helper.generate_prompt(prompt, layer=2), 2, DEFAULT_ROLE))

        # Layer 3: Query each model with role-specific prompts
        for model in models:
            for role in roles:
                process_task((model, prompt, 3, role))

        # Log final results
        score = global_agree_counter / global_decision_count if global_decision_count > 0 else 0
        print(f"Total Agreements: {global_agree_counter}")
        print(f"Total Decisions (# of queries made): {global_decision_count}")
        print(f"Agreement Percentage: {score * 100:.2f}%")


if __name__ == "__main__":
    start_time = time.time()
    main()
    end_time = time.time()
    elapsed_time = (end_time - start_time) / 60
    print(f'Elapsed Time = {elapsed_time:.1f} min.')
