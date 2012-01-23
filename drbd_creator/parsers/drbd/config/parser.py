from drbd_creator.parsers.base import BaseConfigParser

from .lexer import DrbdConfigLexer
from .config import Configuration
from .state import (ResourceState, ResourceAssignState, ParamState, 
                    ParamOpenedState, ParamAssignState, WaitOpenState, 
                    WaitCloseState)


class DrbdConfigParser(BaseConfigParser):
    
    def __init__(self, content):
        super(DrbdConfigParser, self).__init__(content)
        
        self.config = Configuration()
        
        self.current_section = None
        self.current_container = None
        self.level = 0
        
        self.resource_state = ResourceState(self)
        self.resource_assign_state = ResourceAssignState(self)
        
        self.param_state = ParamState(self)
        self.param_opened_state = ParamOpenedState(self)
        self.param_assign_state = ParamAssignState(self)
        
        self.wait_open_state = WaitOpenState(self)
        self.wait_close_state = WaitCloseState(self)
        
        self.state = self.resource_state
    
    def process_token(self, token):
        if token.type == 'RESOURCE':
            self.state.create_resource()
        elif token.type == 'COMMON':
            self.state.create_common()
        elif token.type == 'GLOBAL':
            self.state.create_global()
        elif token.type == 'NAME' or token.type == 'HOST':
            self.state.create_param(token.type, token.value)
        elif token.type == 'VALUE':
            self.state.assign_value(token.value)
        elif token.type == 'LBRACKET':
            self.state.open_bracket()
            self.level += 1
        elif token.type == 'RBRACKET':
            self.state.close_bracket()
            self.level -= 1
            
        if self.level == 0 and token.type == 'RBRACKET':
            self.state = self.resource_state
    
    def parse(self):
        map(self.process_token, DrbdConfigLexer().parse(self.content))
        self.config.build()
        
    def get_config(self):
        return self.config