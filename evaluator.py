from typing import Optional
from enum import Enum, auto

from parser import (
    Program,
    ExpressionStatement,
    PrefixExpression,
    IntegerLiteral,
    Boolean,
)


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
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
        return str(self.value)


class NullObject(Object):
    def __init__(self):
        super().__init__(ObjectType.BOOLEAN)

    def __str__(self) -> str:
        return "null"


NULL = NullObject()
TRUE = BooleanObject(True)
FALSE = BooleanObject(False)


def eval(node):
    print("evaluating:", type(node), node.token)
    if isinstance(node, Program):
        return eval_statements(node.statements)
    elif isinstance(node, ExpressionStatement):
        return eval(node.expression)
    elif isinstance(node, PrefixExpression):
        right = eval(node.right)
        return eval_prefix_expression(node.operator, right)
    elif isinstance(node, IntegerLiteral):
        return IntegerObject(node.value)
    elif isinstance(node, Boolean):
        return native_bool_to_boolean_object(node.value)
    return None


def eval_statements(statements):
    last_stmt = NullObject()
    for stmt in statements:
        last_stmt = eval(stmt)
    return last_stmt


def eval_prefix_expression(operator, right):
    match operator:
        case '!':
            return eval_not_operator_expression(right)
        case '-':
            return eval_minus_prefix_operator_expression(right)
        case _:
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
