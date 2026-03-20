import os
import tempfile
import unittest
from unittest.mock import patch

from app.command_executer import _build_remote_rtp_command, run_remote_rtp


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
            ) as mock_ssh_bash_run:
                mock_ssh_bash_run.return_value.stdout = "rtp_sample-game: 1 windows (created Fri)"

                with self.assertRaises(SystemExit) as error:
                    run_remote_rtp("ubuntu@12.134.22.34", config)

        self.assertEqual(error.exception.code, 1)
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
            ):
                mock_ssh_bash_run.side_effect = [
                    type("Completed", (), {"stdout": "", "returncode": 1})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "", "returncode": 0})(),
                    type("Completed", (), {"stdout": "rtp_sample-game: 1 windows", "returncode": 0})(),
                ]

                run_remote_rtp("ubuntu@12.134.22.34", config)

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
