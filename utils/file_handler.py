'''
    This file handles saving to and loading data from json files
    (specifically, in the data directory of the project)... basically,
    "file and directory management". The functions here make some json file 
    management functions and operations modular.
'''
import json
import os

# Function to load json files when needed 
# (eg. users.json file to the user.py during the registering and/or signup of individuals)
def load_json(filepath):
    # Initially, check if the json file to load data from exists. If not, create the file
    # and return an empty dictionary to it. This helps avoid errors in user registration and assignemnt creation
    # in the case the files cannot be found.
    if not os.path.exists(filepath):
        return {}
    # open the file, load (Json) data (as py dict), return it and then close it
    with open(filepath, 'r') as f:
        return json.load(f)

# Function to save data to a json file
def save_json(filepath, data):
    # open file and write to it using the given data
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4) # indent=4 simply adds structure to the output file been written to
