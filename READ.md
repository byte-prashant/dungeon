target goal
 -- Run test cases through it
        - unit test cases
        - vt runner

 -- design folder structure

Remote upload
 -- Add `remote.engine_path` to `game_command.json`
 -- Run `yagmi remote upload-engine --host ubuntu@12.134.22.34`
 -- The command uploads the current folder with `scp -r <folder_name> ubuntu@ip:/path/to/engine`
    
