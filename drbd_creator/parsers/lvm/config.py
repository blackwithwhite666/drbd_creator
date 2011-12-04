from drbd_creator.parsers.base import BaseConfigParser


class Configuration(dict):
    def __init__(self):
        pass
    
    def vg_contain(self, vg, lv):
        return unicode(vg) in self and unicode(lv) in self[vg]


class LvmConfigParser(BaseConfigParser):
    def __init__(self, content):
        super(LvmConfigParser, self).__init__(content)
        self.config = Configuration()
        
    def parse(self):
        def split_line(line):
            return map(lambda part: unicode(part.strip()), " ".join(line.split()).split(' '))
        
        lines = self.content.splitlines()
        for lv, vg in map(split_line, lines[1:]):
            self.config.setdefault(vg, []).append(lv)
            
    def get_config(self):
        return self.config
