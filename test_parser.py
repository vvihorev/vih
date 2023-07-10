import pytest

from lexer import Lexer, TokenType
from parser import (
    Parser,
    Identifier,
    IntegerLiteral,
    FunctionLiteral,
    Boolean,
    ReturnStatement,
    BlockStatement,
    ForStatement,
    ExpressionStatement,
    PrefixExpression,
    InfixExpression,
    IfExpression,
    CallExpression,
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
    assert node.token.literal == str(value).lower()
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


def test_for_statement():
    program = get_program("""
    let prod = 1;
    for (i = 1; i <= 5; let i = i + 1) {
        let prod = prod * i;
    }
    prod;
    """)
    assert program is not None
    assert len(program.statements) == 3
    for_stmt = program.statements[1]
    assert type(for_stmt) == ForStatement
    assert for_stmt.counter.value == 'i'
    check_integer_literal(for_stmt.initial_value, 1)
    assert str(for_stmt.condition) == '(i <= 5)'
    assert str(for_stmt.update_rule) == 'let i = (i + 1);'


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
    program = get_program("true;false;")

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
    

@pytest.mark.parametrize(
    'input,output', [
        ('1 + (2 + 3) + 4', '((1 + (2 + 3)) + 4);'),
        ('!(True == True)', '(!(True == True));'),
    ]
)
def test_operator_precedence_parsing(input, output):
    program = get_program(input)
    assert str(program) == output


def test_if_expression():
    program = get_program("if (x < y) { x };")
    stmts = program.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    if_expr = expr_stmt.expression
    assert type(if_expr) == IfExpression
    condition = if_expr.condition
    consequence = if_expr.consequence
    assert type(condition) == InfixExpression
    assert type(consequence) == BlockStatement
    check_infix_expression(condition, 'x', '<', 'y')

    stmts = consequence.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    assert expr_stmt.expression.value == 'x'


def test_if_else_expression():
    program = get_program("if (x < y) { x } else { y };")
    stmts = program.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    if_else_expr = expr_stmt.expression
    assert type(if_else_expr) == IfExpression
    condition = if_else_expr.condition
    consequence = if_else_expr.consequence
    alternative = if_else_expr.alternative
    assert type(condition) == InfixExpression
    assert type(consequence) == BlockStatement
    assert type(alternative) == BlockStatement
    check_infix_expression(condition, 'x', '<', 'y')

    stmts = consequence.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    assert expr_stmt.expression.value == 'x'

    stmts = alternative.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    assert expr_stmt.expression.value == 'y'


@pytest.mark.parametrize(
    'input,output', [
        ('if (x > y) {let x = 2; x < y;};', 'if ((x > y)) {let x = 2; (x < y);};'),
    ]
)
def test_block_statement(input, output):
    program = get_program(input)
    assert str(program) == output


def test_function_literal():
    program = get_program("func(x, y) { return x + y; }")
    stmts = program.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    func_literal = expr_stmt.expression
    assert type(func_literal) == FunctionLiteral
    parameters = func_literal.parameters
    body = func_literal.body
    assert type(body) == BlockStatement

    assert parameters[0].value == 'x'
    assert parameters[1].value == 'y'

    body_stmt = body.statements[0]
    assert type(body_stmt) == ReturnStatement


def test_function_call_expression():
    program = get_program("func(x, y) { return x + y; } (1, 2)")
    stmts = program.statements
    assert len(stmts) == 1
    expr_stmt = stmts[0]
    assert type(expr_stmt) == ExpressionStatement
    call_expr = expr_stmt.expression
    assert type(call_expr) == CallExpression
    function = call_expr.function
    arguments = call_expr.arguments

    assert type(function) == FunctionLiteral
    arg0 = arguments[0]
    arg1 = arguments[1]
    assert type(arg0) == IntegerLiteral
    assert type(arg1) == IntegerLiteral
    assert arg0.value == 1
    assert arg1.value == 2


def test_function_call_printing():
    program = get_program('add(1, 2);')
    assert str(program) == 'add(1, 2);'

