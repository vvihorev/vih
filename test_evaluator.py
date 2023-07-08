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
    ]
)
def test_eval_boolean_expression(input, value):
    evaluated = get_eval(input)
    check_boolean_object(evaluated, value)


@pytest.mark.skip
@pytest.mark.parametrize(
    'input,value', [
        ('if (True) { 10 }', 10),
        ('if (False) { 10 }', 10),
        ('if (true) { 10 }', 10),
        ('if (true) { 10 }', 10),
        ('if (true) { 10 }', 10),
        ('if (true) { 10 }', 10),
        ('if (true) { 10 }', 10),
    ]
)
def test_if_else_expression(input, value):
    evaluated = get_eval(input)
    check_boolean_object(evaluated, value)
