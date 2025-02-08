from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler
from app.utils import get_engine_class, get_oga_directory, create_and_update_yagmi_config
import os
import json
class CreateLaunchJsonConfigVSCode(Handler):


    file_path = ""

    def __init__(self):
        self.file_path = ""
        self.pipeline = Pipeline()
        super().__init__()

    def write_config(self):
        config = self.develop_config()
        # Write back to the JSON file
        create_and_update_yagmi_config(self.file_path, config, "launch.json")
    def develop_config(self):
        local, remote = self.get_engine_file_paths()
        config =  {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Attach to Debugpy",
                    "type": "debugpy",
                    "request": "attach",
                    "connect": {
                        "host": "localhost",
                        "port": 5678
                    },
                    "justMyCode": True,
                "pathMappings": [
                {
                    "localRoot": local+"/",
                    "remoteRoot": remote+"/"
                }
            ]
            }
            ]
            }
        print(config)
        return config
    def get_engine_file_paths(self):
        """
        This method is to get the local root of the engine file
        and remote file of engine, which is inside the build
        :return:
        """
        engine_class_path , engine_class = get_engine_class()
        oga_direc = get_oga_directory()
        parts =  engine_class_path.split(".")
        print("2", engine_class_path,parts)
        # dropping engine file name
        parts.pop(-1)
        print("hello1")
        # prepare the local_root


        #prepare the remote path
        game_directory =  os.getcwd().split("/")
        game_directory = game_directory[-1]

        print("2", parts)
        game_directory = oga_direc+"/"+"engines/games/"+game_directory
        local_root = game_directory + "/"+"/".join(parts)
        remote_path = game_directory+"/build/lib/"+"/".join(parts)



        print("Remote path wil be ", remote_path)
        print("Local root of the file", local_root)

        return  local_root, remote_path
    def get_file_path(self):
        oga_direc = get_oga_directory()
        self.file_path = oga_direc+"/.vscode"
        return

    def build_operation_steps(self):
        self.pipeline.add_step(self.get_file_path)
        self.pipeline.add_step(self.write_config)
        return