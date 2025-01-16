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
                f.write(f"alias astro='python -m my_tool.cli'\n")
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


if __name__ == "__main__":
    add_alias_to_shell()
