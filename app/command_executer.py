import subprocess
from decimal import Decimal
import sys
import os
import shlex
import tempfile
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


def upload_engine(host, config):
    """Upload the current working folder to the remote engine path using scp."""
    if not config:
        print("Game command config is not available. Unable to upload engine.", file=sys.stderr)
        sys.exit(1)

    remote_config = config.get("remote", {})
    remote_engine_path = remote_config.get("engine_path")

    if not remote_engine_path:
        print("Missing 'remote.engine_path' in game_command.json.", file=sys.stderr)
        sys.exit(1)

    current_directory = os.getcwd()
    folder_name = os.path.basename(current_directory.rstrip(os.sep))
    parent_directory = os.path.dirname(current_directory.rstrip(os.sep))

    if not folder_name:
        print("Unable to determine the current folder name for upload.", file=sys.stderr)
        sys.exit(1)

    command = ["scp", "-r", folder_name, f"{host}:{remote_engine_path}"]
    print(f"Running command: {' '.join(command)}")

    try:
        subprocess.run(command, cwd=parent_directory or None, check=True)
    except subprocess.CalledProcessError as error:
        print(f"Engine upload failed with exit code {error.returncode}.", file=sys.stderr)
        sys.exit(error.returncode)
    except FileNotFoundError:
        print("scp not found. Make sure it is installed and accessible.", file=sys.stderr)
        sys.exit(1)


def _get_current_folder_name():
    current_directory = os.getcwd().rstrip(os.sep)
    folder_name = os.path.basename(current_directory)
    if not folder_name:
        raise ValueError("Unable to determine the current folder name.")
    return folder_name


def _get_remote_config(config):
    if not config:
        raise ValueError("Game command config is not available.")

    remote_config = config.get("remote")
    if not isinstance(remote_config, dict):
        raise ValueError("Missing 'remote' section in game_command.json.")

    return remote_config


def _get_game_process_config(config, game_name, process_name):
    game_config = config.get(game_name)
    if isinstance(game_config, dict) and process_name in game_config:
        process_config = game_config.get(process_name)
        if isinstance(process_config, dict):
            return process_config

    process_config = config.get(process_name)
    if isinstance(process_config, dict):
        return process_config

    raise ValueError(
        f"Unable to find '{process_name}' config for game '{game_name}' in game_command.json."
    )


def _build_command_with_defaults(module_name, parameters, process_name):
    process_command = {
        "performance": ["python", "-m", f"{module_name}.tests.performance_test"],
        "test": ["nosetests", f"{module_name}.tests.tests.py"],
        "rtp": ["vt-runner", "-c", f"{module_name}.tests.volume_tester", "--progress-bar"],
    }

    if process_name not in process_command:
        raise ValueError(f"Unsupported process type: {process_name}")

    command = list(process_command[process_name])
    redirect_target = None

    for param_config in parameters.values():
        param_name = str(param_config.get("param_name", "")).strip()
        param_value = param_config.get("default")

        if param_value in ("", None):
            continue

        if param_name in {"-- >", ">"}:
            redirect_target = str(param_value)
            continue

        command.extend([param_name, str(param_value)])

    if process_name == "performance":
        command.extend(["|", "python -m OGA.Engine.vt_reduce"])

    command_string = " ".join(shlex.quote(part) for part in command)
    if redirect_target:
        command_string = f"{command_string} > {shlex.quote(redirect_target)}"

    return command_string


def _build_remote_rtp_command(config, game_name):
    rtp_config = _get_game_process_config(config, game_name, "rtp")

    explicit_command = rtp_config.get("command") or rtp_config.get("remote_command")
    if explicit_command:
        return str(explicit_command).format(game_name=game_name)

    module_name = rtp_config.get("module_name")
    if not module_name:
        raise ValueError(
            f"Missing 'module_name' or explicit 'command' in rtp config for game '{game_name}'."
        )

    parameters = rtp_config.get("command_parameters", {})
    if not isinstance(parameters, dict):
        raise ValueError(f"Invalid command parameters for game '{game_name}'.")

    return _build_command_with_defaults(module_name, parameters, "rtp")


def _run_checked(command, **kwargs):
    return subprocess.run(command, check=True, **kwargs)

def _tmux_session_name(remote_config, game_name):
    prefix = remote_config.get("tmux_session_prefix", "rtp")
    return f"{prefix}_{game_name}".replace(".", "_")


def _remote_command_file_path(remote_config, game_name):
    command_file_path = remote_config.get("command_file_path")
    if not command_file_path:
        command_dir = remote_config.get("command_dir")
        if not command_dir:
            command_dir = os.path.join(
                _remote_rgs_path(remote_config),
                _remote_oga_dir(remote_config),
                _remote_bash_dir(remote_config),
            )
        command_file_path = os.path.join(command_dir, f"{game_name}_rtp.sh")

    return str(command_file_path).format(game_name=game_name)


def _remote_rgs_path(remote_config):
    return remote_config.get("rgs_path", "rgs")


def _remote_activate_path(remote_config):
    return remote_config.get("venv_activate", "venv/bin/activate")


def _remote_oga_dir(remote_config):
    return remote_config.get("oga_dir", "OGA-4.8.1")


def _remote_bash_dir(remote_config):
    return remote_config.get("bash_dir", "bash")


def _remote_install_path(remote_config, game_name):
    install_base = remote_config.get("install_base_path", "engine/games")
    return f"{install_base}/{game_name}"


def _write_remote_rtp_script(rgs_path, activate_path, oga_dir, rtp_command):
    script_body = "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            f"cd {shlex.quote(rgs_path)}",
            f"source {shlex.quote(activate_path)}",
            f"cd {shlex.quote(oga_dir)}",
            rtp_command,
            "",
        ]
    )

    temp_file = tempfile.NamedTemporaryFile("w", delete=False, suffix="_run_rtp.sh")
    try:
        temp_file.write(script_body)
        temp_file.flush()
        return temp_file.name
    finally:
        temp_file.close()


def _ssh_bash_run(host, command, check=True):
    return subprocess.run(
        ["ssh", host, f"bash -lc {shlex.quote(command)}"],
        check=check,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def _remote_runtime_prefix(rgs_path, activate_path, oga_dir):
    return (
        f"cd {shlex.quote(rgs_path)} && "
        f"source {shlex.quote(activate_path)} && "
        f"cd {shlex.quote(oga_dir)}"
    )


def run_remote_rtp(host, config):
    """Run RTP on a remote server inside tmux using a generated command file."""
    try:
        game_name = _get_current_folder_name()
        remote_config = _get_remote_config(config)
        rgs_path = _remote_rgs_path(remote_config)
        activate_path = _remote_activate_path(remote_config)
        oga_dir = _remote_oga_dir(remote_config)
        bash_dir = _remote_bash_dir(remote_config)
        remote_command_file = _remote_command_file_path(remote_config, game_name)
        session_name = _tmux_session_name(remote_config, game_name)
        install_path = _remote_install_path(remote_config, game_name)
        rtp_command = _build_remote_rtp_command(config, game_name)
    except ValueError as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)

    local_script_path = _write_remote_rtp_script(rgs_path, activate_path, oga_dir, rtp_command)
    remote_command_dir = os.path.dirname(remote_command_file)
    runtime_prefix = _remote_runtime_prefix(rgs_path, activate_path, oga_dir)
    remote_script_runner = f"sh {shlex.quote(os.path.join(bash_dir, os.path.basename(remote_command_file)))}"

    try:
        existing_sessions = _ssh_bash_run(host, f"{runtime_prefix} && tmux list-sessions", check=False)
        session_exists = session_name in (existing_sessions.stdout or "")
        if session_exists:
            print(
                f"RTP is already running in tmux session '{session_name}' on {host}. "
                "Not starting another run."
            )
            sys.exit(1)

        _ssh_bash_run(host, f"mkdir -p {shlex.quote(remote_command_dir)}")
        _run_checked(["scp", local_script_path, f"{host}:{remote_command_file}"])
        _ssh_bash_run(host, f"chmod +x {shlex.quote(remote_command_file)}")
        _ssh_bash_run(host, f"{runtime_prefix} && pip install {shlex.quote(install_path)}")
        _ssh_bash_run(
            host,
            f"{runtime_prefix} && tmux new -d -s {shlex.quote(session_name)} {shlex.quote(remote_script_runner)}",
        )
        started_sessions = _ssh_bash_run(host, f"{runtime_prefix} && tmux list-sessions", check=False)
        if session_name not in (started_sessions.stdout or ""):
            print(
                f"tmux session '{session_name}' was not found after startup on {host}.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Started RTP in tmux session '{session_name}' on {host}.")
        print(f"Remote command file: {remote_command_file}")
    except subprocess.CalledProcessError as error:
        print(f"Remote RTP command failed with exit code {error.returncode}.", file=sys.stderr)
        sys.exit(error.returncode)
    except FileNotFoundError as error:
        print(f"Required executable not found: {error}.", file=sys.stderr)
        sys.exit(1)
    finally:
        if os.path.exists(local_script_path):
            os.unlink(local_script_path)
