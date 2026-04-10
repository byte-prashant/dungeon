import os
import tarfile
import tempfile
import unittest
from unittest.mock import call, patch

from app.command_executer import (
    _build_remote_rtp_command,
    _collect_upload_paths,
    _write_remote_rtp_script,
    pull_remote_file,
    run_remote_rtp,
    upload_engine,
)


def _write_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as file_obj:
        file_obj.write(content)


class RemoteCommandTests(unittest.TestCase):
    def test_build_remote_rtp_command_uses_unique_redirect_target(self):
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

        command = _build_remote_rtp_command(
            config,
            "sample-game",
            "sample-game_rtp_20260410_120000_deadbeef.xlsx",
        )

        self.assertEqual(
            command,
            "vt-runner -c engines.games.sample.game_rtp.tests.volume_tester --progress-bar -n 1000 > sample-game_rtp_20260410_120000_deadbeef.xlsx",
        )

    def test_write_remote_rtp_script_includes_progress_messages(self):
        script_path = _write_remote_rtp_script(
            "rgs",
            "venv/bin/activate",
            "OGA-4.8.1",
            "vt-runner -c sample.tests.volume_tester --progress-bar",
            "rgs/OGA-4.8.1/sample-game_rtp_20260410_120000_deadbeef.xlsx",
        )

        try:
            with open(script_path, "r", encoding="utf-8") as script_file:
                script_body = script_file.read()
        finally:
            os.unlink(script_path)

        self.assertIn("echo '[run-rtp] Entering remote workspace: rgs'", script_body)
        self.assertIn("echo '[run-rtp] Activating environment: venv/bin/activate'", script_body)
        self.assertIn("echo '[run-rtp] Switching to OGA directory: OGA-4.8.1'", script_body)
        self.assertIn(
            "echo '[run-rtp] Report file: rgs/OGA-4.8.1/sample-game_rtp_20260410_120000_deadbeef.xlsx'",
            script_body,
        )
        self.assertIn("echo '[run-rtp] Starting RTP command.'", script_body)
        self.assertIn('echo "[run-rtp] RTP command exited with status ${status} after ${duration}s"', script_body)

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
                "app.command_executer._build_unique_rtp_report_name",
                return_value="sample-game_rtp_20260410_120000_deadbeef.xlsx",
            ), patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run, patch("builtins.print") as mock_print:
                mock_ssh_bash_run.side_effect = [
                    type("Completed", (), {"stdout": "rtp_sample-game: 1 windows (created Fri)", "returncode": 0})(),
                    type("Completed", (), {"stdout": "1.23 0.98 0.76 1/234 9999", "returncode": 0})(),
                ]

                with self.assertRaises(SystemExit) as error:
                    run_remote_rtp("ubuntu@12.134.22.34", config)

        self.assertEqual(error.exception.code, 1)
        mock_print.assert_has_calls(
            [
                call("[run-rtp] Preparing remote RTP run for 'sample-game'.", flush=True),
                call(
                    "[run-rtp] Unique report file for this run: sample-game_rtp_20260410_120000_deadbeef.xlsx",
                    flush=True,
                ),
                call(
                    "[run-rtp] Connecting to ubuntu@12.134.22.34 and checking tmux session 'rtp_sample-game'.",
                    flush=True,
                ),
                call("[run-rtp] Checking current load on ubuntu@12.134.22.34", flush=True),
                call("[run-rtp] Remote load average: 1.23, 0.98, 0.76", flush=True),
                call(
                    "RTP is already running in tmux session 'rtp_sample-game' on ubuntu@12.134.22.34. "
                    "Current remote load average: 1.23, 0.98, 0.76. Not starting another run."
                ),
            ]
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[0].args,
            ("ubuntu@12.134.22.34", "tmux list-sessions"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[1].args,
            ("ubuntu@12.134.22.34", "cat /proc/loadavg || uptime"),
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
                "app.command_executer._build_unique_rtp_report_name",
                return_value="sample-game_rtp_20260410_120000_deadbeef.xlsx",
            ), patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run, patch(
                "app.command_executer._run_checked"
            ) as mock_run_checked, patch(
                "app.command_executer.os.unlink"
            ), patch("builtins.print") as mock_print:
                mock_ssh_bash_run.side_effect = [
                    type("Completed", (), {"stdout": "", "returncode": 1})(),
                    type("Completed", (), {"stdout": "0.15 0.08 0.04 1/321 1234", "returncode": 0})(),
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
                    "[run-rtp] Unique report file for this run: sample-game_rtp_20260410_120000_deadbeef.xlsx",
                    flush=True,
                ),
                call(
                    "[run-rtp] Connecting to ubuntu@12.134.22.34 and checking tmux session 'rtp_sample-game'.",
                    flush=True,
                ),
                call("[run-rtp] Checking current load on ubuntu@12.134.22.34", flush=True),
                call("[run-rtp] Remote load average: 0.15, 0.08, 0.04", flush=True),
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
                call("The RTP run is detached and will continue even if this terminal disconnects."),
                call("Report file: sample-game_rtp_20260410_120000_deadbeef.xlsx"),
                call(
                    "Remote report path: rgs/OGA-4.8.1/sample-game_rtp_20260410_120000_deadbeef.xlsx"
                ),
                call("Remote log path: /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.log"),
                call("Remote command file: /srv/rgs/tmp/sample-game_rtp.sh"),
            ]
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[0].args,
            ("ubuntu@12.134.22.34", "tmux list-sessions"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[1].args,
            ("ubuntu@12.134.22.34", "cat /proc/loadavg || uptime"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[2].args,
            ("ubuntu@12.134.22.34", "mkdir -p /srv/rgs/tmp"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[3].args,
            ("ubuntu@12.134.22.34", "chmod +x /srv/rgs/tmp/sample-game_rtp.sh"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[4].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && pip install engine/games/sample-game",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[5].args,
            (
                "ubuntu@12.134.22.34",
                "cd rgs && source venv/bin/activate && cd OGA-4.8.1 && tmux new -d -s rtp_sample-game 'sh /srv/rgs/tmp/sample-game_rtp.sh > /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.log 2>&1'",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[6].args,
            ("ubuntu@12.134.22.34", "tmux list-sessions"),
        )
        self.assertEqual(mock_run_checked.call_count, 1)
        scp_command = mock_run_checked.call_args.args[0]
        self.assertEqual(scp_command[0], "scp")
        self.assertEqual(scp_command[2], "ubuntu@12.134.22.34:/srv/rgs/tmp/sample-game_rtp.sh")

    def test_pull_remote_file_downloads_existing_file(self):
        with tempfile.TemporaryDirectory() as temp_dir, patch(
            "app.command_executer._ssh_bash_run"
        ) as mock_ssh_bash_run, patch(
            "app.command_executer._run_checked"
        ) as mock_run_checked, patch("builtins.print") as mock_print:
            mock_ssh_bash_run.side_effect = [
                type("Completed", (), {"stdout": "", "returncode": 0})(),
                type("Completed", (), {"stdout": "", "returncode": 1})(),
            ]

            pull_remote_file(
                "ubuntu@12.134.22.34",
                "/srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx",
                temp_dir,
                False,
            )

        mock_print.assert_has_calls(
            [
                call(
                    "[pull-file] Connecting to ubuntu@12.134.22.34 and checking /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx",
                    flush=True,
                ),
                call(
                    f"[pull-file] Downloading /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx to {temp_dir}",
                    flush=True,
                ),
                call("Downloaded remote path from ubuntu@12.134.22.34."),
                call(
                    f"Local path: {temp_dir}/sample-game_rtp_20260410_120000_deadbeef.xlsx"
                ),
            ]
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[0].args,
            (
                "ubuntu@12.134.22.34",
                "test -e /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[1].args,
            (
                "ubuntu@12.134.22.34",
                "test -d /srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx",
            ),
        )
        self.assertEqual(
            mock_run_checked.call_args.args[0],
            [
                "scp",
                "ubuntu@12.134.22.34:/srv/rgs/tmp/sample-game_rtp_20260410_120000_deadbeef.xlsx",
                temp_dir,
            ],
        )


class UploadEngineTests(unittest.TestCase):
    def test_collect_upload_paths_skips_gitignored_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            game_dir = os.path.join(temp_dir, "sample-game")
            os.mkdir(game_dir)

            _write_file(
                os.path.join(game_dir, ".gitignore"),
                ".idea/\napp/file_content/\ndist/\n*.log\n!keep.log\n.gitignore\n",
            )
            _write_file(os.path.join(game_dir, ".idea", "workspace.xml"))
            _write_file(os.path.join(game_dir, "app", "file_content", "generated.py"))
            _write_file(os.path.join(game_dir, "app", "main.py"))
            _write_file(os.path.join(game_dir, "dist", "bundle.js"))
            _write_file(os.path.join(game_dir, "logs", "test.log"))
            _write_file(os.path.join(game_dir, "logs", "keep.log"))

            selected_directories, selected_files, skipped_paths = _collect_upload_paths(game_dir)

        self.assertIn("app", selected_directories)
        self.assertIn("logs", selected_directories)
        self.assertIn("app/main.py", selected_files)
        self.assertIn("logs/keep.log", selected_files)
        self.assertNotIn(".gitignore", selected_files)
        self.assertNotIn("app/file_content/generated.py", selected_files)
        self.assertNotIn("dist/bundle.js", selected_files)
        self.assertNotIn("logs/test.log", selected_files)
        self.assertIn(".idea/", skipped_paths)
        self.assertIn("app/file_content/", skipped_paths)

    def test_upload_engine_uploads_filtered_archive_and_extracts_remote(self):
        config = {
            "remote": {
                "engine_path": "/srv/engine",
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            game_dir = os.path.join(temp_dir, "sample-game")
            os.mkdir(game_dir)

            _write_file(os.path.join(game_dir, ".gitignore"), "build/\n.gitignore\n")
            _write_file(os.path.join(game_dir, "app", "main.py"), "print('ok')\n")
            _write_file(os.path.join(game_dir, "build", "output.txt"), "skip\n")

            captured_upload = {}

            def capture_upload(command, **kwargs):
                captured_upload["command"] = command
                with tarfile.open(command[1], "r:gz") as archive:
                    captured_upload["members"] = sorted(archive.getnames())

            with patch("app.command_executer.os.getcwd", return_value=game_dir), patch(
                "app.command_executer._run_checked", side_effect=capture_upload
            ) as mock_run_checked, patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run:
                upload_engine("ubuntu@12.134.22.34", config)

        self.assertEqual(mock_run_checked.call_count, 1)
        self.assertEqual(captured_upload["command"][0], "scp")
        self.assertEqual(
            captured_upload["command"][2],
            "ubuntu@12.134.22.34:/srv/engine/.sample-game_upload.tar.gz",
        )
        self.assertIn("sample-game/app", captured_upload["members"])
        self.assertIn("sample-game/app/main.py", captured_upload["members"])
        self.assertNotIn("sample-game/.gitignore", captured_upload["members"])
        self.assertNotIn("sample-game/build/output.txt", captured_upload["members"])
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[0].args,
            ("ubuntu@12.134.22.34", "mkdir -p /srv/engine"),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[1].args,
            (
                "ubuntu@12.134.22.34",
                "tar -xzf /srv/engine/.sample-game_upload.tar.gz -C /srv/engine",
            ),
        )
        self.assertEqual(
            mock_ssh_bash_run.call_args_list[2].args,
            ("ubuntu@12.134.22.34", "rm -f /srv/engine/.sample-game_upload.tar.gz"),
        )
        self.assertEqual(mock_ssh_bash_run.call_args_list[2].kwargs, {"check": False})

    def test_upload_engine_stops_when_everything_is_ignored(self):
        config = {
            "remote": {
                "engine_path": "/srv/engine",
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            game_dir = os.path.join(temp_dir, "sample-game")
            os.mkdir(game_dir)

            _write_file(os.path.join(game_dir, ".gitignore"), "*\n")
            _write_file(os.path.join(game_dir, "ignored.txt"), "skip\n")

            with patch("app.command_executer.os.getcwd", return_value=game_dir), patch(
                "app.command_executer._run_checked"
            ) as mock_run_checked, patch(
                "app.command_executer._ssh_bash_run"
            ) as mock_ssh_bash_run:
                with self.assertRaises(SystemExit) as error:
                    upload_engine("ubuntu@12.134.22.34", config)

        self.assertEqual(error.exception.code, 1)
        mock_run_checked.assert_not_called()
        mock_ssh_bash_run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
