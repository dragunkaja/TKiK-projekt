import ply.yacc as yacc
from lexer import tokens
from ast_nodes import (
    ProgramNode, StatementNode, SelectQueryNode, DeleteQueryNode,
    MoveQueryNode, CopyQueryNode, LogicConditionNode, NotConditionNode,
    RelationConditionNode, LikeConditionNode, StringValueNode,
    NumberValueNode, SizeValueNode, OrderClauseNode
)

precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

def p_program(p):
    'program : statement SEMICOLON'
    p[0] = ProgramNode(p[1])

def p_statement(p):
    'statement : dryrun_opt query'
    p[0] = StatementNode(dryrun=p[1], query=p[2])

def p_dryrun_opt(p):
    '''dryrun_opt : DRYRUN
                  | empty'''
    p[0] = True if p[1] == 'DRYRUN' else False

def p_query(p):
    '''query : select_query
             | delete_query
             | move_query
             | copy_query'''
    p[0] = p[1]

def p_select_query(p):
    'select_query : SELECT column_list FROM STRING where_clause order_clause limit_clause'
    p[0] = SelectQueryNode(columns=p[2], path=p[4], where=p[5], order=p[6], limit=p[7])

def p_delete_query(p):
    'delete_query : DELETE FROM STRING where_clause limit_clause'
    p[0] = DeleteQueryNode(path=p[3], where=p[4], limit=p[5])

def p_move_query(p):
    'move_query : MOVE FROM STRING TO STRING where_clause limit_clause'
    p[0] = MoveQueryNode(source=p[3], destination=p[5], where=p[6], limit=p[7])

def p_copy_query(p):
    'copy_query : COPY FROM STRING TO STRING where_clause limit_clause'
    p[0] = CopyQueryNode(source=p[3], destination=p[5], where=p[6], limit=p[7])

def p_column_list_star(p):
    'column_list : STAR'
    p[0] = '*'

def p_column_list_id(p):
    'column_list : id_list'
    p[0] = p[1]

def p_id_list(p):
    '''id_list : ID
               | ID COMMA id_list'''
    p[0] = [p[1]] if len(p) == 2 else [p[1]] + p[3]

def p_where_clause(p):
    '''where_clause : WHERE condition
                    | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_condition_logic(p):
    '''condition : condition AND condition
                 | condition OR condition'''
    p[0] = LogicConditionNode(logic_op=p[2].upper(), left=p[1], right=p[3])

def p_condition_not(p):
    'condition : NOT condition'
    p[0] = NotConditionNode(val=p[2])

def p_condition_group(p):
    'condition : LPAREN condition RPAREN'
    p[0] = p[2]

def p_condition_rel(p):
    'condition : ID OPERATOR value'
    # TUTAJ BYŁ BŁĄD, poprawione na rel_op:
    p[0] = RelationConditionNode(rel_op=p[2], column=p[1], value=p[3])

def p_condition_like(p):
    'condition : ID LIKE STRING'
    p[0] = LikeConditionNode(column=p[1], value=p[3])

def p_value(p):
    '''value : STRING
             | NUMBER'''
    p[0] = StringValueNode(p[1]) if isinstance(p[1], str) else NumberValueNode(p[1])

def p_value_size(p):
    'value : NUMBER SIZE_UNIT'
    p[0] = SizeValueNode(value=p[1], unit=p[2])

def p_order_clause(p):
    '''order_clause : ORDER BY ID
                    | ORDER BY ID ASC
                    | ORDER BY ID DESC
                    | empty'''
    if len(p) > 2:
        direction = p[4] if len(p) == 5 else 'ASC'
        p[0] = OrderClauseNode(column=p[3], direction=direction)
    else:
        p[0] = None

def p_limit_clause(p):
    '''limit_clause : LIMIT NUMBER
                    | empty'''
    p[0] = p[2] if len(p) == 3 else None

def p_empty(p):
    'empty :'
    pass

def p_error(p):
    if p:
        print(f"Błąd składni w okolicach tokena '{p.value}' (typ: {p.type}, linia: {p.lineno})")
    else:
        print("Błąd składni: niespodziewany koniec zapytania (EOF)")

parser = yacc.yacc()