Version: 0.1.0

target goal
 -- Run test cases through it
        - unit test cases
        - vt runner

 -- design folder structure

Remote upload
 -- Add `remote.engine_path` to `game_command.json`
 -- Run `yagmi remote upload-engine --host ubuntu@12.134.22.34`
 -- The command uploads the current folder with `scp -r <folder_name> ubuntu@ip:/path/to/engine`

Remote RTP
 -- Remote flow uses `cd rgs`, `source venv/bin/activate`, then `cd OGA-4.8.1`
 -- Optionally set `remote.rgs_path`, `remote.oga_dir`, `remote.bash_dir`, `remote.command_file_path`, `remote.venv_activate`, `remote.tmux_session_prefix`, and `remote.install_base_path`
 -- Run `yagmi remote run-rtp --host ubuntu@12.134.22.34`
 -- The command checks `tmux list-sessions`, uploads `bash/<file_name>`, installs `engine/games/<game-name>`, and starts `tmux new -d 'sh bash/<file_name>'`
 -- If the tmux session for the current folder is already running, the command stops and informs the user
    
