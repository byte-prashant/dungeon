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

def find_and_replace_version(directory, old_version, new_version):
    """
    Recursively find files in the given directory, check for the old_version string in the top 10 lines,
    and replace it with the new_version.

    Args:
        directory (str): The root directory to search.
        old_version (str): The version string to find.
        new_version (str): The version string to replace with.
    """
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r') as f:
                    lines = f.readlines()

                # Only check the first 10 lines
                top_lines = lines[:10]
                content_to_check = ''.join(top_lines)

                if old_version in content_to_check:
                    updated_lines = [line.replace(old_version, new_version) for line in top_lines]
                    lines[:10] = updated_lines
                    with open(file_path, 'w') as f:
                        f.writelines(lines)
                    print(f"Updated version in: {file_path}")
            except (UnicodeDecodeError, PermissionError) as e:
                print(f"Skipped file {file_path}: {e}")
