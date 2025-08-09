import os
import sys
import subprocess

def add_alias_to_shell():
    home_dir = os.path.expanduser("~")
    shell_config_files = ['.bashrc', '.zshrc']

    for config_file in shell_config_files:
        config_file_path = os.path.join(home_dir, config_file)

        if os.path.exists(config_file_path):
            # Add the alias to the config file
            with open(config_file_path, 'a') as f:
                f.write("\n# Added by my_tool package\n")
                f.write(f"alias yagmi='python -m app.cli'\n")
            print(f"Alias added to {config_file_path}")

            # Reload the shell configuration
            reload_shell_config(config_file)
            break
    else:
        print("No suitable shell configuration file found. Please add the alias manually.")


def reload_shell_config(config_file):
    shell = os.environ.get('SHELL', '').lower()

    # For Bash or Zsh
    if 'bash' in shell or 'zsh' in shell:
        try:
            print(f"Reloading {config_file}...")
            subprocess.call(['source', os.path.join(os.path.expanduser("~"), config_file)], shell=True)
        except Exception as e:
            print(f"Error reloading shell: {e}")
    else:
        print(f"Shell {shell} not supported for auto-reload. Please reload manually.")


def install_pre_push_hook():
    repo_root = os.path.dirname(os.path.abspath(__file__))
    hooks_dir = os.path.join(repo_root, '.git', 'hooks')

    if not os.path.isdir(hooks_dir):
        print("Git hooks directory not found. Skipping pre-push hook installation.")
        return

    hook_path = os.path.join(hooks_dir, 'pre-push')
    with open(hook_path, 'w') as f:
        f.write('#!/bin/sh\n')
        f.write('yagmi dev --git_push\n')
    os.chmod(hook_path, 0o755)
    print(f"pre-push hook installed at {hook_path}")



if __name__ == "__main__":
    try:
        add_alias_to_shell()
        install_pre_push_hook()

    except Exception as e:
        print("Error occured", e)
