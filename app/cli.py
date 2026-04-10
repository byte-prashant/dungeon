import argparse
import os

from app.build_folder_structure import create_structure_from_json
from app.utils import find_and_replace_version, load_game_commands, setup_yagmi
from app.command_executer import run_vt_runner, upload_engine, run_remote_rtp




def main():
    # Create top-level parser (yagmi command)
    parser = argparse.ArgumentParser(prog='yagmi', description="A simple CLI tool.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # 'dev' subcommand
    dev_parser = subparsers.add_parser('dev', help='Development-related commands')
    dev_subparsers = dev_parser.add_subparsers(dest='subcommand', help='Dev subcommands')
    setup =  dev_subparsers.add_parser('setup', help="Initialize a db")
    # 'init' subcommand under 'dev'
    dev_subparser_init = dev_subparsers.add_parser('init', help="Initialize a project")
    # 'install' subcommand under 'dev'
    dev_subparser_install = dev_subparsers.add_parser('install', help="Install a new game")

    # 'update_version' subcommand under 'dev'
    dev_subparser_update = dev_subparsers.add_parser('update_version', help="Update the project version")

    # 'test' subcommand under 'dev'
    dev_subparser_test = dev_subparsers.add_parser('test', help="Run test cases")
    dev_subparser_test.add_argument('-p', '--performance', action='store_true', help="Run performance test cases")
    dev_subparser_test.add_argument('-t', '--unit', action='store_true', help="Run unit test cases")

    dev_subparser_test = dev_subparsers.add_parser('debug', help="Run test cases")
    dev_subparser_test.add_argument('-a', '--activate', action='store_true', help="Activate debugging")
    dev_subparser_test.add_argument('-d', '--deactivate', action='store_true', help="Deactivate debugging")

    remote_parser = subparsers.add_parser('remote', help='Remote machine commands')
    remote_subparsers = remote_parser.add_subparsers(dest='subcommand', help='Remote subcommands')
    remote_upload_parser = remote_subparsers.add_parser('upload-engine', help='Upload the current folder to a remote engine path using scp')
    remote_upload_parser.add_argument('--host', required=True, help='Remote ssh target, for example ubuntu@12.134.22.34')
    remote_rtp_parser = remote_subparsers.add_parser('run-rtp', help='Run the current game RTP on a remote machine inside tmux')
    remote_rtp_parser.add_argument('--host', required=True, help='Remote ssh target, for example ubuntu@12.134.22.34')

    args = parser.parse_args()

    if args.command == 'dev':
        if args.subcommand == "setup":
            from app.utils import setup_yagmi
            setup_yagmi()

        elif args.subcommand == 'init':
            from app.build_folder_structure import create_structure_from_json
            client_name = input("Enter the client name: ")
            gamename = input("Enter the game name: ")
            print(f"Initializing project for client: {client_name} in {gamename}...")
            create_structure_from_json(client_name, gamename)

        elif args.subcommand == 'update_version':
            from app.utils import find_and_replace_version
            new_version = input("Enter the new version ex-> 0.2.0:    ")
            game_directory_path = os.getcwd()
            find_and_replace_version(game_directory_path, new_version)

        elif args.subcommand == 'test':
            from app.command_executer import run_vt_runner
            from app.utils import load_game_commands

            if args.performance:
                run_vt_runner("performance",load_game_commands() )  # Run performance test cases
            elif args.unit:
                run_vt_runner("test", load_game_commands())  # Run unit test cases
            else:
                print("Please specify a test type: -p for performance or -t for unit tests.")

        elif args.subcommand == 'debug':
            if args.activate:
                from app.oga_debugger.vscode_setup import setup_debugger
                setup_debugger()
    elif args.command == 'remote':
        if args.subcommand == 'upload-engine':
            upload_engine(args.host, load_game_commands())
        elif args.subcommand == 'run-rtp':
            run_remote_rtp(args.host, load_game_commands())

    else:
        print("Invalid command or subcommand")

if __name__ == '__main__':
    main()
