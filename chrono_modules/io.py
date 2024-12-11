import os
import json

def read_input_file(path):
    with open(path) as f:
        return [x.strip() for x in f.read().split('\n')]
    
    
def write_result_to_file(dict_result, filename='data', ):
    out_dir = os.path.abspath(filename)
    os.makedirs(out_dir, exist_ok=True)  # Create the directory if it doesn't exist

    out_path = os.path.join(out_dir, 'result.txt')  # Create the full path
    with open(out_path, 'w+') as f:
        f.write(json.dumps(dict_result))
        
    