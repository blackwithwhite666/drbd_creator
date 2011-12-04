import os

from drbd_creator.utils import cached_property
from drbd_creator.parsers import LvmConfigParser

from .base import BaseManager


class LvmManager(BaseManager):
    '''
    LVM commands
    '''
    
    @cached_property()
    def config(self):
        return LvmConfigParser.create(self.runner.query('lvs -o name,vg_name'))
    
    def vg_exist(self, group):
        return group in self.config
    
    def lv_exist(self, group, name):
        return self.config.vg_contain(group, name)
    
    def create_lv(self, size, name, group):
        return self.runner.execute('lvcreate -L %s -n %s %s' % (size, name, group))
    
    def get_lv_path(self, group, name):
        return os.path.join('/dev', group, name)