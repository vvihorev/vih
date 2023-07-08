import pytest

from lexer import Lexer, TokenType
from parser import (
    Parser,
    Identifier,
    Boolean,
    IntegerLiteral,
    ReturnStatement,
    ExpressionStatement,
    PrefixExpression,
    InfixExpression,
)


def check_parser_errors(parser):
    if len(parser.errors) != 0:
        raise ValueError('\n'.join(parser.errors))


def get_program(input_string):
    parser = Parser(Lexer(input_string))
    program = parser.parse_program()
    check_parser_errors(parser)
    return program


def check_integer_literal(node: IntegerLiteral, value: int):
    assert node.token.token_type == TokenType.DIGIT
    assert node.value == value


def check_identifier(node: Identifier, value: str):
    assert node.token.literal == value
    assert node.value == value


def check_boolean(node: Boolean, value: str):
    assert node.token.literal == str(value)
    assert node.value == value


def check_literal_expression(expr, expected_value):
    if type(expr) == IntegerLiteral:
        check_integer_literal(expr, expected_value)
    elif type(expr) == Identifier:
        check_identifier(expr, expected_value)
    elif type(expr) == Boolean:
        check_boolean(expr, expected_value)
    else:
        raise ValueError(f"Unexpected expression type: {type(expr)}")
    

def check_infix_expression(expr, left, op, right):
    assert type(expr) == InfixExpression
    check_literal_expression(expr.left, left)
    check_literal_expression(expr.right, right)
    assert expr.operator == op


def test_pretty_printing():
    input_string = "let a = 3; return 45;"
    program = get_program(input_string)
    expected_output = "let a = 3; return 45;"
    assert str(program) == expected_output


def test_let_statement():
    program = get_program("""
    let x = 5;
    let y = 10;
    let foobar = 838383;
    """)
    expected_ids = ['x', 'y', 'foobar']

    assert program is not None
    assert len(program.statements) == 3
    for stmt, id in zip(program.statements, expected_ids):
        assert stmt.token.token_type == TokenType.LET
        assert stmt.token.literal == 'let'
        assert stmt.name.value == id


@pytest.mark.parametrize(
    'input,integer_value',
    [
        ('return 5;', 5),
        ('return 15;', 15),
    ]
)
def test_return_statement(input, integer_value):
    program = get_program(input)

    assert program is not None
    assert len(program.statements) == 1

    for stmt in program.statements:
        assert type(stmt) == ReturnStatement
        check_integer_literal(stmt.return_value, integer_value)


def test_identifier_expression():
    program = get_program("some_var;")

    assert program is not None
    assert len(program.statements) == 1
    expr_stmt = program.statements[0]
    assert type(expr_stmt) == ExpressionStatement
    identifier = expr_stmt.expression
    assert type(identifier) == Identifier
    assert identifier.value == 'some_var'


def test_integer_literal_expression():
    program = get_program("534;")

    assert program is not None
    assert len(program.statements) == 1
    expr_stmt = program.statements[0]
    assert type(expr_stmt) == ExpressionStatement
    integer_literal = expr_stmt.expression
    check_integer_literal(integer_literal, 534)


def test_boolean_expression():
    program = get_program("True;False;")

    assert program is not None
    stmts = program.statements
    assert len(stmts) == 2
    check_literal_expression(stmts[0].expression, True)
    check_literal_expression(stmts[1].expression, False)


@pytest.mark.parametrize(
    'input,operator,integer_value',
    [
        ('!5;', '!', 5),
        ('-15;', '-', 15),
    ]
)
def test_prefix_operators(input, operator, integer_value):
    program = get_program(input)

    assert program is not None
    assert len(program.statements) == 1
    expr_stmt = program.statements[0]
    assert type(expr_stmt) == ExpressionStatement
    prefix_expr = expr_stmt.expression
    assert type(prefix_expr) == PrefixExpression
    assert prefix_expr.operator == operator
    check_integer_literal(prefix_expr.right, integer_value)


@pytest.mark.parametrize(
    'input,operator,lvalue,rvalue',
    [
        ('5 + 4;', '+', 5, 4),
        ('15 - 3;', '-', 15, 3),
        ('6 * 4;', '*', 6, 4),
        ('15 / 3;', '/', 15, 3),
        ('5 == 5;', '==', 5, 5),
        ('5 != 5;', '!=', 5, 5),
        ('5 < 5;', '<', 5, 5),
        ('5 > 5;', '>', 5, 5),
        ('5 <= 5;', '<=', 5, 5),
        ('5 >= 5;', '>=', 5, 5),
    ]
)
def test_single_infix_operators(input, operator, lvalue, rvalue):
    program = get_program(input)

    assert program is not None
    assert len(program.statements) == 1
    expr_stmt = program.statements[0]
    assert type(expr_stmt) == ExpressionStatement
    expr = expr_stmt.expression
    assert type(expr) == InfixExpression
    assert expr.operator == operator
    check_integer_literal(expr.left, lvalue)
    check_integer_literal(expr.right, rvalue)


@pytest.mark.parametrize(
    'input,output', [
        ('2 * 3 - 4 / 2 * 4', '((2 * 3) - ((4 / 2) * 4));'),
        ('2 - 1 * 3 == 4 / 2 * 4', '((2 - (1 * 3)) == ((4 / 2) * 4));'),
    ]
)
def test_multiple_infix_operators(input,output):
    program = get_program(input)
    assert str(program) == output


@pytest.mark.parametrize(
    'input,output', [
        ('2 + 3 == 5 == True', '(((2 + 3) == 5) == True);'),
        ('!True == False', '((!True) == False);'),
    ]
)
def test_boolean_expressions(input, output):
    program = get_program(input)
    assert str(program) == output
    

