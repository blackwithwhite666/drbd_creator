import weakref

class Configuration(dict):
    def __init__(self):
        self.sections = []
        self.common = None
    
    def append(self, item):
        self.sections.append(item)
        
    def build(self):
        for section in self.sections:
            section.build()
            if section.type == 'RESOURCE':
                self[section.resource] = section
            else:
                self.common = section

class Section(object):
    def __init__(self, section_type):
        self.type = section_type
        self.resource = None
        self.hosts = {}
        self.params = {}
        self.container = Container()
    
    def build(self):
        def update(d, container):
            for subcontainer in container:
                d.update({subcontainer.name: subcontainer.value})
        
        def get_dict(base, name):
            name = name.strip()
            base[name] = d = base.get(name, {})
            return d
        
        for container in self.container:
            if container.param_type == 'NAME':
                d = get_dict(self.params, container.name)
            elif container.param_type == 'HOST':
                d = get_dict(self.hosts, container.name)
            update(d, container)


class Container(object):
    def __init__(self, parent=None, param_type=None, name=None, value=None):
        self._descendants = []
        self._weak_parent = None
        self._value = None
        
        if parent is not None:
            parent.append(self)
            self._weak_parent = weakref.ref(parent)
        
        self.param_type = param_type
        self.name = name
        self.value = value
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, value):
        if self.param_type == 'HOST':
            self.name = value
        else:
            self._value = value
    
    @property
    def parent(self):
        return (self._weak_parent or (lambda: None))()
    
    def append(self, item):
        self._descendants.append(item)
        
    @property
    def last_descendant(self):
        return self._descendants[-1]
    
    def __iter__(self):
        return iter(self._descendants)
    
    def __repr__(self):
        return '<Container %s:%s:%s>' % tuple(map(lambda item: item or '', (self.param_type, self.name, self.value)))