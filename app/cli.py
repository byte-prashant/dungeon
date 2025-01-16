# my_tool/cli.py
import argparse
from app.buildFolderStructure import create_structure_from_json

def main():
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument('command', type=str, choices=['dev'], help="Command to run")
    parser.add_argument('subcommand', type=str, choices=['init'], help="Subcommand to run under dev")

    args = parser.parse_args()

    if args.command == 'dev' and args.subcommand == 'init':
        # Prompt for user input for client name and folder name
        # Prompt for user input for client name, folder name, and gamename
        client_name = input("Enter the client name: ")
        #folder_name = input("Enter the folder name where the project should be created: ")
        gamename = input("Enter the game name: ")

        print(f"Initializing project for client: {client_name} in {gamename}...")

        # Create the folder structure from the JSON#
        create_structure_from_json(client_name,gamename)
    else:
        print("Invalid command or subcommand")


if __name__ == '__main__':
    main()
