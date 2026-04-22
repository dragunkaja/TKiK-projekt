import ply.lex as lex

#słowa kluczowe - mapowanie małych liter na nazwy tokenów
reserved = {
    'select': 'SELECT', 'delete': 'DELETE', 'move': 'MOVE', 'copy': 'COPY',
    'to': 'TO', 'from': 'FROM', 'dryrun': 'DRYRUN',
    'where': 'WHERE', 'order': 'ORDER', 'by': 'BY', 'limit': 'LIMIT',
    'asc': 'ASC', 'desc': 'DESC',
    'and': 'AND', 'or': 'OR', 'not': 'NOT', 'like': 'LIKE'
}

#lista wszystkich tokenów
tokens = [
    'OPERATOR', 'COMMA', 'SEMICOLON', 'STAR',
    'LPAREN', 'RPAREN', 'SIZE_UNIT',
    'ID', 'STRING', 'NUMBER'
] + list(reserved.values())

#reguły dla prostych tokenów
t_OPERATOR  = r'>=|<=|!=|=|>|<'
t_COMMA     = r','
t_SEMICOLON = r';'
t_STAR      = r'\*'
t_LPAREN    = r'\('
t_RPAREN    = r'\)'

#ignorowane znaki (spacje i tabulatory)
t_ignore = ' \t'

#reguły ze zdefiniowanymi akcjami (funkcje)
def t_SIZE_UNIT(t):
    r'(?i)(GB|MB|KB|B)\b'
    t.value = t.value.upper()
    return t

def t_STRING(t):
    r'\"[^\"]*\"|\'[^\']*\''
    t.value = t.value[1:-1]
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value.lower(), 'ID')
    return t

#śledzenie numerów linii (przydatne do błędów)
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

#obsługa błędów leksykalnych
def t_error(t):
    print(f"Błąd leksykalny: Nielegalny znak '{t.value[0]}' w linii {t.lexer.lineno}")
    t.lexer.skip(1)

lexer = lex.lex()