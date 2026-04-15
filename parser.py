import ply.yacc as yacc
from lexer import tokens

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
)
#              PROGRAM

def p_program(p):
    'program : query SEMICOLON'
    p[0] = p[1]


#              QUERY

def p_query(p):
    'query : SELECT column_list FROM STRING where_clause'
    p[0] = {
        'type': 'query',
        'columns': p[2],
        'path': p[4],
        'where': p[5]
    }

#          SELECT (kolumny)

def p_column_list_star(p):
    'column_list : STAR'
    p[0] = '*'

def p_column_list_single(p):
    'column_list : ID'
    p[0] = [p[1]]

def p_column_list_multiple(p):
    'column_list : column_list COMMA ID'
    p[0] = p[1] + [p[3]]

#              WHERE

def p_where_clause_empty(p):
    'where_clause :'
    p[0] = None

def p_where_clause(p):
    'where_clause : WHERE condition'
    p[0] = p[2]

#          WARUNKI (AND / OR)

def p_condition_logic(p):
    '''condition : condition AND condition
                 | condition OR condition'''
    p[0] = {
        'type': 'logic',
        'op': p[2],
        'left': p[1],
        'right': p[3]
    }

def p_condition_relation(p):
    'condition : ID OPERATOR value'
    p[0] = {
        'type': 'relation',
        'field': p[1],
        'op': p[2],
        'value': p[3]
    }

#              VALUE

def p_value_string(p):
    'value : STRING'
    p[0] = p[1]

def p_value_number(p):
    'value : NUMBER'
    p[0] = p[1]

#              BŁĘDY

def p_error(p):
    if p:
        print(f"Błąd składni przy '{p.value}' (typ: {p.type})")
    else:
        print("Błąd składni na końcu wejścia")

# Budowa parsera
parser = yacc.yacc()