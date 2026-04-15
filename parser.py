import ply.yacc as yacc
from lexer import tokens

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
)

# GRAMATYKA

def p_program(p):
    'program : query SEMICOLON'
    p[0] = p[1]

def p_query(p):
    'query : SELECT column_list FROM STRING where_clause'
    p[0] = {
        'type': 'query',
        'columns': p[2],
        'path': p[4],
        'where': p[5]
    }

def p_column_list_star(p):
    'column_list : STAR'
    p[0] = '*'

def p_column_list_ids(p):
    'column_list : id_list'
    p[0] = p[1]

def p_id_list_single(p):
    'id_list : ID'
    p[0] = [p[1]]

def p_id_list_multiple(p):
    'id_list : ID COMMA id_list'
    p[0] = [p[1]] + p[3]

def p_where_clause_empty(p):
    'where_clause :'
    p[0] = None

def p_where_clause(p):
    'where_clause : WHERE condition_list'
    p[0] = p[2]

def p_condition_single(p):
    'condition_list : condition'
    p[0] = p[1]

def p_condition_and(p):
    'condition_list : condition_list AND condition_list'
    p[0] = ('AND', p[1], p[3])

def p_condition_or(p):
    'condition_list : condition_list OR condition_list'
    p[0] = ('OR', p[1], p[3])

def p_condition(p):
    'condition : ID OPERATOR value'
    p[0] = (p[1], p[2], p[3])

def p_value_string(p):
    'value : STRING'
    p[0] = p[1]

def p_value_number(p):
    'value : NUMBER'
    p[0] = p[1]

def p_error(p):
    if p:
        print(f"Błąd składni przy '{p.value}'")
    else:
        print("Błąd składni na końcu wejścia")

parser = yacc.yacc()