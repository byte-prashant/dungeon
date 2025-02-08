from typing import Optional
class Handler:
    def __init__(self):
        self._next_handler: Optional[Handler] = None


    def set_next(self, handler:'Handler')-> 'Handler':

        self._next_handler  = handler
        return handler
    def  build_operation_steps(self):

        return
    def handle(self)->Optional[str]:
        try:
            self.build_operation_steps()
            if self.pipeline.steps:
                self.pipeline.execute()
            if self._next_handler:
                return self._next_handler.handle()

            return None
        except Exception as e:
            print("Error while execution ",e)