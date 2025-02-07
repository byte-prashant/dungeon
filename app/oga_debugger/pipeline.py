from typing import Callable, Any

# define a step as a callable

Step = Callable[[Any], Any]

class Pipeline:
    def __init__(self):
        self.steps = []

    def add_step(self,step:Step):
        self.steps.append(step)


    def execute(self):
        for step in self.steps:
            data = step()

        return data

