from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler

class CreateLaunchJsonConfigVSCode(Handler):


    file_path = ""

    def __init__(self):
        self.file_path = ""
        self.pipeline = Pipeline()
        super().__init__()

    def write_config(self):
        return

    def get_file_path(self):
        return

    def build_operation_steps(self):
        self.pipeline.add_step(self.get_file_path)
        self.pipeline.add_step(self.write_config)
        return