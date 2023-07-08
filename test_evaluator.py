import pytest
from test_parser import get_program
from evaluator import eval, ObjectType


def get_eval(input):
    program = get_program(input)
    return eval(program) 


def check_integer_object(evaluated, expected_value):
    assert evaluated.otype == ObjectType.INTEGER
    assert evaluated.value == expected_value


def check_boolean_object(evaluated, expected_value):
    assert evaluated.otype == ObjectType.BOOLEAN
    assert evaluated.value == expected_value


def check_null_object(evaluated):
    print(evaluated, dir(evaluated), evaluated.otype)
    assert evaluated.otype == ObjectType.NULL


@pytest.mark.parametrize(
    'input,value', [
        ('10', 10),
        ('5', 5),
        ('-10', -10),
        ('-5', -5),
        ('5 + 5 + 5 + 5 * 2', 25),
        ('-5 + 5 / 5 + 5 * 2', 6),
        ('-5 + 5 / (5 + 5) * 2', -5),
    ]
)
def test_eval_integer_expression(input, value):
    evaluated = get_eval(input)
    check_integer_object(evaluated, value)


@pytest.mark.parametrize(
    'input,value', [
        ('true', True),
        ('false', False),
        ('!true', False),
        ('!false', True),
        ('!5', False),
        ('!!5', True),
        ('!!true', True),
        ('3 == 5 - 2', True),
        ('2 < 3', True),
        ('3 == 1', False),
        ('2 > 3', False),
    ]
)
def test_eval_boolean_expression(input, value):
    evaluated = get_eval(input)
    check_boolean_object(evaluated, value)


@pytest.mark.parametrize(
    'input,value', [
        ('if (true) { 10 }', 10),
        ('if (false) { 10 }', None),
        ('if (1) { 10 }', 10),
        ('if (1 < 2) { 10 }', 10),
        ('if (1 > 2) { 10 }', None),
        ('if (1 < 2) { 10 } else { 20 }', 10),
        ('if (1 > 2) { 10 } else { 20 }', 20),
    ]
)
def test_if_else_expression(input, value):
    evaluated = get_eval(input)
    if value is not None:
        check_integer_object(evaluated, value)
    else:
        check_null_object(evaluated)


@pytest.mark.parametrize(
    'input,value', [
        ('5 * 5; return 3; 9 * 9', 3),
    ]
)
def test_return_statement(input, value):
    evaluated = get_eval(input)
    check_integer_object(evaluated, value)

