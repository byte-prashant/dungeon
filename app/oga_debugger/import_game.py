from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler
from app.utils import get_engine_class, get_oga_directory,replace_function
import os


class ImportGameToDebug(Handler):

    def __init__(self):
        self.file_path  =  ""
        self.pipeline =  Pipeline()
        super().__init__()

    def place_import(self):
        new_def = self.get_new_engine_method()
        replace_function(self.file_path, "get_engine", new_def )
        return


    def get_new_engine_method(self):
        engine_path, engine_class = get_engine_class()
        get_engine_method =  """
        def get_engine(self, logger, parameters):
            if hasattr(self, "_engine"):
                return self._engine
            else:
                import importlib
                module = importlib.import_module('engines.games."""+engine_path+"""')
                game_class = getattr(module,'"""+engine_class+"""')
                self._engine = game_class(logger=logger, parameters=parameters)
                return self._engine
        """

        return get_engine_method
    def get_game_path(self):
        oga_direc = get_oga_directory()
        oga_direc = oga_direc+"OGA/db/models.py"
        self.file_path = oga_direc
        return


    def build_operation_steps(self):

        self.pipeline.add_step(self.get_game_path)
        self.pipeline.add_step(self.place_import)
        return
