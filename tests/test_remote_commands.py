import os
import tempfile
import unittest
from unittest.mock import call, patch

from app.command_executer import (
    _build_remote_rtp_command,
    _write_remote_rtp_script,
    run_remote_rtp,
)


class RemoteCommandTests(unittest.TestCase):
    def test_build_remote_rtp_command_uses_defaults_and_redirect(self):
        config = {
            "sample-game": {
                "rtp": {
                    "module_name": "engines.games.sample.game_rtp",
                    "command_parameters": {
                        "n": {"param_name": "-n", "default": 1000},
                        "filename": {"param_name": "-- >", "default": "rtp_report.xlsx"},
                    },
                }
            }
        }

        command = _build_remote_rtp_command(config, "sample-game")

        self.assertEqual(
            command,
            "vt-runner -c engines.games.sample.game_rtp.tests.volume_tester --progress-bar -n 1000 > rtp_report.xlsx",
        )

    def test_write_remote_rtp_script_includes_progress_messages(self):
        script_path = _write_remote_rtp_script(
            "rgs",
            "venv/bin/activate",
            "OGA-4.8.1",
            "vt-runner -c sample.tests.volume_tester --progress-bar",
        )

        try:
            with open(script_path, "r", encoding="utf-8") as script_file:
                script_body = script_file.read()
        finally:
            os.unlink(script_path)

        self.assertIn("echo '[run-rtp] Entering remote workspace: rgs'", script_body)
        self.assertIn("echo '[run-rtp] Activating environment: venv/bin/activate'", script_body)
        self.assertIn("echo '[run-rtp] Switching to OGA directory: OGA-4.8.1'", script_body)
        self.assertIn("echo '[run-rtp] Starting RTP command.'", script_body)

    def test_run_remote_rtp_stops_when_session_already_exists(self):
        config = {
            "sample-game": {
                "rtp": {
                    "module_name": "engines.games.sample.game_rtp",
                    "command_parameters": {},
                }
            },
            "remote": {
                "command_dir": "/srv/rgs/tmp",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            game_dir = os.path.join(temp_dir, "sample-game")
            os.mkdir(game_dir)

            with patch("app.command_executer.os.getcwd", return_value=game_dir), patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run, patch("builtins.print") as mock_print:
                mock_ssh_bash_run.return_value.stdout = "rtp_sample-game: 1 windows (created Fri)"

                with self.assertRaises(SystemExit) as error:
                    run_remote_rtp("ubuntu@12.134.22.34", config)

        self.assertEqual(error.exception.code, 1)
        mock_print.assert_has_calls(
            [
                call("[run-rtp] Preparing remote RTP run for 'sample-game'.", flush=True),
                call(
                    "[run-rtp] Connecting to ubuntu@12.134.22.34 and checking tmux session 'rtp_sample-game'.",
                    flush=True,
                ),
                call(
                    "RTP is already running in tmux session 'rtp_sample-game' on ubuntu@12.134.22.34. "
                    "Not starting another run."
                ),
            ]
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args.args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && tmux list-sessions",
            ),
        )

    def test_run_remote_rtp_uploads_script_and_starts_tmux(self):
        config = {
            "sample-game": {
                "rtp": {
                    "command": "vt-runner -c sample.tests.volume_tester --progress-bar",
                }
            },
            "remote": {
                "command_dir": "/srv/rgs/tmp",
                "venv_activate": "venv/bin/activate",
                "tmux_session_prefix": "rtp",
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            game_dir = os.path.join(temp_dir, "sample-game")
            os.mkdir(game_dir)

            with patch("app.command_executer.os.getcwd", return_value=game_dir), patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run, patch(
                "app.command_executer._run_checked"
            ) as mock_run_checked, patch(
                "app.command_executer.os.unlink"
            ), patch("builtins.print") as mock_print:
                mock_ssh_bash_run.side_effect = [
                    type("Completed", (), {"stdout": "", "returncode": 1})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "rtp_sample-game: 1 windows", "returncode": 0})(),
                ]

                run_remote_rtp("ubuntu@12.134.22.34", config)

        mock_print.assert_has_calls(
            [
                call("[run-rtp] Preparing remote RTP run for 'sample-game'.", flush=True),
                call(
                    "[run-rtp] Connecting to ubuntu@12.134.22.34 and checking tmux session 'rtp_sample-game'.",
                    flush=True,
                ),
                call("[run-rtp] Ensuring remote command directory exists: /srv/rgs/tmp", flush=True),
                call(
                    "[run-rtp] Uploading generated bash file to /srv/rgs/tmp/sample-game_rtp.sh",
                    flush=True,
                ),
                call(
                    "[run-rtp] Making uploaded script executable: /srv/rgs/tmp/sample-game_rtp.sh",
                    flush=True,
                ),
                call(
                    "[run-rtp] Activating the remote environment and installing engine/games/sample-game",
                    flush=True,
                ),
                call("[run-rtp] Starting tmux session 'rtp_sample-game'", flush=True),
                call("[run-rtp] Verifying tmux session 'rtp_sample-game' is running", flush=True),
                call("Started RTP in tmux session 'rtp_sample-game' on ubuntu@12.134.22.34."),
                call("Remote command file: /srv/rgs/tmp/sample-game_rtp.sh"),
            ]
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[0].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && tmux list-sessions",
            ),
        )
        self.assertEqual(mock_ssh_bash_run.call_args_list[1].args, ("ubuntu@12.134.22.34", "mkdir -p /srv/rgs/tmp"))
        self.assertEqual(mock_ssh_bash_run.call_args_list[2].args, ("ubuntu@12.134.22.34", "chmod +x /srv/rgs/tmp/sample-game_rtp.sh"))
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[3].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && pip install engine/games/sample-game",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[4].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && tmux new -d -s rtp_sample-game 'sh bash/sample-game_rtp.sh'",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[5].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && tmux list-sessions",
            ),
        )
        self.assertEqual(mock_run_checked.call_count, 1)
        scp_command = mock_run_checked.call_args.args[0]
        self.assertEqual(scp_command[0], "scp")
        self.assertEqual(scp_command[2], "ubuntu@12.134.22.34:/srv/rgs/tmp/sample-game_rtp.sh")


if __name__ == "__main__":
    unittest.main()
