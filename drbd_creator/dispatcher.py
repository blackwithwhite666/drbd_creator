import logging

from .exceptions import CreatorException
from .managers import ManagerRegistry


logger = logging.getLogger('creator')


class DrbdParamsComputer(object):
    def __init__(self):
        self._port = None
        self._minor = None
    
    def add_port(self, port):
        self._port = max((self._port or 0, port))
    
    def add_minor(self, minor):
        self._minor = max((self._minor or 0, minor))
        
    @property
    def port(self):
        return 7788 if self._port is None else (self._port + 1)
    
    @property
    def minor(self):
        return 1 if self._minor is None else (self._minor + 1)
    


class Dispatcher(object):

    def __init__(self, name, size, group, primary_host, template, connections, dry_run=False):
        self.name = name
        self.size = size
        self.group = group
        self.primary_host = primary_host
        self.dry_run = dry_run
        self.template = template
        self.drbd_params = DrbdParamsComputer()
        self.managers = ManagerRegistry(connections=connections, dry_run=self.dry_run)
    
    
    def check_lvm_resource(self):
        '''
        Check needed LV and VG volumes
        '''
        def on_vg_not_exist(manager, result, **kwargs):
            if not result: raise CreatorException("Volume Group `%s' on host `%s' not exist" % (self.group, manager.name))
        
        def on_lv_exist(manager, result, **kwargs):
            if result: raise CreatorException("Logical Volume `%s' exist on host `%s' in group `%s'" % (self.name, manager.name, self.group))
        
        self.managers.lvm.vg_exist(group=self.group, callback=on_vg_not_exist)
        self.managers.lvm.lv_exist(group=self.group, name=self.name, callback=on_lv_exist)
    
    def check_drbd_resource(self):
        '''
        Check needed DRBD resources
        '''
        def on_resource_exist(manager, result, **kwargs):
            if result: raise CreatorException("DRBD Resource `%s' exist on host `%s'" % (self.name, manager.name))
        
        self.managers.drbd.check_drbd_resource(name=self.name, callback=on_resource_exist)
    
    def create_lvm_resource(self):
        '''
        Create needed lvm resource
        '''
        self.managers.lvm.create_lv(size=self.size, name=self.name, group=self.group)
    
    def compute_drbd_ports(self):
        '''
        Detect new DRBD port and device minor number
        '''
        lv_dev_path = self.managers.lvm.get_lv_path(group=self.group, name=self.name)[0]
        
        def update_port(manager, result, **kwargs):
            self.drbd_params.add_port(result)
        
        def update_minor(manager, result, **kwargs):
            self.drbd_params.add_minor(result)
        
        def check_disk(manager, result, **kwargs):
            if lv_dev_path == result:
                raise CreatorException("LV `%s' used in DRBD resource `%s' on host `%s'" % (result, kwargs['resource'], manager.name))
        
        def hosts_iterator(manager, result):
            for resource, hosts in result:
                if resource == self.name:
                    raise CreatorException("DRBD Resource `%s' exist on host `%s'" % (self.name, manager.name))
                for host in hosts:
                    self.managers.drbd.get_host_disk(resource=resource, host=host, callback=check_disk)
                    self.managers.drbd.get_host_port(resource=resource, host=host, callback=update_port)
                    self.managers.drbd.get_host_minor(resource=resource, host=host, callback=update_minor)
        
        self.managers.drbd.get_hosts(callback=hosts_iterator)

        if not self.drbd_params.port or not self.drbd_params.minor:
            raise CreatorException('Can`t detect new port and minor number')
        
        logger.info('New port number is %d and minor number is %d' % (self.drbd_params.port, self.drbd_params.minor))
    
    
    def create_drbd_config(self):
        '''
        Create DRBD config and put it to all nodes
        '''
        lv_path = self.managers.lvm.get_lv_path(group=self.group, name=self.name)[0]
        self.managers.drbd.save_drbd_config(name=self.name, 
                                            template=self.template, 
                                            port=self.drbd_params.port, 
                                            minor=self.drbd_params.minor, 
                                            lv_path=lv_path)
    
    def configure_drbd(self):
        '''
        Get up DRBD resource
        '''
        
        # Create drbd metadata on hosts
        self.managers.drbd.create_drbd_md(name=self.name)
        
        # Get up resource on hosts
        self.managers.drbd.up_drbd_resource(name=self.name)
        
        # Overwrite drbd resource on primary host
        self.managers.drbd.overwrite_drbd_peer(name=self.name, specified_manager=self.primary_host)
    
    def check_drbd_success(self):
        def on_resource_not_found(manager, result, **kwargs):
            if not result and not self.dry_run:
                raise CreatorException("Something goes wrong on host `%s'" % manager.name)
        
        self.managers.drbd.check_drbd_resource(callback=on_resource_not_found, name=self.name)
    
    def process(self):
        '''
        Create and sync drbd resource
        '''
        
        # Get host LV and check that new LV not exist on host
        self.check_lvm_resource()
        
        # Check that drbd resource not exist
        self.check_drbd_resource()
        
        # Get drbd config and compute new port and device minor number
        self.compute_drbd_ports()
        
        # Create LV on hosts
        self.create_lvm_resource()
        
        # Create drbd config and put in to hosts
        self.create_drbd_config()
        
        # Get up drbd resource
        self.configure_drbd()
        
        # Check newly created resources
        self.check_drbd_success()