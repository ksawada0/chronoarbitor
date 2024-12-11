#!/usr/bin/env python

import time
import json
import requests
from classes.DecisionResult import DecisionResult
import resources.common as cmn


def query_ollama(model_name, prompt):
    """Queries the Ollama server."""
    response = requests.post(
        f"{cmn.BASE_URL_LOCAL}/api/generate",  
        json={"model": model_name, "prompt": prompt},
        stream=True
    )
    if response.status_code == 200:
        full_response = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8")
                json_response = json.loads(decoded_line)
                full_response += json_response.get("response", "")
        return full_response
    else:
        return None
    
    
def generate_prompt(original_prompt, layer, role=None, agree_count=-1, decision_count=-1):
    """Construct the prompt based on the layer, role, and agreement count."""
    base_prompt = (
        f"Is this statement true? '{original_prompt}' "
        "Please generate your response in the following format: First answer either TRUE or FALSE, followed by a period. Then, state the reason for my decision is [your reason]' "
        "Please limit your response to a maximum of 3000 bytes. Ensure your response fits within this limit."
    )

    if layer == 3 and agree_count is not None:
        return (
            base_prompt
            + f" Current number of agreements so far is {agree_count}. Consider this in your response."
        )
    elif role:
        return f"{base_prompt} Respond as an expert {role}."
    return base_prompt


def process_response(response):
    """Process LLM response."""
    decision = "TRUE" if "TRUE" in response else "FALSE"
    return DecisionResult(decision, response)

