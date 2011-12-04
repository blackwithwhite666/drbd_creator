class BaseConfigParser(object):
    def __init__(self, content):
        self.content = content
        
    def parse(self):
        raise NotImplementedError()
    
    def get_config(self):
        raise NotImplementedError()
    
    @classmethod
    def create(cls, content):
        parser = cls(content)
        parser.parse()
        return parser.get_config()