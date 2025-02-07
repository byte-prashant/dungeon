import copy
import json
import os
import re
from app.config import structure
import ast
import astor
from pathlib import Path
def load_settings():
    """Load settings from a configuration file (settings.json)"""
    import copy
    setting = copy.deepcopy(structure)
    return setting

def load_game_commands():
    """Load settings from a configuration file (settings.json)"""
    cwd = os.getcwd()
    settings_file = cwd+'/game_command.json'

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

def find_and_replace_version(directory, new_version):
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

            if not  file_path.endswith(".py"):
                continue
            update_version(file_path,new_version)


def get_oga_directory():
    import os
    root = os.path.abspath(os.sep)
    # Get the current working directory
    current_directory = os.getcwd()

    # Find the part of the path up to "OGA" (case-insensitive)
    final_ans = ""
    if "OGA" in current_directory.upper():
        for path_name in current_directory.split(os.sep):
            final_ans = os.path.join(final_ans, path_name)  # Reconstruct the path
            if "OGA" in path_name.upper():
                break
    if not  final_ans:
        raise Exception("Unable to OGA root directory")

    return root+final_ans




def update_version(file_path,new_version):
    try:
        # Read all lines of the file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        triple_quote = '"""'
        start, end = None, None

        for index, line in enumerate(lines):
            if triple_quote in line:
                if start is None:
                    start = index
                elif end is None:
                    end = index
                    break

        # Update the version inside the triple quotes
        if start is not None and end is not None and start != end:
            docstring_lines = lines[start + 1:end]
            updated_lines = []

            version_pattern = r"(version\s*:\s*)(\d+\.\d+\.\d+)"
            new_version = "Version: "+new_version
            for line in docstring_lines:
                if re.search(version_pattern, line, re.IGNORECASE):
                    updated_line = re.sub(version_pattern, new_version, line, flags=re.IGNORECASE)
                    updated_lines.append(updated_line)
                else:
                    updated_lines.append(line)

            lines[start + 1:end] = updated_lines

            # Write the updated content back to the file
            with open(file_path, 'w') as file:
                file.writelines(lines)
            print("Version updated successfully for.", file_path)
        else:
            print("No docstring found at the top of the file.", file_path)

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


def find_file(root_directory, target_filename):
    """
    Recursively searches for a file in all subdirectories.

    :param root_directory: The root directory to start the search from.
    :param target_filename: The name of the file to search for.
    :return: List of full paths to the found files.
    """
    found_files = []
    for dirpath, dirnames, filenames in os.walk(root_directory):
        if target_filename in filenames:
            found_files.append(os.path.join(dirpath, target_filename))
    return found_files

def get_games_config():
    target = "games.json"
    found_files = find_file(os.getcwd(),target)
    if found_files:
        with open(found_files[0], 'r') as f:
            settings = json.load(f)
    return settings

def get_engine_class():
    try:
        config = get_games_config()
        engine_class_path = config['game'][0]['engine_class']
        path_parts = engine_class_path.split(".")
        engine_class = path_parts.pop(-1)
        return ".".join(path_parts), engine_class
    except Exception as e:
        print("Found error while readind game config",e)

def replace_function(file_path, function_name, new_function_code):
    """
    Replaces a function in a Python file with a new function.

    Args:
        file_path (str): Path to the Python file.
        function_name (str): Name of the function to replace.
        new_function_code (str): Code for the new function as a string.
    """
    try:
        # Read the existing Python file
        with open(file_path, "r") as file:
            file_content = file.read()

        # Parse the existing file content
        tree = ast.parse(file_content)

        # Parse the new function code
        new_function_tree = ast.parse(new_function_code).body[0]

        if not isinstance(new_function_tree, ast.FunctionDef):
            raise ValueError("The provided new function code is not a valid function definition.")

        # Find and replace the target function
        for index, node in enumerate(tree.body):
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                tree.body[index] = new_function_tree
                break
        else:
            raise ValueError(f"Function '{function_name}' not found in the file.")

        # Convert the modified AST back to source code
        modified_code = astor.to_source(tree)

        # Write the updated code back to the file
        with open(file_path, "w") as file:
            file.write(modified_code)

        print(f"Function '{function_name}' has been successfully replaced.")

    except Exception as e:
        print(f"Error: {e}")


def replace_sh_function(file_path, target_function_name, new_function_definition):
    try:
        # Read the original file
        with open(file_path, "r") as f:
            lines = f.readlines()

        # Regex pattern to find the function declaration
        pattern = re.compile(rf'^\s*(function\s+)?{re.escape(target_function_name)}\s*\(\s*\)\s*{{?')

        in_target_function = False
        brace_count = 0
        start_line = -1
        end_line = -1

        # Find the start and end of the target function
        for i, line in enumerate(lines):
            if not in_target_function:
                if pattern.match(line.strip()):
                    in_target_function = True
                    start_line = i
                    brace_count += line.count('{') - line.count('}')
            else:
                brace_count += line.count('{') - line.count('}')
                if brace_count <= 0:
                    end_line = i
                    break

        if start_line == -1 or end_line == -1:
            raise ValueError(f"Function '{target_function_name}' not found!")

        # Replace the old function with the new definition
        new_lines = lines[:start_line] + [new_function_definition + "\n"] + lines[end_line + 1:]

        # Write the modified content back to the file
        with open(file_path, "w") as f:
            f.writelines(new_lines)

        print(f"Function '{target_function_name}' has been successfully replaced.")

    except Exception as e:
        print(f"Error: {e}")


def create_and_update_yagmi_config(folder_path, data_dict):
    # Create the hidden folder (e.g., .hidden_folder) if it doesn't exist
    hidden_folder_path = Path(folder_path)
    if not hidden_folder_path.exists():
        hidden_folder_path.mkdir(exist_ok=True)
        print("Db folder created")

    # Define the file to store the boolean values
    file_path = hidden_folder_path/"config.json"

    # Load existing data if the file exists
    if file_path.exists():
        with open(file_path, 'r') as file:
            data = json.load(file)
    else:
        data = {}

    # Update the boolean value
    data.update(**data_dict)

    # Write back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

    print(f"config Stored in {file_path}")



def get_yagmi_config(folder_path):
    file_path = Path(folder_path)
    if file_path.exists():
        with open(file_path, 'r') as file:
            return json.load(file)
    return {}


def create_yagmi_db(oga_path):
    from app.utils import  create_and_update_yagmi_config
    from app.config import yagmi_config, yagmi_db_config
    file_path = yagmi_db_config['folder_name']

    if oga_path[-1] =="/":
        oga_path = oga_path[:-1]
    oga_path += "/"+file_path
    create_and_update_yagmi_config(oga_path , yagmi_config)
    print("Yagmi db has been created succesfully")


def setup_yagmi():
    oga_path = get_oga_directory()
    create_yagmi_db(oga_path)