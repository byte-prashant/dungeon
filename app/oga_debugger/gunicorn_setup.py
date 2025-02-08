from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler
from app.utils import get_oga_directory
from app.utils import replace_sh_function

class SetTimeoutForGunicorn(Handler):
    file_path = ""

    def __init__(self):
        self.file_path = ""
        self.pipeline = Pipeline()
        super().__init__()

    def change_time_out(self):

        replace_sh_function(self.file_path+"/do","start_rgs",self.new_fun_def )

        return
    def new_function_definition(self):
        new_fun_def = """
function start_rgs() {
    if ! database_setup
    then
        return "$?"
    fi
        gunicorn --worker 1 --timeout 1200 --paste config.ini -b "${HOST:-0.0.0.0}":"${PORT:-6543}"11 "$@"

}
        """
        self.new_fun_def = new_fun_def.strip()

        return
    def get_file_path(self):
        self.file_path = get_oga_directory()
        return


    def build_operation_steps(self):
        self.pipeline.add_step(self.get_file_path)
        self.pipeline.add_step(self.new_function_definition)
        self.pipeline.add_step(self.change_time_out)
        return