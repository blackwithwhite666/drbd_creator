import ply.lex as lex

class DrbdConfigLexerException(Exception):
    pass

class DrbdConfigLexer:
    reserved = {
        'on' : 'HOST',
        'resource': 'RESOURCE',
        'common': 'COMMON',
        'global': 'GLOBAL',
    }
    
    # List of token names.   This is always required
    tokens = [
       'LBRACKET',
       'RBRACKET',
       'SEMICOLON',
       'NAME',
       'VALUE',
       'COMMENT'
    ] + list(reserved.values())

    states = (
        ('brackets', 'inclusive'),
        ('assignment', 'exclusive'),
    )
    
    
    # Rules for the ccode state
    def t_brackets_LBRACKET(self, t):     
        r'\{'
        t.lexer.level += 1
        return t
    
    def t_brackets_RBRACKET(self, t):
        r'\}'
        t.lexer.level -= 1
        
        # If closing brace, return the code fragment
        if t.lexer.level == 0:
            t.lexer.lineno += t.value.count('\n')
            t.lexer.begin('INITIAL')           
            return t
        
        return t
    
    # Ignored characters (whitespace)
    t_brackets_ignore = ' \t\n'
    
    # For bad characters, we just skip over it
    def t_brackets_error(self, t):
        self.t_error(t)
    
    
    def t_assignment_VALUE(self, t):
        r'[\d\s\w\-\:/.]+'
        return t
    
    def t_assignment_SEMICOLON(self, t):
        r'\;'
        t.lexer.pop_state()
        pass
    
    def t_assignment_LBRACKET(self, t):
        r'\{'
        self.t_brackets_LBRACKET(t)
        t.lexer.begin('brackets')
        return t
    
    # Ignored characters (whitespace)
    t_assignment_ignore = ' \t\n'
    
    # For bad characters, we just skip over it
    def t_assignment_error(self, t):
        self.t_error(t)
    
    
    def t_NAME(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_\-]+'
        t.type = self.reserved.get(t.value, 'NAME')    # Check for reserved words
        t.lexer.push_state('assignment')
        return t
    
    def t_COMMENT(self, t):
        r'\#.*'
        pass
    
    # A string containing ignored characters (spaces and tabs)
    t_ignore = ' \t\n'

    # Error handling rule
    def t_error(self, t):
        raise DrbdConfigLexerException("Illegal character '%s'" % t.value[0])
    
    
    # Build the lexer
    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        self.lexer.level = 0
    
    # Test it output
    def parse(self, data):
        self.lexer.input(data)
        while True:
            tok = self.lexer.token()
            if not tok: break
            yield tok
        if self.lexer.level:
            raise DrbdConfigLexerException("Bracket not closed")
