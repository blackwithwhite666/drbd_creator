from .executor import Executor
from .aggregator import Aggregator
from .drbd_manager import DrbdManager
from .lvm_manager import LvmManager


class ManagerRegistry(object):
    class_mapping = (
                     ('drbd', DrbdManager),
                     ('lvm', LvmManager),
                     )
    
    def __init__(self, connections, dry_run=False):
        self.connections = connections
        self.dry_run = dry_run
        self.managers = {}
        self.class_dict = dict(self.class_mapping)
        
    def create(self, name):
        managers = map(lambda conn: self.class_dict[name](runner=Executor(conn, dry_run=self.dry_run)), self.connections)
        return Aggregator(managers)
    
    def __getattr__(self, name):
        try:
            manager = self.managers[name]
        except KeyError:
            if name not in self.class_dict:
                raise AttributeError
            manager = self.managers[name] = self.create(name)
        return manager