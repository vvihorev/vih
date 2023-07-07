import pytest

from lexer import Lexer, TokenType, Token
from parser import ExpressionStatement, Identifier, IntegerLiteral, Parser, PrefixExpression


def check_parser_errors(parser):
    if len(parser.errors) != 0:
        raise ValueError('\n'.join(parser.errors))


def get_program(input_string):
    parser = Parser(Lexer(input_string))
    program = parser.parse_program()
    check_parser_errors(parser)
    return program


def check_integer_literal(node: IntegerLiteral, value: int):
    assert type(node) == IntegerLiteral
    assert node.token.token_type == TokenType.DIGIT
    assert node.value == value


def test_pretty_printing():
    input_string = "let a = 3; return 45;"
    program = get_program(input_string)
    expected_output = "let a = None; return None;"
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


def test_return_statement():
    program = get_program("""
    return x;
    return 10;
    """)

    assert program is not None
    assert len(program.statements) == 2

    expected_tokens = [Token(TokenType.ID, 'x'), None]
    for stmt, token in zip(program.statements, expected_tokens):
        print(stmt)
        assert stmt.token.token_type == TokenType.RETURN
        if stmt.return_value:
            assert stmt.return_value.token == token


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

