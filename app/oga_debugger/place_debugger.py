from app.oga_debugger.pipeline import Pipeline
from app.oga_debugger.handler import Handler
from app.utils import get_oga_directory, replace_function
class PlaceDebugger(Handler):
    def __init__(self):
        self.file_path  =  ""
        self.pipeline =  Pipeline()
        super().__init__()

    def place_debugger(self):
        try:
            new_def = self.new_method_def()
            replace_function(self.file_path,"development_main",new_def)
            print(" Debugger placed to development file successfully!")
        except Exception as e:
            print(e)

    def new_method_def(self):

        new_def = """
def development_main(global_config, **settings):
    \"""
    config = Configurator(settings=settings)

    #config.add_route('users', '/admin/user', factory=UserFactory)

    app = config.make_wsgi_app()
    if ENABLE_FORCE_TOOL: app = RNGMockMiddleware(app)
    app = HTTPMethodOverrideMiddleware(app)
    app = HTTPHeaderRenameMiddleware(app, {'X-OGA-Accept': 'Accept'})
    app = HTTPReverseProxiedMiddleware(app)
    return app
    \"""
    print("development_main()")
    # -------- added config for vscode debugger----------
    import debugpy
    debugpy.listen(("localhost",5678))
    debugpy.wait_for_client()
    #-----------------------------------------
    
    config = Configurator(settings=settings)
    config.include("web")
    config.include("web.development")
    
    app = config.make_wsgi_app()

    if REVERSE_PROXY_MW:
        app = HTTPReverseProxiedMiddleware(app)
        print("HTTPReverseProxiedMiddleware active")

    if HEADER_RENAME_MW:
        app = HTTPHeaderRenameMiddleware(app, {"X-OGA-Accept": "Accept"})
        print("HTTPHeaderRenameMiddleware active")

    if METHOD_OVERRIDE_MW:
        app = HTTPMethodOverrideMiddleware(app)
        print("HTTPMethodOverrideMiddleware active")

    #
    # development specific-middlewares
    #
    if MOCK_RNG:
        app = RNGMockMiddleware(app)
        print("RNGMockMiddleware active")

    if SQLTAP_MW:
        app = SQLTapMiddleware(app)
        print("SQLTapMiddleware active")

    return app

    
    
    """

        return new_def

    def get_file_path(self):
        oga_direc = get_oga_directory()
        oga_direc = oga_direc + "/web/development.py"
        self.file_path = oga_direc
        return


    def build_operation_steps(self):

        self.pipeline.add_step(self.get_file_path)
        self.pipeline.add_step(self.place_debugger)
        return
