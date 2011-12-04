from .config import Container, Section

class State(object):
    def __init__(self, dispatcher):
        self.dispatcher = dispatcher
    
    def open_bracket(self):
        raise NotImplementedError()
    
    def close_bracket(self):
        raise NotImplementedError()
    
    def create_param(self, param_type, name):
        raise NotImplementedError()
    
    def assign_value(self, value):
        raise NotImplementedError()
    
    def create_resource(self):
        raise NotImplementedError()
    
    def create_common(self):
        raise NotImplementedError()


class WaitOpenState(State):
    def open_bracket(self):
        self.dispatcher.state = self.dispatcher.param_state

class WaitCloseState(State):
    def close_bracket(self):
        pass


class ResourceState(State):
    def create_resource(self):
        section = Section('RESOURCE')
        self.dispatcher.config.append(section)
        self.dispatcher.current_section = section
        self.dispatcher.current_container = section.container
        self.dispatcher.state = self.dispatcher.resource_assign_state
    
    def create_common(self):
        section = Section('COMMON')
        self.dispatcher.config.append(section)
        self.dispatcher.current_container = section.container
        self.dispatcher.state = self.dispatcher.wait_open_state

class ResourceAssignState(State):
    def assign_value(self, value):
        self.dispatcher.current_section.resource = value.strip()
        self.dispatcher.state = self.dispatcher.wait_open_state


class ParamState(State):
    def create_param(self, param_type, name):
        container = Container(self.dispatcher.current_container)
        container.param_type = param_type
        container.name = name
        self.dispatcher.state = self.dispatcher.param_assign_state
    
    def open_bracket(self):
        self.dispatcher.current_container = self.dispatcher.current_container.last_descendant
        self.dispatcher.state = self.dispatcher.param_opened_state

    def close_bracket(self):
        self.dispatcher.current_container = self.dispatcher.current_container.parent
        self.dispatcher.state = self.dispatcher.param_state


class ParamOpenedState(ParamState):
    def open_bracket(self):
        State.open_bracket(self)


class ParamAssignState(ParamState):
    def assign_value(self, value):
        container = self.dispatcher.current_container.last_descendant
        container.value = value
        self.dispatcher.state = self.dispatcher.param_state