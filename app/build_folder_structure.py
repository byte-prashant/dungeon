import argparse
import os
from app.file_content.setup import create_setup_file

from app.utils import load_settings,print_folder_structure

import argparse
import os
import json


def create_python_package(dir_path):
    """Create a directory and add an __init__.py file to make it a Python package."""
    os.makedirs(dir_path, exist_ok=True)
    init_file = os.path.join(dir_path, '__init__.py')
    if not os.path.exists(init_file):
        with open(init_file, 'w') as f:
            f.write("# This is an empty __init__.py file to mark the directory as a Python package.")
    print(f"Created Python package: {dir_path}")


def create_structure(base_path, structure, game_name, client_name):
    if not structure:
        return
    for key, value in structure.items():
        if isinstance(value, list):
            # It's a folder with files
            dir_path = os.path.join(base_path, key)
            create_python_package(dir_path)

            # Create files listed in the array
            for file in value:
                file_path = os.path.join(dir_path, file)
                with open(file_path, 'w') as f:
                    if file.endswith('.json'):
                        f.write('{}')  # Example: empty JSON file
                    elif file.endswith('.py'):
                        f.write('"""\n  version:0.1.0 \n"""\n')  # Python file placeholder

                    elif file.endswith('.md'):
                        f.write('"""\n  version:0.1.0 \n"""\n') # Markdown file placeholder
                print(f"Created file: {file_path}")
        elif isinstance(value, dict):
            # It's a folder with subfolders (recursive)
            dir_path = os.path.join(base_path, key)
            create_python_package(dir_path)
            create_structure(dir_path, value, game_name, client_name)
        else:
            # It's a file in the current directory
            file_path = os.path.join(base_path, key)
            with open(file_path, 'w') as f:
                if key.endswith('.md'):
                    f.write('"""\n  version:0.1.0 \n"""\n')  # Placeholder for markdown files
                elif key.endswith('.py'):
                    f.write('"""\n  version:0.1.0\n"""\n')  # Placeholder for Python files
                    if "setup.py" ==  key:
                        setup_content = create_setup_file(game_name)

                        f.write(setup_content)
                        print(f"Created setup.py at: {file_path}")

            print(f"Created file: {file_path}")


def create_structure_from_json(client_name, game_name):
    """Recursively create directories and files from the given JSON structure."""
    setting = load_settings()
    base_path = setting['base_folder']
    base_path = os.path.join(base_path)
    structure = setting['folder_structure']
    new_structure = update_structure(structure, client_name, game_name)
    create_structure(base_path, new_structure, game_name ,client_name)


def update_structure(structure, client_name, game_name):
    """
    we can also replce the  key name and values while passing to the function
    :param structure:
    :param client_name:
    :param game_name:
    :return:
    """
    new_dict = {}
    import copy
    new_dict[game_name] = copy.deepcopy(structure["game_name"])
    # del new_dict["game_name"]
    new_dict[game_name][client_name] = copy.deepcopy(structure["game_name"]["client_name"])
    del new_dict[game_name]["client_name"]
    new_dict[game_name][client_name][game_name] = copy.deepcopy(structure["game_name"]["client_name"]["game_name"])
    del new_dict[game_name][client_name]["game_name"]
    print_folder_structure(new_dict)
    return new_dict
