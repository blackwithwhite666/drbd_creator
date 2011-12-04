import logging
import re
import os
from tempfile import NamedTemporaryFile

from drbd_creator.utils import cached_property
from drbd_creator.parsers import DrbdConfigParser
from drbd_creator.exceptions import RunException

from .base import BaseManager

logger = logging.getLogger('managers.drbd')


class DrbdManager(BaseManager):
    '''
    DRBD commands
    '''
    
    DISK_MATCH = re.compile('^.+minor ([\d]+)$')
    PORT_MATCH = re.compile('^.+\:([\d]+)$')
    
    @cached_property()
    def config(self):
        return DrbdConfigParser.create(self.runner.query('drbdadm dump'))

    def check_drbd_resource(self, name):
        try:
            self.runner.query('drbdadm sh-dev %s' % name)
            return True
        except RunException, e:
            logger.debug(e.message)
            return False
    
    def drbd_file_exist(self, path):
        try:
            self.runner.query('test -e %s' % path)
            return True
        except RunException, e:
            logger.debug(e.message)
            return False
    
    def create_drbd_config(self, path, content):
        if not self.drbd_file_exist(path):
            f = NamedTemporaryFile()
            f.write(content)
            f.flush()
            self.runner.put(f.name, path)
            
    def create_drbd_md(self, name):
        return self.runner.execute('drbdadm create-md %s' % name)
    
    def up_drbd_resource(self, name):
        return self.runner.execute('drbdadm up %s' % name)
    
    def overwrite_drbd_peer(self, name):
        return self.runner.execute('drbdadm -- --overwrite-data-of-peer primary %s' % name)
    
    def get_hosts(self):
        for resource, section in self.config.items():
            yield (resource, section.hosts.keys())
    
    def get_host_disk(self, resource, host):
        params = self.config[resource].hosts[host]
        return params['disk']
    
    def get_host_port(self, resource, host):
        params = self.config[resource].hosts[host]
        return int(self.PORT_MATCH.match(params['address']).group(1))
    
    def get_host_minor(self, resource, host):
        params = self.config[resource].hosts[host]
        return int(self.DISK_MATCH.match(params['device']).group(1))
    
    def generate_drbd_config(self, template, port, minor, name, lv_path):
        return template % {'port': port, 'minor': minor, 'name': name, 'lv_path': self.lv_path}
    
    def generate_drbd_path(self, name):
        return os.path.join('/etc', 'drbd.d', '%s.res' % name)
    
    def save_drbd_config(self, name, template, port, minor, lv_path):
        path = self.generate_drbd_path(name)
        content = self.generate_drbd_config(template, port, minor, name, lv_path)
        self.create_drbd_config(path, content)