from typing import Optional
from app.oga_debugger.place_debugger import PlaceDebugger
from app.oga_debugger.import_game import ImportGameToDebug
from app.oga_debugger.gunicorn_setup import SetTimeoutForGunicorn
from app.oga_debugger.build_launch_json import CreateLaunchJsonConfigVSCode


def setup_debugger():
    increase_gunicorn_timeout = SetTimeoutForGunicorn()
    write_vscode_config = CreateLaunchJsonConfigVSCode()
    place_debugger = PlaceDebugger()
    import_game = ImportGameToDebug()
    increase_gunicorn_timeout.set_next(write_vscode_config).set_next(place_debugger).set_next(import_game)
    increase_gunicorn_timeout.handle()



setup_debugger()