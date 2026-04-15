import ply.lex as lex

tokens = (
    'SELECT', 'FROM', 'WHERE', 'AND', 'OR',
    'ID', 'STRING', 'NUMBER',
    'OPERATOR',
    'COMMA', 'SEMICOLON', 'STAR'
)

t_COMMA = r','
t_SEMICOLON = r';'
t_STAR = r'\*'
t_OPERATOR = r'>=|<=|!=|=|>|<'

t_ignore = ' \t'

def t_SELECT(t):
    r'(?i)SELECT'
    return t

def t_FROM(t):
    r'(?i)FROM'
    return t

def t_WHERE(t):
    r'(?i)WHERE'
    return t

def t_AND(t):
    r'(?i)AND'
    return t

def t_OR(t):
    r'(?i)OR'
    return t


def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_STRING(t):
    r'"[^"]*"'
    t.value = t.value.strip('"')
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print(f"Nieznany znak: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()