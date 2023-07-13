import pytest
from test_parser import get_program
from evaluator import eval, ObjectType, Environment


def get_eval(input):
    env = Environment()
    program = get_program(input)
    return eval(program, env) 


def check_integer_object(evaluated, expected_value):
    assert evaluated.otype == ObjectType.INTEGER
    assert evaluated.value == expected_value


def check_boolean_object(evaluated, expected_value):
    assert evaluated.otype == ObjectType.BOOLEAN
    assert evaluated.value == expected_value


def check_string_object(evaluated, expected_value):
    assert evaluated.otype == ObjectType.STRING
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
        ('""', ""),
        ('"Hello!"', "Hello!"),
    ]
)
def test_eval_string_expression(input, value):
    evaluated = get_eval(input)
    check_string_object(evaluated, value)


@pytest.mark.parametrize(
    'input,value', [
        ('"Hello" + " " + "world!', "Hello world!"),
    ]
)
def test_eval_string_concatenation(input, value):
    evaluated = get_eval(input)
    check_string_object(evaluated, value)


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


def test_nested_block_statements():
    input = """
    if (10 > 1) {
            if (10 > 1) {
                    return 10
            }
            return 1;
    }
    """
    expected_value = 10
    evaluated = get_eval(input)
    check_integer_object(evaluated, expected_value)


@pytest.mark.parametrize(
    'input,expected_message', [
        ('5 + true;', 'type mismatch: INTEGER + BOOLEAN'),
        ('5 + true; 5;', 'type mismatch: INTEGER + BOOLEAN'),
        ('-true;', 'unknown operator: -BOOLEAN'),
        ('false + true; 5;', 'unknown operator: BOOLEAN + BOOLEAN'),
        ('"hello" - "world"; 5;', 'unknown operator: STRING - STRING'),
        ('a;', 'identifier not found: a'),
        ('for (i=0;i<5;let i=i+1) {a;}', 'identifier not found: a'),
        ('for (i=0;a;let i=i+1) {a;}', 'identifier not found: a'),
        ('let a = [1, 2, 3]; a[3]', 'Index 3 out of bounds for collection of len 3'),
        ('let a = 2; a[3]', 'Exprected collection for indexing, got ObjectType.INTEGER'),
        ('len(0)', 'Builtin function len expected type String or List'),
        ('len("asd", "asd")', 'Builtin function len expected one argument'),
        ('len()', 'Builtin function len expected one argument'),
    ]
)
def test_error_handling(input, expected_message):
    evaluated = get_eval(input)
    assert evaluated.otype == ObjectType.ERROR
    assert evaluated.msg == expected_message


@pytest.mark.parametrize(
    'input,expected_value', [
        ('let a = 5; a;', 5),
        ('let a = 5 * 5; a;', 25),
        ('let a = 5; let b = a; b;', 5),
        ('let a = 5; let b = a; let c = a + b + 5; c;', 15),
    ]
)
def test_let_statement(input, expected_value):
    check_integer_object(get_eval(input), expected_value)


@pytest.mark.parametrize(
    'input,expected_value', [
        ('''
            let prod = 1;
            for (i = 1; i <= 5; let i = i + 1) {
                let prod = prod * i;
            }
            prod;
         ''', 120),
    ]
)
def test_for_statement(input, expected_value):
    check_integer_object(get_eval(input), expected_value)


def test_function_object():
    input = "func(x) { x + 2; };"
    evaluated = get_eval(input)
    assert evaluated.otype == ObjectType.FUNCTION
    assert len(evaluated.parameters) == 1
    assert str(evaluated.body) == '(x + 2);'


@pytest.mark.parametrize(
    'input,expected_value', [
        ('let identity = func(x) { x; }; identity(5);', 5),
        ('let identity = func(x) { return x; }; identity(5);', 5),
        ('let double = func(x) { return x + x; }; double(5);', 10),
        ('let add = func(x, y) { return x + y; }; add(5, 7);', 12),
        ('let add = func(x, y) { return x + y; }; add(5 + 5, add(5, 5));', 20),
        ('func(x){x;}(5)', 5),
    ]
)
def test_function_application(input, expected_value):
    evaluated = get_eval(input)
    check_integer_object(evaluated, expected_value)


@pytest.mark.parametrize(
    'input,expected_value', [
        ('let A = [1, 2, 3]; A[1]', 2),
    ]
)
def test_list_operations(input, expected_value):
    evaluated = get_eval(input)
    check_integer_object(evaluated, expected_value)


@pytest.mark.parametrize(
    'input,expected_value', [
        ('len("")', 0),
        ('len("hello")', 5),
        ('len("hello world")', 11),
    ]
)
def test_builtin_functions(input, expected_value):
    evaluated = get_eval(input)
    check_integer_object(evaluated, expected_value)

