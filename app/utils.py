import json
import os
import re

def load_settings():
    """Load settings from a configuration file (settings.json)"""
    settings_file = 'app/config.json'

    if not os.path.exists(settings_file):
        print(f"Settings file {settings_file} not found!")
        return None

    with open(settings_file, 'r') as f:
        settings = json.load(f)

    return settings

def load_game_commands():
    """Load settings from a configuration file (settings.json)"""
    cwd = os.getcwd()
    settings_file = cwd+'/command_config.json'

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
    else:
        final_ans = current_directory  # Fallback to the original directory

    return root + final_ans




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
            print("Version updated successfully.")
        else:
            print("No docstring found at the top of the file.")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")