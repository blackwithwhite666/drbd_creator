class Aggregator(object):
    '''
    Call multiple managers methods
    '''
    
    class Caller(object):
        def __init__(self, managers, name):
            self.managers = managers
            self.name = name
        
        def __call__(self, callback=None, specified_manager=False, **kwargs):
            result = []
            for manager in self.managers:
                if specified_manager and manager.name != specified_manager: continue
                if callable(callback):
                    callback(manager, getattr(manager, self.name)(**kwargs), **kwargs)
                else:
                    result.append(getattr(manager, self.name)(**kwargs))
            return result
            
    def __init__(self, managers):
        self.managers = managers
    
    def __getattr__(self, name):
        return self.Caller(self.managers, name)