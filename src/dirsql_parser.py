import ply.yacc as yacc
from lexer import tokens

from ast_nodes import (
    ProgramNode,
    StatementNode,
    SelectQueryNode,
    DeleteQueryNode,
    MoveQueryNode,
    CopyQueryNode,
    LogicConditionNode,
    NotConditionNode,
    RelationConditionNode,
    LikeConditionNode,
    StringValueNode,
    NumberValueNode,
    SizeValueNode,
    OrderClauseNode,
)

# Precedencja operatorów logicznych
precedence = (
    ('left', 'OR'),
    ('left', 'AND'),
    ('right', 'NOT'),
)

#               PROGRAM

def p_program(p):
    'program : statement SEMICOLON'
    p[0] = ProgramNode(p[1])

#              STATEMENT

def p_statement(p):
    'statement : dryrun_opt query'
    p[0] = StatementNode(p[1], p[2])

def p_dryrun_opt_true(p):
    'dryrun_opt : DRYRUN'
    p[0] = True

def p_dryrun_opt_empty(p):
    'dryrun_opt : empty'
    p[0] = False

#                QUERY

def p_query_select(p):
    'query : select_query'
    p[0] = p[1]

def p_query_delete(p):
    'query : delete_query'
    p[0] = p[1]

def p_query_move(p):
    'query : move_query'
    p[0] = p[1]

def p_query_copy(p):
    'query : copy_query'
    p[0] = p[1]

#             SELECT QUERY

def p_select_query(p):
    'select_query : SELECT column_list FROM STRING where_clause order_clause limit_clause'
    p[0] = SelectQueryNode(
        columns=p[2],
        path=p[4],
        where=p[5],
        order=p[6],
        limit=p[7],
    )

#             DELETE QUERY

def p_delete_query(p):
    'delete_query : DELETE FROM STRING where_clause limit_clause'
    p[0] = DeleteQueryNode(
        path=p[3],
        where=p[4],
        limit=p[5],
    )

#              MOVE QUERY

def p_move_query(p):
    'move_query : MOVE FROM STRING TO STRING where_clause limit_clause'
    p[0] = MoveQueryNode(
        source=p[3],
        destination=p[5],
        where=p[6],
        limit=p[7],
    )

#              COPY QUERY

def p_copy_query(p):
    'copy_query : COPY FROM STRING TO STRING where_clause limit_clause'
    p[0] = CopyQueryNode(
        source=p[3],
        destination=p[5],
        where=p[6],
        limit=p[7],
    )

#            COLUMNS / SELECT

def p_column_list_star(p):
    'column_list : STAR'
    p[0] = '*'

def p_column_list_id_list(p):
    'column_list : id_list'
    p[0] = p[1]

def p_id_list_single(p):
    'id_list : ID'
    p[0] = [p[1]]

def p_id_list_multiple(p):
    'id_list : ID COMMA id_list'
    p[0] = [p[1]] + p[3]

#              WHERE CLAUSE

def p_where_clause_condition(p):
    'where_clause : WHERE condition'
    p[0] = p[2]

def p_where_clause_empty(p):
    'where_clause : empty'
    p[0] = None

#               CONDITIONS

def p_condition_and(p):
    'condition : condition AND condition'
    p[0] = LogicConditionNode('AND', p[1], p[3])

def p_condition_or(p):
    'condition : condition OR condition'
    p[0] = LogicConditionNode('OR', p[1], p[3])

def p_condition_not(p):
    'condition : NOT condition'
    p[0] = NotConditionNode(p[2])

def p_condition_group(p):
    'condition : LPAREN condition RPAREN'
    p[0] = p[2]

def p_condition_rel(p):
    'condition : ID OPERATOR value'
    p[0] = RelationConditionNode(
        column=p[1],
        operator=p[2],
        value=p[3],
    )

def p_condition_like(p):
    'condition : ID LIKE STRING'
    p[0] = LikeConditionNode(
        column=p[1],
        value=p[3],
    )

#                VALUES

def p_value_string(p):
    'value : STRING'
    p[0] = StringValueNode(p[1])

def p_value_number(p):
    'value : NUMBER'
    p[0] = NumberValueNode(p[1])

def p_value_size(p):
    'value : NUMBER SIZE_UNIT'
    p[0] = SizeValueNode(p[1], p[2])

#          ORDER / LIMIT CLAUSE

def p_order_clause_empty(p):
    'order_clause : empty'
    p[0] = None

def p_order_clause_default(p):
    'order_clause : ORDER BY ID'
    p[0] = OrderClauseNode(column=p[3], direction='ASC')

def p_order_clause_asc(p):
    'order_clause : ORDER BY ID ASC'
    p[0] = OrderClauseNode(column=p[3], direction='ASC')

def p_order_clause_desc(p):
    'order_clause : ORDER BY ID DESC'
    p[0] = OrderClauseNode(column=p[3], direction='DESC')

def p_limit_clause_empty(p):
    'limit_clause : empty'
    p[0] = None

def p_limit_clause_value(p):
    'limit_clause : LIMIT NUMBER'
    p[0] = p[2]

#                EMPTY

def p_empty(p):
    'empty :'
    pass

#                ERRORS

def p_error(p):
    if p:
        print(f"Błąd składni w okolicach tokena '{p.value}' (typ: {p.type}, linia: {p.lineno})")
    else:
        print("Błąd składni: niespodziewany koniec zapytania (EOF)")

# Inicjalizacja parsera
parser = yacc.yacc()