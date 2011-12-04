class BaseManager(object):
    def __init__(self, runner):
        self.runner = runner
    
    @property
    def config(self):
        raise NotImplementedError()
    
    @property
    def name(self):
        return self.runner.host