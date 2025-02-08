from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler
from app.utils import get_engine_class, get_oga_directory,replace_function
from app.oga_debugger.utils import replace_method_in_file
import os


class ImportGameToDebug(Handler):

    def __init__(self):
        self.file_path  =  ""
        self.pipeline =  Pipeline()
        super().__init__()

    def place_import(self):
        try:
            new_def = self.get_new_engine_method()
            replace_method_in_file(self.file_path, "HostGame", "get_engine", new_def)
            print(" engine import method has been updated successfully")

        except Exception as e:
            print(e)

        return


    def get_new_engine_method(self):
        """
        -- obviously we can improve following algo, by reading the config file from
        engine games
        :return:
        """

        get_engine_method =  """
def get_engine(self, logger, parameters):
    if hasattr(self, "_engine"):
            return self._engine
    else:
        from pathlib import Path
        import json
        config = {}
        # Get the current script's directory
        current_dir = Path(__file__).resolve().parent

        # Navigate to the parent directory
        parent_dir = current_dir.parent
        # Define the path to the .yagmi folder
        yagmi_folder = parent_dir / ".yagmi"

        # Check if the folder exists
        if yagmi_folder.exists() and yagmi_folder.is_dir():
            file_path = Path(yagmi_folder)
            if file_path.exists():
                with open(yagmi_folder+"/config.py", 'r') as file:
                    config = json.load(file)
        import importlib
        if 'engine' in config and config['engine']:
            path_parts = config['engine'].split(".")
            engine_path = ".".join(path_parts)
            engine_class = path_parts.pop(-1)
            module = importlib.import_module('engines.games.'+engine_path)
            game_class = getattr(module,engine_class)
            self._engine = game_class(logger=logger, parameters=parameters)
            return self._engine
        else:
            self._engine =  ""
            return self._engine
"""

        return get_engine_method

    def get_game_path(self):
        oga_direc = get_oga_directory()
        oga_direc = oga_direc+"/OGA/db/models.py"
        self.file_path = oga_direc
        return


    def build_operation_steps(self):

        self.pipeline.add_step(self.get_game_path)
        self.pipeline.add_step(self.place_import)
        return
