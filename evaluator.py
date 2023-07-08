from typing import Optional
from enum import Enum, auto

from parser import (
    Program,
    ExpressionStatement,
    BlockStatement,
    LetStatement,
    PrefixExpression,
    InfixExpression,
    IfExpression,
    IntegerLiteral,
    Boolean,
    ReturnStatement,
    Identifier,
)


class Environment:
    def __init__(self):
        self.store = {}

    def get(self, identifier):
        return self.store.get(identifier, None)

    def set(self, identifier, value):
        self.store[identifier] = value


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    RETURN_VALUE = auto()
    ERROR = auto()
    NULL = auto()


class Object:
    def __init__(self, type):
        self.otype: ObjectType = type
        self.value: Optional[int|bool]


class IntegerObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.INTEGER)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class BooleanObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.BOOLEAN)
        self.value = value

    def __str__(self) -> str:
        return str(self.value).lower()


class ReturnObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.RETURN_VALUE)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class ErrorObject(Object):
    def __init__(self, msg):
        super().__init__(ObjectType.ERROR)
        self.msg = msg

    def __str__(self) -> str:
        return f"ERROR: {self.msg}"

class NullObject(Object):
    def __init__(self):
        super().__init__(ObjectType.NULL)

    def __str__(self) -> str:
        return "null"


NULL = NullObject()
TRUE = BooleanObject(True)
FALSE = BooleanObject(False)


def eval(node, env: Environment):
    # print("evaluating:", type(node), node.token, "env:", env.store)
    if isinstance(node, Program):
        return eval_program(node, env)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression, env)
    if isinstance(node, BlockStatement):
        return eval_block_statement(node, env)
    if isinstance(node, ReturnStatement):
        value = eval(node.return_value, env)
        if is_error(value):
            return value
        return ReturnObject(value)
    if isinstance(node, LetStatement):
        value = eval(node.value, env)
        if is_error(value):
            return value
        env.set(node.name.value, value)
    if isinstance(node, PrefixExpression):
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left, env)
        if is_error(left):
            return left
        right = eval(node.right, env)
        if is_error(right):
            return right
        return eval_infix_expression(node.operator, left, right)
    if isinstance(node, IfExpression):
        return eval_if_expression(node, env)
    if isinstance(node, IntegerLiteral):
        return IntegerObject(node.value)
    if isinstance(node, Boolean):
        return native_bool_to_boolean_object(node.value)
    if isinstance(node, Identifier):
        value = env.get(node.value)
        if value is None:
            return new_error("identifier not found: %s", node.value)
        return value
    return None


def eval_program(program, env):
    result = None
    for stmt in program.statements:
        result = eval(stmt, env)
        if isinstance(result, ReturnObject):
            return result.value
        if isinstance(result, ErrorObject):
            return result
    return result


def eval_block_statement(block, env):
    result = None
    for stmt in block.statements:
        result = eval(stmt, env)
        if result is not None:
            if isinstance(result, ReturnObject) or isinstance(result, ErrorObject):
                return result
    return result


def eval_prefix_expression(operator, right):
    match operator:
        case '!':
            return eval_not_operator_expression(right)
        case '-':
            return eval_minus_prefix_operator_expression(right)
        case _:
            return new_error('unknown operator: %s%s', operator, get_type_name(right))


def eval_infix_expression(operator, left, right):
    if isinstance(left, IntegerObject) and isinstance(right, IntegerObject):
        return eval_integer_infix_expression(operator, left, right)
    match operator:
        case '<':
            return native_bool_to_boolean_object(left.value < right.value)
        case '>':
            return native_bool_to_boolean_object(left.value > right.value)
        case '<=':
            return native_bool_to_boolean_object(left.value <= right.value)
        case '>=':
            return native_bool_to_boolean_object(int(left.value >= right.value))
        case '==':
            return native_bool_to_boolean_object(left.value == right.value)
        case '!=':
            return native_bool_to_boolean_object(int(left.value != right.value))
    if type(left) != type(right):
        return new_error('type mismatch: %s %s %s', get_type_name(left), operator, get_type_name(right))
    return new_error('unknown operator: %s %s %s', get_type_name(left), operator, get_type_name(right))


def native_bool_to_boolean_object(value):
    if value:
        return TRUE
    return FALSE


def eval_not_operator_expression(right):
    if right == TRUE:
        return FALSE
    elif right == FALSE:
        return TRUE
    elif right == NULL:
        return TRUE
    else:
        return FALSE


def eval_minus_prefix_operator_expression(right):
    if not isinstance(right, IntegerObject):
        return new_error('unknown operator: -%s', get_type_name(right))
    return IntegerObject(-right.value)


def eval_integer_infix_expression(operator, left, right):
    match operator:
        case '+':
            return IntegerObject(left.value + right.value)
        case '-':
            return IntegerObject(left.value - right.value)
        case '*':
            return IntegerObject(left.value * right.value)
        case '/':
            return IntegerObject(int(left.value / right.value))
        case '<':
            return native_bool_to_boolean_object(left.value < right.value)
        case '>':
            return native_bool_to_boolean_object(left.value > right.value)
        case '<=':
            return native_bool_to_boolean_object(left.value <= right.value)
        case '>=':
            return native_bool_to_boolean_object(int(left.value >= right.value))
        case '==':
            return native_bool_to_boolean_object(left.value == right.value)
        case '!=':
            return native_bool_to_boolean_object(int(left.value != right.value))
    return new_error('unknown operator: %s %s %s', get_type_name(left), operator, get_type_name(right))


def eval_if_expression(node, env):
    condition = eval(node.condition, env)
    if is_error(condition):
        return condition
    if is_truthy(condition):
        return eval(node.consequence, env)
    elif node.alternative is not None:
        return eval(node.alternative, env)
    else:
        return NULL


def is_truthy(node):
    if node == NULL:
        return False
    if node == TRUE:
        return True
    if node == FALSE:
        return False
    return True


def new_error(format_string, *params):
    return ErrorObject(format_string % params)


def is_error(obj):
    if obj is not None:
        return isinstance(obj, ErrorObject)
    return False


def get_type_name(expr):
    try:
        return expr.otype.name
    except AttributeError:
        return None

