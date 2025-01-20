# my_tool/cli.py
import argparse
from app.build_folder_structure import create_structure_from_json
from app.utils import find_and_replace_version
def main():
    parser = argparse.ArgumentParser(description="A simple CLI tool.")
    parser.add_argument('command', type=str, choices=['dev'], help="Command to run")
    parser.add_argument('subcommand', type=str, choices=['init',"update_version"], help="Subcommand to run under dev")

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

    if args.command == 'dev' and args.subcommand == 'update_version':
        current_version = input("Enter the current version ex-> 0.1.0: ")
        new_version = input("Enter the current version ex-> 0.2.0: ")
        current_version = "version:"+current_version
        new_version = "version:"+new_version
        game_directory_path = input("enter game directory path ex -> /Users/pnt/development/OGA game/yo utr/")
        find_and_replace_version(game_directory_path,current_version,new_version)


    else:
        print("Invalid command or subcommand")


if __name__ == '__main__':
    main()
