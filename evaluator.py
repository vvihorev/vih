from typing import Optional
from enum import Enum, auto

from parser import (
    Program,
    ExpressionStatement,
    BlockStatement,
    LetStatement,
    ReturnStatement,
    ForStatement,
    PrefixExpression,
    InfixExpression,
    CallExpression,
    IfExpression,
    IntegerLiteral,
    StringLiteral,
    FunctionLiteral,
    Boolean,
    Identifier,
)


class Environment:
    def __init__(self, trace_eval=False):
        self.store = {}
        self.outer: Optional[Environment] = None
        self.trace_eval = trace_eval

    def get(self, identifier):
        value = self.store.get(identifier, None)
        if value is None and self.outer is not None:
            return self.outer.get(identifier)
        return value

    def set(self, identifier, value):
        self.store[identifier] = value

    def unset(self, identifier):
        if identifier in self.store:
            del self.store[identifier]

    def __str__(self):
        items = []
        for k, v in self.store.items():
            if v.otype == ObjectType.FUNCTION:
                v = v.compact_str()
            items.append(f"{k}: {v}")
        if self.outer is not None:
            outer_items = []
            for k, v in self.outer.store.items():
                if v.otype == ObjectType.FUNCTION:
                    v = v.compact_str()
                outer_items.append(f"{k}: {v}")
            return f"{{{', '.join(items)}}} outer: {{{', '.join(outer_items)}}}"
        return f"{{{', '.join(items)}}}"


class ObjectType(Enum):
    INTEGER = auto()
    BOOLEAN = auto()
    RETURN_VALUE = auto()
    FUNCTION = auto()
    STRING = auto()
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
        return f'"self.value"'


class BooleanObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.BOOLEAN)
        self.value = value

    def __str__(self) -> str:
        return str(self.value).lower()


class StringObject(Object):
    def __init__(self, value: str):
        super().__init__(ObjectType.STRING)
        self.value: str = value

    def __str__(self) -> str:
        return str(self.value).lower()


class ReturnObject(Object):
    def __init__(self, value):
        super().__init__(ObjectType.RETURN_VALUE)
        self.value = value

    def __str__(self) -> str:
        return str(self.value)


class FunctionObject(Object):
    def __init__(self, parameters, body, env):
        super().__init__(ObjectType.FUNCTION)
        self.parameters = parameters
        self.body = body
        self.env = env

    def __str__(self) -> str:
        params = ', '.join([str(p) for p in self.parameters])
        return f"func({params}) {{\n{self.body}\n}}"
    
    def compact_str(self):
        params = ', '.join([str(p) for p in self.parameters])
        return f"func({params})"


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
    if env.trace_eval:
        print("evaluating:", type(node), node.token, "env:", env)
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
    if isinstance(node, ForStatement):
        return eval_for_statement(node, env)
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
    if isinstance(node, StringLiteral):
        return StringObject(node.value)
    if isinstance(node, Boolean):
        return native_bool_to_boolean_object(node.value)
    if isinstance(node, Identifier):
        value = env.get(node.value)
        if value is None:
            return new_error("identifier not found: %s", node.value)
        return value
    if isinstance(node, FunctionLiteral):
        params = node.parameters
        body = node.body
        return FunctionObject(params, body, env)
    if isinstance(node, CallExpression):
        function = eval(node.function, env)
        if is_error(function):
            return function
        args = eval_expressions(node.arguments, env)
        if len(args) == 1 and is_error(args[0]):
            return args[0]
        return apply_function(function, args)
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


def eval_for_statement(stmt: ForStatement, env):
    initial_value = eval(stmt.initial_value, env)
    if is_error(initial_value):
        return initial_value
    env.set(stmt.counter.value, initial_value)
    condition = eval(stmt.condition, env)
    if is_error(condition):
        return condition
    while is_truthy(eval(stmt.condition, env)):
        evaluated = eval_block_statement(stmt.body, env)
        if is_error(evaluated):
            return evaluated
        eval(stmt.update_rule, env)


def eval_expressions(expressions, env):
    result = []
    for expr in expressions:
        evaluated = eval(expr, env)
        if is_error(evaluated):
            return evaluated
        result.append(evaluated)
    return result


def apply_function(function, args):
    if not isinstance(function, FunctionObject):
        return new_error("not a function: %s", get_type_name(function))
    extended_env = extend_function_env(function, args)
    evaluated = eval(function.body, extended_env)
    return unwrap_return_value(evaluated)


def extend_function_env(function, args):
    env = new_enclosed_environment(function.env)
    for i, param in enumerate(function.parameters):
        env.set(param.value, args[i])
    return env


def unwrap_return_value(obj):
    if isinstance(obj, ReturnObject):
        return obj.value
    return obj


def new_enclosed_environment(outer: Environment):
    env = Environment(outer.trace_eval)
    env.outer = outer
    return env


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
    if isinstance(left, StringObject) and isinstance(right, StringObject):
        if operator != '+':
            return new_error('unknown operator: STRING %s STRING', operator)
        return StringObject(left.value + right.value)
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
    if right.value is None:
        return new_error('integer value is null in: -%s', get_type_name(right))
    return IntegerObject(-right.value)


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

