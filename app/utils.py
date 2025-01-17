import json
import os
def load_settings():
    """Load settings from a configuration file (settings.json)"""
    settings_file = 'app/config.json'

    if not os.path.exists(settings_file):
        print(f"Settings file {settings_file} not found!")
        return None

    with open(settings_file, 'r') as f:
        settings = json.load(f)

    return settings


def print_folder_structure(folder_structure, indent=0):
    """
    Recursively prints the folder structure from a nested dictionary.

    Args:
        folder_structure (dict): The folder structure in dictionary format.
        indent (int): The current indentation level (used for recursion).
    """
    for key, value in folder_structure.items():
        # Print the folder or file name
        print(" " * indent + f"|- {key}")

        if isinstance(value, dict):  # If it's a dictionary, it's a folder
            print_folder_structure(value, indent + 2)  # Recurse with increased indentation
        elif isinstance(value, list):  # If it's a list, it contains files
            for item in value:
                print(" " * (indent + 2) + f"|- {item}")
