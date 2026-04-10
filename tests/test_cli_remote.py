import unittest
from argparse import Namespace
from unittest.mock import patch

from app.cli import main


class CliRemoteCommandTests(unittest.TestCase):
    def test_remote_run_rtp_dispatches_executor(self):
        args = Namespace(command="remote", subcommand="run-rtp", host="ubuntu@12.134.22.34")

        with patch("argparse.ArgumentParser.parse_args", return_value=args), patch(
            "app.utils.load_game_commands", return_value={"remote": {}}
        ) as mock_load_commands, patch(
            "app.command_executer.run_remote_rtp"
        ) as mock_run_remote_rtp:
            main()

        mock_load_commands.assert_called_once_with()
        mock_run_remote_rtp.assert_called_once_with("ubuntu@12.134.22.34", {"remote": {}})

    def test_remote_upload_engine_dispatches_executor(self):
        args = Namespace(command="remote", subcommand="upload-engine", host="ubuntu@12.134.22.34")

        with patch("argparse.ArgumentParser.parse_args", return_value=args), patch(
            "app.utils.load_game_commands", return_value={"remote": {"engine_path": "/x"}}
        ) as mock_load_commands, patch(
            "app.command_executer.upload_engine"
        ) as mock_upload_engine:
            main()

        mock_load_commands.assert_called_once_with()
        mock_upload_engine.assert_called_once_with("ubuntu@12.134.22.34", {"remote": {"engine_path": "/x"}})

    def test_remote_pull_file_dispatches_executor(self):
        args = Namespace(
            command="remote",
            subcommand="pull-file",
            host="ubuntu@12.134.22.34",
            remote_path="/srv/rgs/tmp/report.xlsx",
            output_dir=".",
            recursive=False,
        )

        with patch("argparse.ArgumentParser.parse_args", return_value=args), patch(
            "app.command_executer.pull_remote_file"
        ) as mock_pull_remote_file:
            main()

        mock_pull_remote_file.assert_called_once_with(
            "ubuntu@12.134.22.34",
            "/srv/rgs/tmp/report.xlsx",
            ".",
            False,
        )


if __name__ == "__main__":
    unittest.main()
