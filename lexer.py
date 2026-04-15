import ply.lex as lex

reserved = {
    'select': 'SELECT',
    'from': 'FROM',
    'where': 'WHERE',
    'and': 'AND',
    'or': 'OR',
}

tokens = [
    'ID', 'STRING', 'NUMBER',
    'OPERATOR', 'COMMA', 'SEMICOLON', 'STAR'
] + list(reserved.values())

t_COMMA = r','
t_SEMICOLON = r';'
t_STAR = r'\*'
t_OPERATOR = r'>=|<=|!=|=|>|<'
t_ignore = ' \t'

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
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