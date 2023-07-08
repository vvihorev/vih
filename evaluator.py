from typing import Optional
from enum import Enum, auto

from parser import (
    Program,
    ExpressionStatement,
    BlockStatement,
    PrefixExpression,
    InfixExpression,
    IfExpression,
    IntegerLiteral,
    Boolean,
    ReturnStatement,
)


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    RETURN_VALUE = auto()
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


class NullObject(Object):
    def __init__(self):
        super().__init__(ObjectType.NULL)

    def __str__(self) -> str:
        return "null"


NULL = NullObject()
TRUE = BooleanObject(True)
FALSE = BooleanObject(False)


def eval(node):
    # print("evaluating:", type(node), node.token)
    if isinstance(node, Program):
        return eval_statements(node.statements)
    if isinstance(node, ExpressionStatement):
        return eval(node.expression)
    if isinstance(node, BlockStatement):
        return eval_statements(node.statements)
    if isinstance(node, ReturnStatement):
        return ReturnObject(eval(node.return_value))
    if isinstance(node, PrefixExpression):
        right = eval(node.right)
        return eval_prefix_expression(node.operator, right)
    if isinstance(node, InfixExpression):
        left = eval(node.left)
        right = eval(node.right)
        return eval_infix_expression(node.operator, left, right)
    if isinstance(node, IfExpression):
        return eval_if_expression(node)
    if isinstance(node, IntegerLiteral):
        return IntegerObject(node.value)
    if isinstance(node, Boolean):
        return native_bool_to_boolean_object(node.value)
    return None


def eval_statements(statements):
    last_stmt = None
    for stmt in statements:
        last_stmt = eval(stmt)
        if isinstance(stmt, ReturnStatement):
            return last_stmt.value
    return last_stmt


def eval_prefix_expression(operator, right):
    match operator:
        case '!':
            return eval_not_operator_expression(right)
        case '-':
            return eval_minus_prefix_operator_expression(right)
        case _:
            return NULL


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
    return NULL


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
        return NULL
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


def eval_if_expression(node):
    condition = eval(node.condition)
    if is_truthy(condition):
        return eval(node.consequence)
    elif node.alternative is not None:
        return eval(node.alternative)
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


