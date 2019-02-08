import json
import os

config_folder = os.path.dirname(os.path.realpath(__file__))

def load_file(file_name):
    with open(os.path.join(config_folder, file_name)) as file:
        return file.read()

def load_json_file(json_name):
    with open(os.path.join(config_folder, json_name)) as file:
        json_str = file.read()
        json_dict = json.loads(json_str)
    return json_dict
