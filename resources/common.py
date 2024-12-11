#!/usr/bin/env python
################################################################################
# Description:
#       This script maintains the constant variables and a class, used to execute
#       MDMS testing tasks
# ################################################################################

import datetime
import os

##############################
# Default directory paths
##############################

##############################
# Ollama
##############################
# BASE_URL_LOCAL = 'http://127.0.0.1:11434'
# BASE_URL_LOCAL = 'http://0.0.0.0:11434'

# Dynamically fetch the Ollama server URL from the environment variable
BASE_URL_LOCAL = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")

##############################
# Miscellaneous
##############################
TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)
START_TIME = datetime.datetime.now()

##############################
# Test (Deprecated)
##############################
# TEST_SUBSYSTEM = 'dsp'


# MODELS = ["llama3", "phi", "gemma", "mistral", "qwq", "qway2"]
# MODELS = ["llama3", "phi", "gemma", "mistral"]
MODELS = ["llama3", "phi", "gemma"]
# ROLES = ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist"]
# ROLES = ["Engineer", "Philosophy Professor", "Mathematician", "Social Scientist", "Physicist", "Astronomer", "Molecular Biologist", "Medical Doctor", "Social Worker", "Occupational Therapist"]
ROLES = ["Engineer", "Philosophy Professor"]

##############################
# Tokens
##############################
# Tokenizer mappings for each model (TODO: adjust sa needed)
MODEL_TOKENIZER_MAP = {
    "llama3": "gpt2",
    "phi": "gpt2",
    "gemma": "gpt2",
    "qwen2": "gpt2",
    "mistral-nemo": "gpt2",
    "mistral": "gpt2"
}