import subprocess
from decimal import Decimal
import sys
import os
from redis.cluster import command
from .utils import get_oga_directory
# Configuration for each game
config = {
    "super88": {
        "command_parameters": {
            "n": {
                "param_name": "-n",
                "help": "run N times (otherwise will read lines from stdin)",
                "type": int,
                "default": 10000
            },
            "m": {
                "param_name": "-m",
                "help": "Add a value to set as the max win",
                "type": Decimal,
                "default": ""
            },
            "stake": {
                "param_name": "--stake",
                "help": "The amount to be staked per win line (or any way equivalent) in each gameplay.",
                "type": str,
                "default": "1.76"
            }
        },
        "module_name": "engines.games.super-88-fortunes.hitsqwad.super_88_fortunes_rtp_94"
    },

    "blazing":{
            "performance":{
                "command_parameters": {
                    "n": {
                        "param_name": "-n",
                        "help": "run N times (otherwise will read lines from stdin)",
                        "type": int,
                        "default": 10000
                    },
                    "m": {
                        "param_name": "-m",
                        "help": "Add a value to set as the max win",
                        "type": Decimal,
                        "default": ""
                    },
                    "stake": {
                        "param_name": "--stake",
                        "help": "The amount to be staked per win line (or any way equivalent) in each gameplay.",
                        "type": str,
                        "default": "1"
                    }
                },

                "module_name": "engines.games.blazing-7s-cashway.light_n_wonder.blazing_7s_cashway_rtp_94"
            },

            "test":{
                "command_parameters":{},
                "module_name":"engines.games.blazing-7s-cashway.light_n_wonder.blazing_7s_cashway_rtp_94"

            },

            "rtp":{
                "command_parameters": {
                    "n": {
                        "param_name": "-n",
                        "help": "no of spins want to perform",
                        "type": int,
                        "default": 1000000
                    },

                "filename": {
                        "param_name": "-- >",
                        "help": "Output file name, it should be .xlsx format",
                        "type": str,
                        "default": "rtp_report.xlsx"
                    },
                },
                "module_name": "engines.games.blazing-7s-cashway.light_n_wonder.blazing_7s_cashway_rtp_94"

            },


    }
}


def get_input_for_parameter(param_name, param_type, help_text, default_value):
    """Prompt the user for input and handle the conversion of input to the correct type."""
    user_input = input(f"{help_text} (default: {default_value}): ").strip()

    if user_input == "":  # If the user presses enter without typing anything, use the default value
        return default_value
    else:
        try:
            return param_type(user_input)  # Convert the input to the desired type
        except ValueError:
            print(f"Invalid input for {param_name}. Using default value: {default_value}")
            return default_value

 # nosetests --with-coverage --cover-erase --cover-package=./engines/games/blazing-7s-cashway  engines.games.blazing-7s-cashway.light_n_wonder.blazing-7s-cashways.tests.tests.py && coverage html --include='*/blazing-7s-cashways/*'

def construct_vt_runner_command(module_name, parameters,process_name):
    """Constructs and returns the vt-runner command based on user input and the game config."""

    process_command = {"performance": ['python', '-m', f'{module_name}.tests.performance_test'],
                        "test":['nosetests' ,f'{module_name}.tests.tests.py'],
                        "rtp": ['vt-runner', '-c', f'{module_name}.tests.volume_tester', '--progress-bar'],
                       }
    command = process_command[process_name]
    # For each parameter in the game configuration, get the user's input and add it to the command
    for param_name, param_config in parameters.items():
        param_value = get_input_for_parameter(
            param_name,
            param_config['type'],
            param_config['help'],
            param_config['default']
        )

        # If the parameter has a value, add it to the command
        if param_value:
            command.extend([param_config['param_name'], str(param_value)])
    if process_name == "performance":
        # Pipe the output to OGA.Engine.vt_reduce
        command.append('|')
        command.append('python -m OGA.Engine.vt_reduce')
        print(command)
    return command


def run_vt_runner(process_name,config):
    """Runs the vt-runner for the selected game based on user input."""
    # Retrieve the parameters and module name for the selected game from the config
    if config and  process_name in config:
        game_config = config[process_name]
        parameters = game_config["command_parameters"]
        module_name = game_config["module_name"]

        # Construct the vt-runner command
        command = ' '.join(construct_vt_runner_command(module_name, parameters,process_name))
        #command = "vt-runner -c  engines.games.blazing-7s-cashway.light_n_wonder.blazing_7s_cashway_rtp_94.tests.volume_tester --progress-bar -n 100000 -- > rtp_report2.xlsx"
        # Print and execute the command
        print(f"\nRunning command: {command}")
        try:
            # Use subprocess.Popen for real-time output streaming

            process = subprocess.Popen(command, cwd=get_oga_directory(), shell=True, stdout=sys.stdout, stderr=sys.stderr, text=True)

            # Wait for the command to finish
            process.wait()

            # Check if the command was successful (exit code 0)
            if process.returncode != 0:
                print(f"Error: Command '{command}' failed with exit code {process.returncode}", file=sys.stderr)
                sys.exit(process.returncode)

            process.wait()


            # Check if the command was successful (return code 0)
            if process.returncode != 0:
                print(f"Error: Command '{' '.join(command)}' failed with exit code {process.returncode}", file=sys.stderr)
                sys.exit(process.returncode)

        except subprocess.CalledProcessError as e:
            print(f"Error running vt-runner: {e}")
        except FileNotFoundError:
            print("vt-runner not found. Make sure it's installed and accessible.")
    else:
        print(f"Game's command_config file is not present. Please add config to  location",os.getcwd() ,"following command is not present",process_name)

