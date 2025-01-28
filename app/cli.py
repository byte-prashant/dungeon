# my_tool/cli.py
import argparse
import os

from app.build_folder_structure import create_structure_from_json
from app.utils import find_and_replace_version, load_game_commands
import argparse
import subprocess
import os
from vt_runner import run_vt_runner

def create_structure_from_json(client_name, gamename):
    # Placeholder function for creating folder structure
    print(f"Creating project structure for {client_name} and {gamename}")


def find_and_replace_version(game_directory_path, current_version, new_version):
    # Placeholder function for version update
    print(f"Updating version from {current_version} to {new_version}")


def run_performance_test():
    print("Running performance test cases...")
    subprocess.run(['yagmi', 'dev', 'test', '-p'])


def run_unit_test():
    print("Running unit test cases...")
    subprocess.run(['yagmi', 'dev', 'test', '-t'])


if __name__ == "__main__":
    # Create top-level parser (yagmi command)
    parser = argparse.ArgumentParser(prog='yagmi', description="A simple CLI tool.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 'dev' subcommand
    dev_parser = subparsers.add_parser('dev', help='Development-related commands')
    dev_subparsers = dev_parser.add_subparsers(dest='subcommand', help='Dev subcommands')

    # 'init' subcommand under 'dev'
    dev_subparser_init = dev_subparsers.add_parser('init', help="Initialize a project")

    # 'update_version' subcommand under 'dev'
    dev_subparser_update = dev_subparsers.add_parser('update_version', help="Update the project version")

    # 'test' subcommand under 'dev'
    dev_subparser_test = dev_subparsers.add_parser('test', help="Run test cases")
    dev_subparser_test.add_argument('-p', '--performance', action='store_true', help="Run performance test cases")
    dev_subparser_test.add_argument('-t', '--unit', action='store_true', help="Run unit test cases")

    args = parser.parse_args()

    if args.command == 'dev':
        if args.subcommand == 'init':
            client_name = input("Enter the client name: ")
            gamename = input("Enter the game name: ")
            print(f"Initializing project for client: {client_name} in {gamename}...")
            create_structure_from_json(client_name, gamename)

        elif args.subcommand == 'update_version':
            current_version = input("Enter the current version ex-> 0.2.0:    ")
            new_version = input("Enter the new version:    ")
            game_directory_path = os.getcwd()
            find_and_replace_version(game_directory_path, current_version, new_version)

        elif args.subcommand == 'test':

            if args.performance:
                run_vt_runner("performance",load_game_commands() )  # Run performance test cases
            elif args.unit:
                run_vt_runner("test", load_game_commands())  # Run unit test cases
            else:
                print("Please specify a test type: -p for performance or -t for unit tests.")

    else:
        print("Invalid command or subcommand")

if __name__ == '__main__':
    main()
